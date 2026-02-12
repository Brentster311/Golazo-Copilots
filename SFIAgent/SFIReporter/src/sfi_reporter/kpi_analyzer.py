"""KPI analysis via LLM — gathers data, fetches docs, builds prompt.

This module provides the logic for the "Analyze with LLM" right-click
feature.  It collects all action items for a KPI, fetches content from
their documentation URLs, and constructs a structured analysis prompt
that asks the four key questions:

  1. What is being asked?
  2. Why?
  3. On what resources should I act?
  4. How? (step by step)

The prompt is then sent to the Copilot Chat panel for streaming.
"""

from __future__ import annotations

import logging
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sfi_reporter.app import SFIReporterApp

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_MAX_CONTENT_PER_URL = 4_000
_MAX_ITEMS_IN_PROMPT = 30
_URL_FETCH_TIMEOUT = 10  # seconds
_MAX_URLS = 10
_URL_FIELDS = (
    "url",
    "ActionWikiLink",
    "Remediation",
    "AssetTypeLink0",
    "AssetTypeLink1",
    "AssetTypeLink2",
    "CustomGroupingLink",
)
_USER_AGENT = "SFIReporter/1.0 (KPI Analysis)"


# ---------------------------------------------------------------------------
# HTML → text
# ---------------------------------------------------------------------------

class _HTMLTextExtractor(HTMLParser):
    """Simple HTML-to-text converter that strips tags, scripts, and styles."""

    def __init__(self):
        super().__init__()
        self._text: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False
        if tag in ("p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"):
            self._text.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._text.append(data)

    def get_text(self) -> str:
        return "".join(self._text).strip()


def extract_text(html: str) -> str:
    """Extract readable text from an HTML string.

    Strips script/style blocks and HTML tags.  Falls back to raw text
    on parse errors.
    """
    try:
        parser = _HTMLTextExtractor()
        parser.feed(html)
        return parser.get_text()
    except Exception:
        # If parsing fails, strip tags with regex as fallback
        text = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Truncation
# ---------------------------------------------------------------------------

def truncate_content(text: str, max_len: int = _MAX_CONTENT_PER_URL) -> str:
    """Truncate text to *max_len* characters, appending a truncation marker."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "\n... (truncated)"


# ---------------------------------------------------------------------------
# URL collection
# ---------------------------------------------------------------------------

def collect_urls(items: list[dict]) -> set[str]:
    """Collect unique HTTP/HTTPS URLs from all URL fields across items."""
    urls: set[str] = set()
    for item in items:
        for field in _URL_FIELDS:
            val = item.get(field)
            if val and isinstance(val, str) and val.strip():
                url = val.strip()
                # Security: only allow http/https schemes
                if url.lower().startswith(("http://", "https://")):
                    urls.add(url)
    return urls


# ---------------------------------------------------------------------------
# URL fetching
# ---------------------------------------------------------------------------

def fetch_url_content(
    url: str,
    timeout: int = _URL_FETCH_TIMEOUT,
) -> dict:
    """Fetch a URL and extract text content.

    Returns ``{"url": ..., "content": ..., "error": ...}``.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Only process text content types
            ctype = resp.headers.get("Content-Type", "")
            if "text" not in ctype and "html" not in ctype and "json" not in ctype:
                return {"url": url, "content": "", "error": f"Non-text content type: {ctype}"}
            raw = resp.read(200_000)  # cap read at 200KB
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            text = extract_text(html)
            text = truncate_content(text)
            return {"url": url, "content": text, "error": ""}
    except urllib.error.HTTPError as exc:
        return {"url": url, "content": "", "error": f"HTTP {exc.code}"}
    except Exception as exc:
        return {"url": url, "content": "", "error": str(exc)}


def fetch_all_urls(
    urls: set[str],
    timeout: int = _URL_FETCH_TIMEOUT,
    max_urls: int = _MAX_URLS,
) -> dict[str, str]:
    """Fetch multiple URLs in parallel, return {url: content} mapping.

    URLs that fail are included with empty content.
    """
    if not urls:
        return {}

    # Cap the number of URLs to fetch
    url_list = sorted(urls)[:max_urls]

    results: dict[str, str] = {}
    successes = 0
    failures = 0

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fetch_url_content, u, timeout): u for u in url_list}
        for future in as_completed(futures):
            result = future.result()
            url = result["url"]
            if result["content"]:
                results[url] = result["content"]
                successes += 1
            else:
                results[url] = f"(Could not fetch: {result['error']})"
                failures += 1

    logger.info(
        "URL fetch complete: %d success, %d failed out of %d",
        successes, failures, len(url_list),
    )
    return results


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def _summarise_item_for_prompt(item: dict) -> str:
    """Format a single item as a compact text block for the prompt."""
    parts = [
        f"- **{item.get('id', '?')}**: {item.get('title', '?')}",
        f"  Service: {item.get('S360_ServiceTreeServiceName', '?')}",
        f"  Owner: {item.get('ActionOwnerName', '?')}",
        f"  SLA: {item.get('SlaType', '?')} | ETA: {item.get('EtaDate', 'none')} | Due: {item.get('dueDate', '?')}",
        f"  Status: {item.get('ActionItemStatus', '?')}",
    ]
    # Include asset types if present
    for i in range(3):
        asset = item.get(f"AssetType{i}")
        if asset:
            parts.append(f"  Asset{i}: {asset}")
    return "\n".join(parts)


def build_analysis_prompt(
    items: list[dict],
    fetched_docs: dict[str, str],
) -> str:
    """Build a structured analysis prompt for the LLM.

    Args:
        items: All action items for the KPI.
        fetched_docs: Mapping of URL → extracted text content.

    Returns:
        The full prompt string ready to send to the Copilot session.
    """
    if not items:
        return "No items found for this KPI."

    # KPI identity
    kpi_id = items[0].get("_kpi_id", "Unknown")
    kpi_name = items[0].get("_kpi_name", kpi_id)
    total = len(items)
    out_of_sla = sum(1 for i in items if i.get("SlaType") == "OutOfSla")

    # Item summaries (capped)
    display_items = items[:_MAX_ITEMS_IN_PROMPT]
    item_lines = "\n".join(_summarise_item_for_prompt(i) for i in display_items)
    truncation_note = ""
    if total > _MAX_ITEMS_IN_PROMPT:
        truncation_note = f"\n*(Showing {_MAX_ITEMS_IN_PROMPT} of {total} items)*\n"

    # Documentation section
    doc_lines = ""
    if fetched_docs:
        doc_parts = []
        for url, content in fetched_docs.items():
            doc_parts.append(f"### {url}\n{content}\n")
        doc_lines = "\n".join(doc_parts)
    else:
        doc_lines = "(No documentation URLs available or all fetches failed.)"

    prompt = f"""Analyze the following SFI/QEI KPI and its action items in detail.

## KPI: {kpi_name} ({kpi_id})
Total items: {total} | Out of SLA: {out_of_sla}

## Action Items
{item_lines}
{truncation_note}
## Documentation
{doc_lines}

## Questions to Answer

Please provide a thorough analysis addressing each of these:

1. **What is being asked?** — Explain what this KPI requires in plain language. What specific compliance or security standard does it enforce?

2. **Why?** — Why does this requirement exist? What risk or threat does it mitigate? What happens if it's not addressed?

3. **On what resources should I act?** — Based on the action items above, list the specific Azure resources, services, subscriptions, or assets that need attention. Group by service if helpful.

4. **How? (Step by step)** — Provide concrete, actionable remediation steps. Reference the documentation above where applicable. Include Azure CLI commands, portal steps, or policy configurations as appropriate.
"""
    return prompt.strip()


# ---------------------------------------------------------------------------
# Main analysis entry point
# ---------------------------------------------------------------------------

def analyze_kpi(app: "SFIReporterApp", kpi_id: str) -> str:
    """Gather items for a KPI, fetch docs, and build the analysis prompt.

    This function does I/O (URL fetching) and should be called from a
    background thread.

    Args:
        app: The running SFIReporterApp instance.
        kpi_id: The KPI identifier to analyze.

    Returns:
        The fully constructed prompt string.
    """
    # 1. Gather all items for this KPI
    all_items = (app.current_data or {}).get("detailed_items", [])
    kpi_items = [i for i in all_items if i.get("_kpi_id") == kpi_id]

    if not kpi_items:
        return f"No action items found for KPI '{kpi_id}'."

    logger.info(
        "Analyzing KPI %s: %d items",
        kpi_id, len(kpi_items),
    )

    # 2. Collect unique URLs
    urls = collect_urls(kpi_items)
    logger.info("Collected %d unique URLs for KPI %s", len(urls), kpi_id)

    # 3. Fetch URL content
    fetched_docs = fetch_all_urls(urls)

    # 4. Build prompt
    prompt = build_analysis_prompt(kpi_items, fetched_docs)

    logger.info(
        "Analysis prompt built for KPI %s: %d chars, %d items, %d URLs fetched",
        kpi_id, len(prompt), len(kpi_items), len(fetched_docs),
    )

    return prompt
