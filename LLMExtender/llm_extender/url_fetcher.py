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
_MAX_REDIRECTS = 10
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})


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
# Lazy Playwright imports (optional dependency)
# ---------------------------------------------------------------------------

_PLAYWRIGHT_INSTALL_MSG = (
    "Playwright is required for render_js=True. "
    "Install it with: pip install llm-extender[browser] "
    "&& playwright install chromium"
)


def _import_sync_playwright():
    """Lazy-import sync_playwright; raises ImportError if missing."""
    from playwright.sync_api import sync_playwright  # noqa: WPS433
    return sync_playwright


def _import_async_playwright():
    """Lazy-import async_playwright; raises ImportError if missing."""
    from playwright.async_api import async_playwright  # noqa: WPS433
    return async_playwright


# Module-level names that tests can patch to inject mocked Playwright.
# When ``None``, the real lazy import is used.
sync_playwright = None
async_playwright = None


def _get_sync_playwright():
    """Return the sync Playwright launcher (patchable or real)."""
    if sync_playwright is not None:
        return sync_playwright
    return _import_sync_playwright()


def _get_async_playwright():
    """Return the async Playwright launcher (patchable or real)."""
    if async_playwright is not None:
        return async_playwright
    return _import_async_playwright()


def _fetch_with_browser(
    url: str,
    *,
    auth: AuthStrategy | None = None,
    timeout: float = 30.0,
    max_length: int = _DEFAULT_MAX_LENGTH,
) -> str:
    """Fetch a URL using a headless Chromium browser (sync)."""
    try:
        launcher = _get_sync_playwright()
    except ImportError:
        raise ProviderError(_PLAYWRIGHT_INSTALL_MSG) from None

    timeout_ms = timeout * 1000
    extra_headers: dict[str, str] = {}
    if auth is not None:
        extra_headers["Authorization"] = f"Bearer {auth.resolve()}"

    browser = None
    try:
        with launcher() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx_kwargs: dict = {}
            if extra_headers:
                ctx_kwargs["extra_http_headers"] = extra_headers
            context = browser.new_context(**ctx_kwargs)
            page = context.new_page()
            page.goto(url, timeout=timeout_ms)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            text = page.inner_text("body")
    except ProviderError:
        raise
    except Exception as exc:
        raise ProviderError(
            f"Browser fetch failed for '{url}': {exc}"
        ) from exc
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:  # noqa: BLE001
                pass  # Already closed by context manager

    if len(text) > max_length:
        text = text[:max_length]
    return text


async def _afetch_with_browser(
    url: str,
    *,
    auth: AuthStrategy | None = None,
    timeout: float = 30.0,
    max_length: int = _DEFAULT_MAX_LENGTH,
) -> str:
    """Fetch a URL using a headless Chromium browser (async)."""
    try:
        launcher = _get_async_playwright()
    except ImportError:
        raise ProviderError(_PLAYWRIGHT_INSTALL_MSG) from None

    timeout_ms = timeout * 1000
    extra_headers: dict[str, str] = {}
    if auth is not None:
        extra_headers["Authorization"] = f"Bearer {await auth.aresolve()}"

    browser = None
    try:
        async with launcher() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx_kwargs: dict = {}
            if extra_headers:
                ctx_kwargs["extra_http_headers"] = extra_headers
            context = await browser.new_context(**ctx_kwargs)
            page = await context.new_page()
            await page.goto(url, timeout=timeout_ms)
            await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            text = await page.inner_text("body")
    except ProviderError:
        raise
    except Exception as exc:
        raise ProviderError(
            f"Browser fetch failed for '{url}': {exc}"
        ) from exc
    finally:
        if browser is not None:
            try:
                await browser.close()
            except Exception:  # noqa: BLE001
                pass  # Already closed by context manager

    if len(text) > max_length:
        text = text[:max_length]
    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_url(
    url: str,
    *,
    auth: AuthStrategy | None = None,
    timeout: float = 30.0,
    max_length: int = _DEFAULT_MAX_LENGTH,
    render_js: bool = False,
) -> str:
    """Fetch a URL and return its text content (HTML stripped).

    Args:
        url: The URL to fetch.
        auth: Optional auth strategy. If provided, the resolved token is
            sent as a ``Authorization: Bearer <token>`` header.
        timeout: HTTP timeout in seconds.
        max_length: Maximum character length of the returned text.
            Content is truncated if it exceeds this limit.
        render_js: If ``True``, use a headless Chromium browser
            (via Playwright) to render JavaScript before extracting
            text.  Requires ``pip install llm-extender[browser]``.

    Returns:
        The extracted text content from the page.

    Raises:
        ProviderError: If the HTTP request fails (non-2xx status)
            or if Playwright is not installed when ``render_js=True``.
    """
    if render_js:
        return _fetch_with_browser(
            url, auth=auth, timeout=timeout, max_length=max_length
        )

    headers: dict[str, str] = {"User-Agent": _USER_AGENT}
    if auth is not None:
        headers["Authorization"] = f"Bearer {auth.resolve()}"

    with httpx.Client(timeout=httpx.Timeout(timeout), follow_redirects=False) as client:
        target = url
        for _ in range(_MAX_REDIRECTS):
            response = client.get(target, headers=headers)
            if response.status_code in _REDIRECT_STATUSES:
                target = str(response.url.join(response.headers["location"]))
                continue
            break
        else:
            raise ProviderError(
                f"Too many redirects while fetching '{url}'"
            )

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
    render_js: bool = False,
) -> str:
    """Fetch a URL asynchronously and return its text content (HTML stripped).

    Args:
        url: The URL to fetch.
        auth: Optional auth strategy. If provided, the resolved token is
            sent as a ``Authorization: Bearer <token>`` header. Uses
            ``aresolve()`` for async credential resolution.
        timeout: HTTP timeout in seconds.
        max_length: Maximum character length of the returned text.
        render_js: If ``True``, use a headless Chromium browser
            (via Playwright) to render JavaScript before extracting
            text.  Requires ``pip install llm-extender[browser]``.

    Returns:
        The extracted text content from the page.

    Raises:
        ProviderError: If the HTTP request fails (non-2xx status)
            or if Playwright is not installed when ``render_js=True``.
    """
    if render_js:
        return await _afetch_with_browser(
            url, auth=auth, timeout=timeout, max_length=max_length
        )

    headers: dict[str, str] = {"User-Agent": _USER_AGENT}
    if auth is not None:
        headers["Authorization"] = f"Bearer {await auth.aresolve()}"

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(timeout), follow_redirects=False
    ) as client:
        target = url
        for _ in range(_MAX_REDIRECTS):
            response = await client.get(target, headers=headers)
            if response.status_code in _REDIRECT_STATUSES:
                target = str(response.url.join(response.headers["location"]))
                continue
            break
        else:
            raise ProviderError(
                f"Too many redirects while fetching '{url}'"
            )

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
