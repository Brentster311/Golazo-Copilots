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

import hashlib
import logging
import os
import re
import tempfile
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sfi_reporter.app import SFIReporterApp

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes (SFI-035: structured provenance)
# ---------------------------------------------------------------------------

@dataclass
class FetchResult:
    """Result of fetching a single URL for provenance tracking."""
    url: str
    ok: bool
    chars: int
    error: str
    method: str = "urllib"
    discovered_urls: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Structured result from analyze_kpi with provenance metadata."""
    prompt: str
    urls_found: list[str] = field(default_factory=list)
    fetch_results: list[FetchResult] = field(default_factory=list)
    docs_dir: str = ""  # path where fetched docs are saved on disk

    def __str__(self) -> str:
        """Return the prompt string for backward compatibility."""
        return self.prompt


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

# URL patterns to exclude from discovered links (noise)
_DISCOVERED_URL_EXCLUDE = re.compile(
    r"login\.microsoftonline\.com"
    r"|oauth2?\.?"
    r"|/authorize\?"
    r"|privacystatement"
    r"|servicesagreement"
    r"|/consent\?"
    r"|accounts\.google\.com"
    r"|login\.live\.com",
    re.IGNORECASE,
)

# Domains that indicate an auth redirect (skip CDP, report auth_wall fast)
_AUTH_REDIRECT_DOMAINS = re.compile(
    r"login\.microsoftonline\.com"
    r"|login\.live\.com"
    r"|login\.windows\.net"
    r"|accounts\.google\.com"
    r"|auth\.docker\.io"
    r"|auth0\.com",
    re.IGNORECASE,
)

# Regex for finding URLs in fetched text content
_TEXT_URL_RE = re.compile(r"https?://[^\s)>\]\"']+")

# Patterns that indicate a login / auth wall page (case-insensitive)
_LOGIN_PAGE_INDICATORS = [
    r"sign\s*in\s+(to\s+your\s+account|options)",
    r"can't\s+access\s+your\s+account",
    r"enter\s+your\s+(email|password|credentials)",
    r"microsoft\s+sign\s+in",
    r"<form[^>]*login",
    r"oauth2",
    r"authorize\?",
]
_LOGIN_PAGE_RE = re.compile("|".join(_LOGIN_PAGE_INDICATORS), re.IGNORECASE)

_AUTH_BLOCKED_MSG = (
    "(Authentication wall \u2014 this URL requires interactive login. "
    "Content is not available for analysis.)"
)

_AUTH_HINT_MSG = (
    "\U0001f512 Some URLs required authentication.  To allow fetching:\n"
    "  1. Open Microsoft Edge with your \u2018Work\u2019 profile\n"
    "  2. Sign in to the target site (e.g. lens.msftcloudes.com)\n"
    "  3. Re-run the analysis \u2014 SFI Reporter will reuse Edge\u2019s cookies via CDP."
)

# Patterns that indicate a JS SPA shell (no real rendered content)
_JS_SHELL_INDICATORS = [
    r"enable\s+javascript",
    r"javascript\s+(is\s+)?required",
    r"this\s+app\s+(works|requires)\s+(best\s+)?with\s+javascript",
    r"you need to enable javascript",
    r"noscript",
    r"loading[\u2026.]{1,3}$",  # page is just "Loading..." or "Loading\u2026"
]
_JS_SHELL_RE = re.compile("|".join(_JS_SHELL_INDICATORS), re.IGNORECASE)

# Minimum character count below which fetched text is considered too thin
# to be useful content (likely a JS SPA shell that wasn't rendered).
_MIN_USEFUL_CHARS = 400


def _is_js_shell(text: str) -> bool:
    """Detect whether extracted text is a JS SPA shell with no real content.

    Heuristics:
    - Text is very short (< *_MIN_USEFUL_CHARS*), **and**
    - Either matches JS-shell indicators **or** has very low word count.

    CDP-rendered pages return the full rendered DOM, so this mainly catches
    urllib/bearer fetches that got the HTML skeleton of a client-side app.
    """
    if not text:
        return False
    stripped = text.strip()
    length = len(stripped)
    if length >= _MIN_USEFUL_CHARS:
        return False  # enough content to be useful
    # Very short text — does it look like a shell?
    if _JS_SHELL_RE.search(stripped):
        return True
    # Ultra-thin: fewer than 50 words is almost certainly not real content
    words = stripped.split()
    if len(words) < 50:
        return True
    return False


# Generic Azure scope for bearer-token fetches (works for most MS-internal sites)
_AZURE_DEFAULT_SCOPE = "https://management.azure.com/.default"


def _is_login_page(text: str) -> bool:
    """Detect whether extracted text looks like a login / auth wall.

    Heuristics:
    - Must match login-page indicators, AND
    - Must have very low information density (short useful text relative
      to total length, or very few unique words).
    """
    if not text:
        return False
    # Quick check: does it contain login indicators?
    if not _LOGIN_PAGE_RE.search(text):
        return False
    # Strip whitespace and check content quality
    stripped = text.strip()
    non_ws = re.sub(r"\s+", " ", stripped)
    words = non_ws.split()
    unique_words = set(w.lower() for w in words)
    # Login pages have very few unique words relative to length
    if len(unique_words) < 30 and len(words) < 80:
        return True
    # Also flag if "sign in" appears many times relative to content
    sign_in_count = len(re.findall(r"sign\s*in", stripped, re.IGNORECASE))
    if sign_in_count >= 2 and len(unique_words) < 60:
        return True
    return False

# URL patterns considered potentially relevant to SFI/security remediation
_RELEVANT_URL_PATTERNS = re.compile(
    r"aka\.ms"
    r"|learn\.microsoft\.com"
    r"|docs\.microsoft\.com"
    r"|dev\.azure\.com"
    r"|github\.com"
    r"|wiki\."
    r"|confluence\."
    r"|remediat"
    r"|security"
    r"|compliance"
    r"|azure",
    re.IGNORECASE,
)


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
        text = parser.get_text()
    except Exception:
        # If parsing fails, strip tags with regex as fallback
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
    return _sanitize_text(text)


# ---------------------------------------------------------------------------
# Truncation & sanitization
# ---------------------------------------------------------------------------

def _sanitize_text(text: str) -> str:
    """Remove control characters and excessive whitespace that can break API payloads."""
    # Strip control chars except newline/tab
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Collapse runs of 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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

def _fetch_via_cdp(url: str, timeout: int = _URL_FETCH_TIMEOUT) -> dict:
    """Fetch a URL via headless Chromium (Playwright CDP) for SPA rendering.

    Waits for ``networkidle`` so JavaScript-rendered content (dashboards,
    SPAs) is fully available before extracting text.

    Returns ``{"url": ..., "content": ..., "error": ..., "method": "cdp"}``.
    """
    try:
        from playwright.sync_api import sync_playwright  # noqa: F811
    except ImportError:
        return {"url": url, "content": "", "error": "playwright not installed",
                "method": "cdp"}

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(timeout * 1000)
            page.goto(url, wait_until="networkidle")

            # Early auth-redirect detection: check if we landed on a login domain
            final_url = page.url
            if _AUTH_REDIRECT_DOMAINS.search(final_url):
                logger.info("CDP detected auth redirect to %s for %s", final_url, url)
                browser.close()
                return {"url": url, "content": "",
                        "error": "auth_redirect", "method": "cdp"}

            # Extract all discovered links before we grab text
            discovered = page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => e.href).filter(h => h.startsWith('http'))",
            )
            # Filter out login/OAuth/privacy noise
            discovered = [
                u for u in discovered
                if not _DISCOVERED_URL_EXCLUDE.search(u)
            ]
            html = page.content()
            browser.close()

        text = extract_text(html)
        text = truncate_content(text)
        result: dict = {
            "url": url,
            "content": text,
            "error": "",
            "method": "cdp",
        }
        if discovered:
            result["discovered_urls"] = discovered
        return result
    except Exception as exc:
        return {"url": url, "content": "", "error": str(exc), "method": "cdp"}


def _fetch_via_urllib(url: str, timeout: int = _URL_FETCH_TIMEOUT,
                     extra_headers: dict[str, str] | None = None) -> dict:
    """Fetch a URL using plain HTTP (urllib) — lightweight, no JS execution.

    Returns ``{"url": ..., "content": ..., "error": ..., "method": "urllib"}``.
    """
    try:
        headers = {"User-Agent": _USER_AGENT}
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if "text" not in ctype and "html" not in ctype and "json" not in ctype:
                return {"url": url, "content": "",
                        "error": f"Non-text content type: {ctype}",
                        "method": "urllib"}
            raw = resp.read(200_000)
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            text = extract_text(html)
            text = truncate_content(text)
            return {"url": url, "content": text, "error": "", "method": "urllib"}
    except urllib.error.HTTPError as exc:
        return {"url": url, "content": "", "error": f"HTTP {exc.code}",
                "method": "urllib"}
    except Exception as exc:
        return {"url": url, "content": "", "error": str(exc), "method": "urllib"}


def _fetch_with_bearer_token(url: str, timeout: int = _URL_FETCH_TIMEOUT) -> dict:
    """Try to fetch a URL by attaching an Azure CLI bearer token.

    Uses ``AzureCliCredential`` to get a token for the default Azure scope
    and passes it as an ``Authorization: Bearer`` header.  Works for many
    Microsoft-internal portals that accept AAD tokens.

    Returns ``{"url": ..., "content": ..., "error": ..., "method": "bearer"}``.
    """
    try:
        from azure.identity import AzureCliCredential
    except ImportError:
        return {"url": url, "content": "", "error": "azure-identity not installed",
                "method": "bearer"}

    try:
        cred = AzureCliCredential()
        token = cred.get_token(_AZURE_DEFAULT_SCOPE)
        logger.debug("Bearer token acquired for %s", url)
    except Exception as exc:
        logger.debug("Bearer token acquisition failed: %s", exc)
        return {"url": url, "content": "", "error": f"token_failed: {exc}",
                "method": "bearer"}

    result = _fetch_via_urllib(
        url, timeout,
        extra_headers={"Authorization": f"Bearer {token.token}"},
    )
    result["method"] = "bearer"

    # Even with a valid token, some sites still redirect to login
    if result["content"] and _is_login_page(result["content"]):
        logger.debug("Bearer fetch still hit login page for %s", url)
        return {"url": url, "content": "", "error": "bearer_rejected",
                "method": "bearer"}
    # Bearer + urllib can't render JS — detect SPA shell
    if result["content"] and _is_js_shell(result["content"]):
        logger.debug("Bearer fetch returned JS shell for %s (%d chars)",
                     url, len(result["content"]))
        return {"url": url, "content": "", "error": "bearer_js_shell",
                "method": "bearer"}
    return result


def _get_edge_user_data_dir() -> str | None:
    """Find the Edge user-data directory for the current OS.

    Returns the path if it exists, else ``None``.
    """
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", "")
        candidate = os.path.join(base, "Microsoft", "Edge", "User Data")
    elif os.name == "posix":  # macOS / Linux
        home = os.path.expanduser("~")
        import sys
        if sys.platform == "darwin":
            candidate = os.path.join(
                home, "Library", "Application Support",
                "Microsoft Edge", "Default",
            )
        else:
            candidate = os.path.join(home, ".config", "microsoft-edge")
    else:
        return None
    return candidate if os.path.isdir(candidate) else None


# Directories to skip when copying an Edge profile (large/unnecessary)
_EDGE_PROFILE_SKIP_DIRS = frozenset({
    "Cache", "Code Cache", "Service Worker", "GPUCache",
    "blob_storage", "File System", "IndexedDB", "Sessions",
    "Extension State", "Extension Rules", "Extensions",
    "Local Extension Settings", "Sync Extension Settings",
    "GCM Store", "optimization_guide_prediction_model_downloads",
    "Download Service", "BudgetDatabase", "DawnCache",
    "DawnGraphiteCache", "GrShaderCache", "ShaderCache",
    "Storage", "ScriptCache", "WebStorage",
    "JumpListIconsMostVisited", "JumpListIconsRecentClosed",
    "Feature Engagement Tracker", "Segmentation Platform",
})


def _find_edge_work_profile(user_data_dir: str) -> str | None:
    """Return the profile directory name for a 'Work' or managed profile.

    Reads Edge's ``Local State`` file and looks for a profile whose name
    contains *work*, or that has a ``hosted_domain`` (managed account).
    Falls back to the ``last_used`` profile if no explicit work profile
    is found.
    """
    import json as _json

    local_state_path = os.path.join(user_data_dir, "Local State")
    if not os.path.isfile(local_state_path):
        return None
    try:
        with open(local_state_path, "r", encoding="utf-8") as fh:
            data = _json.load(fh)
        info_cache = data.get("profile", {}).get("info_cache", {})
        for profile_dir, info in info_cache.items():
            name = (info.get("name") or "").lower()
            if "work" in name:
                return profile_dir
            if info.get("hosted_domain") or info.get("managed_user_id"):
                return profile_dir
        last_used = data.get("profile", {}).get("last_used")
        if last_used and last_used in info_cache:
            return last_used
    except (ValueError, KeyError, OSError):
        pass
    return None


def _copy_edge_profile(user_data_dir: str, profile_name: str) -> str | None:
    """Copy essential Edge profile files to a temporary directory.

    Copies ``Local State`` plus the named profile's files (skipping large
    cache/storage directories) into ``<temp>/Default/`` so that Playwright
    picks them up as the default profile.

    Returns the temp directory path, or ``None`` on failure.
    """
    import shutil
    import tempfile

    src_profile = os.path.join(user_data_dir, profile_name)
    if not os.path.isdir(src_profile):
        return None

    temp_dir = tempfile.mkdtemp(prefix="sfi_edge_")

    # Copy Local State (contains cookie-encryption key)
    local_state = os.path.join(user_data_dir, "Local State")
    if os.path.isfile(local_state):
        try:
            shutil.copy2(local_state, os.path.join(temp_dir, "Local State"))
        except OSError:
            pass

    # Copy profile into Default/ inside the temp dir
    dst_profile = os.path.join(temp_dir, "Default")
    os.makedirs(dst_profile, exist_ok=True)

    try:
        for item in os.listdir(src_profile):
            if item in _EDGE_PROFILE_SKIP_DIRS:
                continue
            src_path = os.path.join(src_profile, item)
            dst_path = os.path.join(dst_profile, item)
            try:
                if os.path.isdir(src_path):
                    shutil.copytree(
                        src_path, dst_path, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("Cache*", "*.log"),
                    )
                else:
                    shutil.copy2(src_path, dst_path)
            except (PermissionError, OSError):
                continue  # skip locked files
    except OSError as exc:
        logger.debug("Profile copy failed: %s", exc)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

    logger.debug("Copied Edge profile '%s' → %s", profile_name, temp_dir)
    return temp_dir


def _fetch_via_edge_cdp(url: str, timeout: int = _URL_FETCH_TIMEOUT) -> dict:
    """Fetch a URL using Playwright with the Edge channel + user profile.

    Copies the user's Edge profile to a temporary directory (to avoid the
    lock held by a running Edge process), then launches Edge headless
    against that copy.  The user's cookies / SSO sessions are preserved,
    letting us bypass auth walls the user has already signed in to.

    Returns ``{"url": ..., "content": ..., "error": ..., "method": "edge_cdp"}``.
    """
    import shutil

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"url": url, "content": "", "error": "playwright not installed",
                "method": "edge_cdp"}

    user_data = _get_edge_user_data_dir()
    if not user_data:
        return {"url": url, "content": "",
                "error": "edge_profile_not_found",
                "method": "edge_cdp"}

    # Find the work profile and copy it to a temp dir
    profile_name = _find_edge_work_profile(user_data) or "Default"
    temp_dir = _copy_edge_profile(user_data, profile_name)
    if not temp_dir:
        return {"url": url, "content": "",
                "error": "edge_profile_copy_failed",
                "method": "edge_cdp"}

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch_persistent_context(
                user_data_dir=temp_dir,
                channel="msedge",
                headless=True,
                args=["--no-first-run", "--disable-extensions"],
            )
            page = browser.new_page()
            page.set_default_timeout(timeout * 1000)
            page.goto(url, wait_until="networkidle")

            final_url = page.url
            if _AUTH_REDIRECT_DOMAINS.search(final_url):
                logger.info("Edge CDP still hit auth redirect for %s", url)
                browser.close()
                return {"url": url, "content": "",
                        "error": "edge_auth_redirect",
                        "method": "edge_cdp"}

            html = page.content()
            browser.close()

        text = extract_text(html)
        if _is_login_page(text):
            return {"url": url, "content": "",
                    "error": "edge_auth_wall",
                    "method": "edge_cdp"}
        if _is_js_shell(text):
            return {"url": url, "content": "",
                    "error": "edge_js_shell",
                    "method": "edge_cdp"}
        text = truncate_content(text)
        return {"url": url, "content": text, "error": "",
                "method": "edge_cdp"}
    except Exception as exc:
        return {"url": url, "content": "", "error": str(exc),
                "method": "edge_cdp"}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def fetch_url_content(
    url: str,
    timeout: int = _URL_FETCH_TIMEOUT,
) -> dict:
    """Fetch a URL and extract text content.

    Cascade:
      1. Headless Chromium CDP (handles SPAs)
      2. If auth redirect → bearer token via AzureCliCredential
      3. If bearer fails → Edge CDP with user profile cookies
      4. If all auth methods fail → auth_redirect error
      5. If no auth issue → fall back to plain urllib

    Returns ``{"url": ..., "content": ..., "error": ..., "method": ...}``.
    """
    # ---------- Step 1: CDP (headless Chromium) ----------
    result = _fetch_via_cdp(url, timeout)

    if result.get("error") == "auth_redirect":
        # Auth wall detected — try authenticated methods before giving up
        logger.info("Auth redirect on %s — trying bearer token", url)

        # ---------- Step 2: Bearer token via AzureCliCredential ----------
        bearer = _fetch_with_bearer_token(url, timeout)
        if bearer["content"]:
            logger.info("Fetched %s via bearer token (%d chars)",
                        url, len(bearer["content"]))
            return bearer

        # ---------- Step 3: Edge CDP (reuse user cookies) ----------
        logger.info("Bearer failed for %s — trying Edge CDP with user profile", url)
        edge = _fetch_via_edge_cdp(url, timeout)
        if edge["content"]:
            logger.info("Fetched %s via Edge CDP (%d chars)",
                        url, len(edge["content"]))
            return edge

        # All auth methods exhausted
        logger.info("All auth methods failed for %s (bearer: %s, edge: %s)",
                    url, bearer.get("error"), edge.get("error"))
        return {"url": url, "content": "",
                "error": "auth_redirect", "method": "cdp"}

    if result["content"]:
        logger.info("Fetched %s via CDP (%d chars)", url, len(result["content"]))
        return result

    # ---------- Fallback: plain urllib (static pages) ----------
    cdp_error = result.get("error", "")
    result = _fetch_via_urllib(url, timeout)
    if result["content"] and _is_js_shell(result["content"]):
        logger.debug("urllib returned JS shell for %s (%d chars)",
                     url, len(result["content"]))
        result["content"] = ""
        result["error"] = f"js_shell (CDP also failed: {cdp_error})" if cdp_error else "js_shell"
    elif not result["content"] and cdp_error and cdp_error != "playwright not installed":
        result["error"] = f"{result['error']} (CDP also failed: {cdp_error})"
    elif result["content"]:
        logger.info("Fetched %s via urllib (%d chars)", url, len(result["content"]))
    return result


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


def _fetch_with_provenance(
    urls: set[str],
    timeout: int = _URL_FETCH_TIMEOUT,
    max_urls: int = _MAX_URLS,
) -> tuple[dict[str, str], list[FetchResult]]:
    """Fetch URLs and return both content mapping and provenance metadata.

    Returns:
        A tuple of (fetched_docs dict, list of FetchResult).
    """
    if not urls:
        return {}, []

    url_list = sorted(urls)[:max_urls]
    fetched_docs: dict[str, str] = {}
    fetch_results: list[FetchResult] = []

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fetch_url_content, u, timeout): u for u in url_list}
        for future in as_completed(futures):
            result = future.result()
            url_key = result["url"]
            method = result.get("method", "urllib")
            discovered = result.get("discovered_urls", [])

            if result["content"]:
                content = result["content"]
                # Detect login / auth walls masquerading as content
                if _is_login_page(content):
                    logger.info("Auth wall detected for %s — discarding content", url_key)
                    fetched_docs[url_key] = _AUTH_BLOCKED_MSG
                    fetch_results.append(
                        FetchResult(url=url_key, ok=False, chars=0,
                                    error="auth_wall", method=method,
                                    discovered_urls=discovered))
                else:
                    fetched_docs[url_key] = content
                    fetch_results.append(
                        FetchResult(url=url_key, ok=True,
                                    chars=len(content),
                                    error="", method=method,
                                    discovered_urls=discovered))
            elif result.get("error") == "auth_redirect":
                # CDP detected auth redirect — mark as auth wall immediately
                fetched_docs[url_key] = _AUTH_BLOCKED_MSG
                fetch_results.append(
                    FetchResult(url=url_key, ok=False, chars=0,
                                error="auth_wall", method=method,
                                discovered_urls=discovered))
            elif "js_shell" in (result.get("error") or ""):
                # JS SPA shell — urllib/bearer couldn't render the page
                fetched_docs[url_key] = _AUTH_BLOCKED_MSG
                fetch_results.append(
                    FetchResult(url=url_key, ok=False, chars=0,
                                error="auth_wall", method=method,
                                discovered_urls=discovered))
            else:
                fetched_docs[url_key] = f"(Could not fetch: {result['error']})"
                fetch_results.append(
                    FetchResult(url=url_key, ok=False, chars=0,
                                error=result["error"], method=method,
                                discovered_urls=discovered))

    successes = sum(1 for r in fetch_results if r.ok)
    failures = len(fetch_results) - successes
    logger.info(
        "URL fetch complete: %d success, %d failed out of %d",
        successes, failures, len(url_list),
    )
    return fetched_docs, fetch_results


# ---------------------------------------------------------------------------
# Sources provenance card (SFI-035)
# ---------------------------------------------------------------------------

def format_sources_card(result: AnalysisResult) -> str:
    """Format a human-readable provenance summary for the Sources card.

    Args:
        result: The AnalysisResult containing fetch metadata.

    Returns:
        A formatted string suitable for display in the chat panel.
    """
    total = len(result.fetch_results)
    successes = sum(1 for r in result.fetch_results if r.ok)
    failures = total - successes

    if total == 0:
        return "\U0001f4cb Sources \u2014 No documentation URLs found in action items"

    lines = [f"\U0001f4cb Sources ({total} URLs extracted, {successes} fetched, {failures} failed)"]
    fetched_urls = {fr.url for fr in result.fetch_results}
    for fr in result.fetch_results:
        if fr.ok:
            lines.append(f"  \u2705 {fr.url}  ({fr.chars} chars via {fr.method})")
        elif fr.error == "auth_wall":
            lines.append(f"  \U0001f512 {fr.url}  (login / auth wall)")
        else:
            lines.append(f"  \u274c {fr.url}  ({fr.error})")
        # Show discovered URLs (skip those we already fetched)
        novel = [u for u in fr.discovered_urls if u not in fetched_urls][:5]
        for durl in novel:
            lines.append(f"    \u21b3 discovered: {durl}")

    # Add Edge hint if any URLs hit auth walls
    has_auth_walls = any(fr.error == "auth_wall" for fr in result.fetch_results)
    if has_auth_walls:
        lines.append("")
        lines.append(_AUTH_HINT_MSG)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Save fetched docs to disk
# ---------------------------------------------------------------------------

def _safe_filename(url: str) -> str:
    """Generate a filesystem-safe filename from a URL."""
    # Use a hash suffix to avoid collisions for long/similar URLs
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    # Extract a readable portion from the URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    name = parsed.netloc.replace(".", "_")
    path_part = parsed.path.strip("/").replace("/", "_")[:40]
    if path_part:
        name += f"__{path_part}"
    return f"{name}__{h}.txt"


def _save_fetched_docs(
    fetched_docs: dict[str, str],
    kpi_name: str,
) -> Path:
    """Save each fetched document to ``temp/sfireporter/<kpi_name>/docs/``.

    Returns the docs directory path.
    """
    # Sanitise KPI name for filesystem
    safe_kpi = re.sub(r'[<>:"/\\|?*]', '_', kpi_name)[:80]
    docs_dir = Path(tempfile.gettempdir()) / "sfireporter" / safe_kpi / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[tuple[str, str, str]] = []  # (url, filename, status)
    for url, content in fetched_docs.items():
        fname = _safe_filename(url)
        fpath = docs_dir / fname
        is_error = content.startswith("(Could not fetch:")
        fpath.write_text(
            f"URL: {url}\n"
            f"Status: {'FAILED' if is_error else 'OK'}\n"
            f"{'=' * 60}\n"
            f"{content}\n",
            encoding="utf-8",
        )
        manifest.append((url, fname, "FAILED" if is_error else "OK"))
        logger.debug("Saved fetched doc: %s -> %s", url, fpath)

    # Write a manifest index file
    manifest_path = docs_dir / "_manifest.txt"
    lines = [f"Fetched docs for KPI: {kpi_name}\n{'=' * 60}"]
    for url, fname, status in manifest:
        lines.append(f"[{status}] {fname}\n        {url}")
    manifest_path.write_text("\n".join(lines), encoding="utf-8")

    logger.info("Saved %d fetched docs to %s", len(fetched_docs), docs_dir)
    return docs_dir


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
    docs_dir: str = "",
) -> str:
    """Build a structured analysis prompt for the LLM.

    Args:
        items: All action items for the KPI.
        fetched_docs: Mapping of URL → extracted text content.
        docs_dir: If provided, emit a file manifest instead of inline content.

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
    has_readable_docs = False
    if docs_dir and fetched_docs:
        # Check if there's anything actually readable
        for url, content in fetched_docs.items():
            if not (content.startswith("(Could not fetch:") or content.startswith("(Authentication wall")):
                has_readable_docs = True
                break

    if docs_dir and has_readable_docs:
        # Manifest mode: list saved files so the LLM can read them on demand
        manifest_parts = ["Documents have been saved to disk. Use the "
                          "`read_fetched_doc` tool to read any file listed below.\n"]
        for url, content in fetched_docs.items():
            fname = _safe_filename(url)
            is_blocked = content.startswith("(Could not fetch:") or content.startswith("(Authentication wall")
            if is_blocked:
                manifest_parts.append(f"- \u274c **BLOCKED** \u2014 {url}  (auth wall or fetch error)")
            else:
                chars = len(content)
                manifest_parts.append(f"- **{fname}** ({chars:,} chars) \u2014 {url}")
        doc_lines = "\n".join(manifest_parts)
    elif fetched_docs:
        doc_parts = []
        for url, content in fetched_docs.items():
            doc_parts.append(f"### {url}\n{content}\n")
        doc_lines = "\n".join(doc_parts)
    else:
        doc_lines = "(No documentation URLs available or all fetches failed.)"

    # When docs are on disk, allow the LLM to read them and optionally fetch more
    tool_instruction = (
        "IMPORTANT: All item data and documentation content has already been gathered\n"
        "and is provided below. Do NOT call any tools \u2014 just analyze the information given.\n"
        "If access to a URL was blocked, it is noted in the documentation section."
    )
    if docs_dir and has_readable_docs:
        tool_instruction = (
            "IMPORTANT: All item data has been gathered. Documentation has been saved to disk.\n"
            "Use the `read_fetched_doc` tool to read files listed in the Documentation section.\n"
            "Read the most relevant documents before providing your analysis.\n"
            "Skip any URLs marked BLOCKED \u2014 they require interactive auth and have no content.\n"
            "If the documentation is insufficient, you may use `web_fetch` to fetch additional URLs\n"
            "that you discover in the content or that might provide remediation guidance.\n"
            "Do not re-fetch URLs that are already in the manifest."
        )
    elif docs_dir and fetched_docs and not has_readable_docs:
        # All docs were blocked — tell the LLM to skip file tools entirely
        tool_instruction = (
            "IMPORTANT: All documentation URLs were blocked by authentication walls.\n"
            "Do NOT call read_fetched_doc \u2014 there are no readable files.\n"
            "Provide your best analysis based on the KPI name, action item details,\n"
            "and your general knowledge of Azure/SFI compliance requirements.\n"
            "You may use `web_fetch` to look up public Microsoft Learn or aka.ms\n"
            "documentation for the relevant KPI or security standard."
        )

    prompt = f"""Analyze the following SFI/QEI KPI and its action items in detail.

{tool_instruction}

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
# URL discovery from fetched content
# ---------------------------------------------------------------------------

def _discover_relevant_urls(
    fetched_docs: dict[str, str],
    fetch_results: list[FetchResult],
    already_known: set[str],
    max_discovered: int = 5,
) -> set[str]:
    """Scan fetched content and CDP-discovered links for new relevant URLs.

    Returns a set of URLs worth fetching in a second pass (capped at
    *max_discovered* to avoid runaway crawling).
    """
    candidates: set[str] = set()

    # 1. URLs discovered by CDP on fetched pages
    for fr in fetch_results:
        for durl in fr.discovered_urls:
            if durl not in already_known:
                candidates.add(durl)

    # 2. URLs found in the text content itself
    for content in fetched_docs.values():
        if content.startswith("(Could not fetch:"):
            continue
        for m in _TEXT_URL_RE.finditer(content):
            url = m.group(0).rstrip(".,;:!?)")
            if url not in already_known:
                candidates.add(url)

    # Filter: must pass relevance check and exclusion filter
    relevant: set[str] = set()
    for url in candidates:
        if _DISCOVERED_URL_EXCLUDE.search(url):
            continue
        if _RELEVANT_URL_PATTERNS.search(url):
            relevant.add(url)

    # Cap to avoid runaway fetching
    if len(relevant) > max_discovered:
        relevant = set(sorted(relevant)[:max_discovered])

    return relevant


# ---------------------------------------------------------------------------
# Main analysis entry point
# ---------------------------------------------------------------------------

def analyze_kpi(app: "SFIReporterApp", kpi_id: str) -> AnalysisResult:
    """Gather items for a KPI, fetch docs, and build the analysis prompt.

    This function does I/O (URL fetching) and should be called from a
    background thread.

    Args:
        app: The running SFIReporterApp instance.
        kpi_id: The KPI identifier to analyze.

    Returns:
        An AnalysisResult with the prompt and provenance metadata.
    """
    # 1. Gather all items for this KPI
    all_items = (app.current_data or {}).get("detailed_items", [])
    kpi_items = [i for i in all_items if i.get("_kpi_id") == kpi_id]

    if not kpi_items:
        return AnalysisResult(
            prompt=f"No action items found for KPI '{kpi_id}'.",
            urls_found=[],
            fetch_results=[],
        )

    logger.info(
        "Analyzing KPI %s: %d items",
        kpi_id, len(kpi_items),
    )

    # 2. Collect unique URLs
    urls = collect_urls(kpi_items)
    urls_found = sorted(urls)
    logger.info("Collected %d unique URLs for KPI %s", len(urls), kpi_id)

    # 3. Fetch URL content (also builds provenance metadata)
    fetched_docs, fetch_results = _fetch_with_provenance(urls)

    # 3.5 Recursive discovery: follow relevant links found in fetched content
    already_fetched = set(fetched_docs.keys()) | urls
    max_depth = 3  # prevent runaway crawling
    for depth in range(1, max_depth + 1):
        discovered_urls = _discover_relevant_urls(
            fetched_docs, fetch_results, already_fetched,
        )
        if not discovered_urls:
            break
        logger.info(
            "Discovery pass %d: %d relevant URLs found for KPI %s",
            depth, len(discovered_urls), kpi_id,
        )
        extra_docs, extra_results = _fetch_with_provenance(discovered_urls)
        fetched_docs.update(extra_docs)
        fetch_results.extend(extra_results)
        urls_found.extend(sorted(discovered_urls))
        already_fetched.update(discovered_urls)

    # 4. Save fetched docs to disk
    kpi_name = kpi_items[0].get("_kpi_name", kpi_id)
    docs_dir = _save_fetched_docs(fetched_docs, kpi_name)
    docs_dir_str = str(docs_dir)

    # 5. Build prompt (references saved files, not inline content)
    prompt = build_analysis_prompt(kpi_items, fetched_docs, docs_dir=docs_dir_str)

    logger.info(
        "Analysis prompt built for KPI %s: %d chars, %d items, %d URLs fetched, docs at %s",
        kpi_id, len(prompt), len(kpi_items), len(fetched_docs), docs_dir_str,
    )

    return AnalysisResult(
        prompt=prompt,
        urls_found=urls_found,
        fetch_results=fetch_results,
        docs_dir=docs_dir_str,
    )
