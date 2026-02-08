"""URL content fetcher for LLM Extender.

Fetches web page content, strips HTML to readable text, and provides
both sync and async variants. Supports authenticated fetches via
AuthStrategy (e.g., AzureChainedAuth with a custom scope).
"""

from __future__ import annotations

from html.parser import HTMLParser
from typing import TYPE_CHECKING

import httpx

from llm_extender.exceptions import ProviderError

if TYPE_CHECKING:
    from llm_extender.auth.base import AuthStrategy

_USER_AGENT = "LLMExtender/1.0"
_DEFAULT_MAX_LENGTH = 50_000


# ---------------------------------------------------------------------------
# HTML-to-text extractor (stdlib, no external deps)
# ---------------------------------------------------------------------------

class _HTMLTextExtractor(HTMLParser):
    """Strip HTML tags, scripts, and styles — keep only visible text."""

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._pieces.append(data)

    def get_text(self) -> str:
        return " ".join(self._pieces).strip()


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text, stripping tags/scripts/styles."""
    extractor = _HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_url(
    url: str,
    *,
    auth: AuthStrategy | None = None,
    timeout: float = 30.0,
    max_length: int = _DEFAULT_MAX_LENGTH,
) -> str:
    """Fetch a URL and return its text content (HTML stripped).

    Args:
        url: The URL to fetch.
        auth: Optional auth strategy. If provided, the resolved token is
            sent as a ``Authorization: Bearer <token>`` header.
        timeout: HTTP timeout in seconds.
        max_length: Maximum character length of the returned text.
            Content is truncated if it exceeds this limit.

    Returns:
        The extracted text content from the page.

    Raises:
        ProviderError: If the HTTP request fails (non-2xx status).
    """
    headers: dict[str, str] = {"User-Agent": _USER_AGENT}
    if auth is not None:
        token = auth.resolve()
        headers["Authorization"] = f"Bearer {token}"

    with httpx.Client(timeout=httpx.Timeout(timeout), follow_redirects=True) as client:
        response = client.get(url, headers=headers)

    if response.status_code >= 400:
        raise ProviderError(
            f"Failed to fetch URL '{url}': HTTP {response.status_code}"
        )

    content_type = response.headers.get("content-type", "")
    raw_text = response.text

    if "text/html" in content_type or "<" in raw_text[:100]:
        text = _html_to_text(raw_text)
    else:
        text = raw_text

    if len(text) > max_length:
        text = text[:max_length]

    return text


async def afetch_url(
    url: str,
    *,
    auth: AuthStrategy | None = None,
    timeout: float = 30.0,
    max_length: int = _DEFAULT_MAX_LENGTH,
) -> str:
    """Fetch a URL asynchronously and return its text content (HTML stripped).

    Args:
        url: The URL to fetch.
        auth: Optional auth strategy. If provided, the resolved token is
            sent as a ``Authorization: Bearer <token>`` header. Uses
            ``aresolve()`` for async credential resolution.
        timeout: HTTP timeout in seconds.
        max_length: Maximum character length of the returned text.

    Returns:
        The extracted text content from the page.

    Raises:
        ProviderError: If the HTTP request fails (non-2xx status).
    """
    headers: dict[str, str] = {"User-Agent": _USER_AGENT}
    if auth is not None:
        token = await auth.aresolve()
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(timeout), follow_redirects=True
    ) as client:
        response = await client.get(url, headers=headers)

    if response.status_code >= 400:
        raise ProviderError(
            f"Failed to fetch URL '{url}': HTTP {response.status_code}"
        )

    content_type = response.headers.get("content-type", "")
    raw_text = response.text

    if "text/html" in content_type or "<" in raw_text[:100]:
        text = _html_to_text(raw_text)
    else:
        text = raw_text

    if len(text) > max_length:
        text = text[:max_length]

    return text


def _build_context_prompt(url: str, content: str, user_prompt: str) -> str:
    """Build the context-augmented prompt."""
    return f"Content from {url}:\n\n{content}\n\n{user_prompt}"
