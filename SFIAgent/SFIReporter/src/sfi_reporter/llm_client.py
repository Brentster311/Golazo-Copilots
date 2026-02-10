"""LLM client for SFI action item analysis using Azure OpenAI.

Provides configuration, prompt building, and API call functionality.
"""
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone

from llm_extender.exceptions import ProviderError
from llm_extender.url_fetcher import fetch_url

logger = logging.getLogger(__name__)


class LLMConfigError(Exception):
    """Raised when LLM configuration is missing or invalid."""
    pass


class LLMError(Exception):
    """Raised when an LLM API call fails."""
    pass


SYSTEM_PROMPT = """\
You are an SFI (Security, Fundamentals, and Infrastructure) remediation analyst.
Analyze the following action item data and produce a structured assessment.

## Output Format (use these exact section headers):

### 🎯 Mission
What is being asked? Summarize the remediation objective in 2-3 sentences.

### ✅ Steps to Done
Provide a concise, numbered list of actionable steps to complete remediation.

### 🔧 Resources Needing Repair
List the specific resources, services, or assets that need attention.
Include resource type, name/ID, and subscription if available.

### ⚠️ Risk of Delay
What are the consequences of not completing this on time?
Consider SLA impact, compliance implications, and downstream effects.
"""


@dataclass
class LLMConfig:
    """Configuration for Azure OpenAI LLM calls.

    Authentication uses Azure CLI credential (``az login``) — no API keys.
    """
    endpoint: str
    deployment: str = "gpt-4o"
    api_version: str = "2024-10-21"
    timeout: int = 90

    def __repr__(self) -> str:
        return (
            f"LLMConfig(endpoint='{self.endpoint}', "
            f"deployment='{self.deployment}', "
            f"api_version='{self.api_version}', "
            f"timeout={self.timeout})"
        )

    __str__ = __repr__

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load configuration from environment variables.

        Required:
            AZURE_OPENAI_ENDPOINT: Azure OpenAI resource endpoint

        Optional:
            AZURE_OPENAI_DEPLOYMENT: Model deployment name (default: gpt-4o)
            AZURE_OPENAI_API_VERSION: API version (default: 2024-10-21)

        Raises:
            LLMConfigError: If required environment variables are missing.
        """
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()

        if not endpoint:
            raise LLMConfigError(
                "Missing required environment variable: AZURE_OPENAI_ENDPOINT.\n\n"
                "To use the LLM analysis feature, set this environment variable:\n"
                "  AZURE_OPENAI_ENDPOINT = https://your-resource.openai.azure.com/\n"
                "  AZURE_OPENAI_DEPLOYMENT = gpt-4o  (optional)\n\n"
                "Or use ⚙️ Configure LLM to save settings.\n"
                "Authentication uses Azure CLI — run `az login` first.\n"
            )

        return cls(
            endpoint=endpoint,
            deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip(),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21").strip(),
        )


@dataclass
class AnalysisResult:
    """Structured result of an LLM analysis."""
    action_item_id: str
    kpi_id: str
    title: str
    analysis_text: str
    mission: str = ""
    steps_to_done: str = ""
    resources: str = ""
    risk_of_delay: str = ""
    model: str = ""
    timestamp: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0


def _truncate(text: str, max_chars: int = 2000) -> str:
    """Truncate text to max_chars, appending ellipsis if truncated."""
    if not text or len(text) <= max_chars:
        return text or ""
    return text[:max_chars] + "... [truncated]"


# ── SFI-021: URL Content Enrichment ───────────────────────────────────

# Fields that may contain URLs to fetch for LLM context enrichment.
_SINGLE_URL_FIELDS = (
    "ActionWikiLink",
    "CustomGroupingLink",
    "AssetTypeLink0",
    "AssetTypeLink1",
    "AssetTypeLink2",
)

_RESOURCE_URI_SPLIT_RE = re.compile(r"[;\s,]+")


def _extract_urls(item: dict) -> list[str]:
    """Extract unique, non-empty URLs from known action-item fields."""
    urls: list[str] = []
    seen: set[str] = set()

    # ResourceURIs can contain multiple URLs separated by ; , or whitespace
    raw_uris = item.get("ResourceURIs") or ""
    if raw_uris:
        for part in _RESOURCE_URI_SPLIT_RE.split(str(raw_uris).strip()):
            part = part.strip()
            if part and part not in seen:
                urls.append(part)
                seen.add(part)

    # Single-value URL fields
    for field_name in _SINGLE_URL_FIELDS:
        val = item.get(field_name) or ""
        if val:
            val = str(val).strip()
            if val and val not in seen:
                urls.append(val)
                seen.add(val)

    return urls


def fetch_action_item_urls(item: dict) -> dict[str, str]:
    """Fetch content from URLs embedded in an action item.

    Extracts URLs from ResourceURIs, ActionWikiLink, CustomGroupingLink,
    and AssetTypeLink0/1/2. Each URL is fetched concurrently using
    llm-extender's ``fetch_url``.  Failed or timed-out URLs are silently
    skipped.

    Args:
        item: Action item data dict.

    Returns:
        Mapping of URL → fetched text content (only successful fetches).
    """
    urls = _extract_urls(item)
    if not urls:
        return {}

    results: dict[str, str] = {}

    def _fetch_one(url: str) -> tuple[str, str | None]:
        try:
            content = fetch_url(url, timeout=10, max_length=1500)
            return url, content
        except Exception as exc:
            logger.debug("URL fetch failed for %s: %s", url, exc)
            return url, None

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(_fetch_one, url): url for url in urls}
        for future in as_completed(futures):
            url, content = future.result()
            if content is not None:
                results[url] = content

    return results


def _format_item_for_prompt(item: dict) -> str:
    """Format an action item dict into a readable string for the LLM prompt."""
    lines = []

    def add(label: str, *keys: str, truncate: int = 0):
        for key in keys:
            val = item.get(key, "")
            if val:
                val = str(val).strip()
                if truncate:
                    val = _truncate(val, truncate)
                lines.append(f"**{label}**: {val}")
                return
        lines.append(f"**{label}**: N/A")

    add("Title", "title", "Title")
    add("KPI ID", "_kpi_id")
    add("Action Item ID", "id", "S360_ActionItemId")
    add("Status", "ActionItemStatus")
    add("SLA Type", "SlaType")
    add("Due Date", "dueDate", "DueDate")
    add("ETA Date", "EtaDate")
    add("ETA Status", "EtaStatus")
    add("Created Date", "createdDate")

    # Service tree
    add("Division", "S360_ServiceTreeDivisionName")
    add("Group", "S360_ServiceTreeGroupName")
    add("Organization", "S360_ServiceTreeOrganizationName")
    add("Service", "S360_ServiceTreeServiceName")

    # Ownership
    add("Assigned To", "S360_AssignedToName", "S360_AssignedTo")
    add("Action Owner", "ActionOwnerName", "ActionOwnerAlias")

    # Details
    add("Remediation", "Remediation", truncate=2000)
    add("Details", "Details", truncate=1000)

    # Cloud / Environment
    add("Clouds", "Clouds")
    add("Environments", "Environments")

    # Assets
    for i in range(3):
        asset_type = item.get(f"AssetType{i}", "")
        asset_link = item.get(f"AssetTypeLink{i}", "")
        if asset_type or asset_link:
            lines.append(f"**Asset {i}**: {asset_type} — {asset_link}")

    # Resource URIs
    uris = item.get("ResourceURIs", "")
    if uris:
        lines.append(f"**Resource URIs**: {_truncate(str(uris), 500)}")

    # Wiki / custom links
    add("Action Wiki Link", "ActionWikiLink")
    add("Custom Grouping Link", "CustomGroupingLink")

    return "\n".join(lines)


def build_prompt(item: dict, url_content: dict[str, str] | None = None) -> list[dict]:
    """Build the chat messages for the LLM analysis.

    Args:
        item: Action item data dict.
        url_content: Optional mapping of URL → fetched text content (for SFI-021).

    Returns:
        List of message dicts for the chat completions API.
    """
    user_text = f"## Action Item Data\n\n{_format_item_for_prompt(item)}"

    if url_content:
        url_sections = []
        for url, content in url_content.items():
            url_sections.append(f"### {url}\n{_truncate(content, 1500)}")
        user_text += "\n\n## Additional Context from URLs\n\n" + "\n\n".join(url_sections)

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]


def _parse_sections(text: str) -> dict[str, str]:
    """Parse the LLM response into named sections.

    Looks for the four expected section headers and extracts content between them.
    """
    sections = {
        "mission": "",
        "steps_to_done": "",
        "resources": "",
        "risk_of_delay": "",
    }

    # Map header patterns to section keys
    header_map = {
        "mission": ["🎯 mission", "mission"],
        "steps_to_done": ["✅ steps to done", "steps to done"],
        "resources": ["🔧 resources needing repair", "resources needing repair", "resources"],
        "risk_of_delay": ["⚠️ risk of delay", "risk of delay"],
    }

    lines = text.split("\n")
    current_section = None
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip().lstrip("#").strip().lower()
        matched = False
        for key, patterns in header_map.items():
            if any(stripped == p or stripped.startswith(p) for p in patterns):
                if current_section and current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = key
                current_lines = []
                matched = True
                break
        if not matched and current_section is not None:
            current_lines.append(line)

    # Capture the last section
    if current_section and current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def analyze_item(item: dict, config: LLMConfig, url_content: dict[str, str] | None = None) -> AnalysisResult:
    """Analyze an action item using Azure OpenAI.

    Args:
        item: Action item data dict.
        config: LLM configuration.
        url_content: Optional URL content for enrichment (SFI-021).

    Returns:
        AnalysisResult with structured analysis.

    Raises:
        LLMError: If the API call fails.
    """
    try:
        from openai import AzureOpenAI
    except ImportError as e:
        raise LLMError(
            "The 'openai' package is not installed. "
            "Install it with: pip install openai>=1.0.0"
        ) from e

    try:
        from azure.identity import AzureCliCredential, get_bearer_token_provider
    except ImportError as e:
        raise LLMError(
            "The 'azure-identity' package is not installed. "
            "Install it with: pip install azure-identity"
        ) from e

    messages = build_prompt(item, url_content=url_content)

    try:
        token_provider = get_bearer_token_provider(
            AzureCliCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        client = AzureOpenAI(
            azure_endpoint=config.endpoint,
            azure_ad_token_provider=token_provider,
            api_version=config.api_version,
            timeout=config.timeout,
            max_retries=0,
        )

        logger.info("Calling Azure OpenAI (deployment=%s)...", config.deployment)
        response = client.chat.completions.create(
            model=config.deployment,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=2000,
        )

        choice = response.choices[0]
        analysis_text = choice.message.content or ""
        usage = response.usage

        sections = _parse_sections(analysis_text)

        title = item.get("title", item.get("Title", "Unknown"))

        return AnalysisResult(
            action_item_id=str(item.get("id", item.get("S360_ActionItemId", "unknown"))),
            kpi_id=str(item.get("_kpi_id", "")),
            title=title,
            analysis_text=analysis_text,
            mission=sections["mission"],
            steps_to_done=sections["steps_to_done"],
            resources=sections["resources"],
            risk_of_delay=sections["risk_of_delay"],
            model=config.deployment,
            timestamp=datetime.now(timezone.utc).isoformat(),
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )

    except ImportError:
        raise
    except Exception as e:
        error_type = type(e).__name__
        logger.error("LLM analysis failed: %s: %s", error_type, e)
        raise LLMError(f"LLM analysis failed ({error_type}): {e}") from e
