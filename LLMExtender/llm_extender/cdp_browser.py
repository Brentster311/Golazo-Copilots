"""CDP browser integration for fetching from Conditional Access–protected sites.

Connects Playwright to the user's real Edge browser via Chrome DevTools
Protocol (CDP), enabling content fetching from sites that require device
compliance (Conditional Access policies 530033 / 53000).

Windows-only in this iteration — Edge paths are platform-specific.

Requires ``playwright`` (included in the ``[browser]`` optional dependency).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from llm_extender.auth.aad_browser import (
    detect_aad_redirect,
    wait_for_aad_login,
)
from llm_extender.exceptions import ProviderError

if TYPE_CHECKING:
    from llm_extender.auth.aad_browser import await_for_aad_login  # noqa: F401

_DEFAULT_CDP_PORT = 9222
_DEFAULT_LOGIN_TIMEOUT = 120.0
_DEFAULT_MAX_LENGTH = 50_000

# Known Edge install locations on Windows
_EDGE_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

_EDGE_NOT_FOUND_MSG = (
    "Microsoft Edge not found. browser_auth='cdp' requires Edge installed "
    "on Windows. Searched: shutil.which('msedge'), "
    + ", ".join(str(p) for p in _EDGE_PATHS)
)

_CDP_CONNECT_MSG = (
    "Could not connect to Edge via CDP on port {port}. "
    "Make sure Edge launched successfully and is not blocking remote debugging. "
    "Error: {error}"
)


# ---------------------------------------------------------------------------
# Lazy Playwright imports (re-use the same pattern as url_fetcher.py)
# ---------------------------------------------------------------------------

def _get_sync_playwright():
    """Return the sync Playwright launcher."""
    from playwright.sync_api import sync_playwright  # noqa: WPS433
    return sync_playwright


def _get_async_playwright():
    """Return the async Playwright launcher."""
    from playwright.async_api import async_playwright  # noqa: WPS433
    return async_playwright


# ---------------------------------------------------------------------------
# Edge discovery helpers
# ---------------------------------------------------------------------------

def _find_edge_executable() -> Path:
    """Locate the Microsoft Edge executable on Windows.

    Tries ``shutil.which`` first, then falls back to well-known install
    paths.

    Returns:
        Path to the Edge executable.

    Raises:
        ProviderError: If Edge is not found.
    """
    found = shutil.which("msedge")
    if found:
        return Path(found)

    for candidate in _EDGE_PATHS:
        if candidate.exists():
            return candidate

    raise ProviderError(_EDGE_NOT_FOUND_MSG)


def _find_edge_user_data_dir() -> Path:
    """Return the default Edge user-data directory on Windows.

    Returns:
        Path to ``%LOCALAPPDATA%\\Microsoft\\Edge\\User Data``.
    """
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    return Path(local_app_data) / "Microsoft" / "Edge" / "User Data"


# ---------------------------------------------------------------------------
# Edge process management
# ---------------------------------------------------------------------------

def _launch_edge_with_cdp(
    *,
    port: int = _DEFAULT_CDP_PORT,
    url: str | None = None,
) -> subprocess.Popen:
    """Kill existing Edge instances and relaunch with CDP enabled.

    Edge ignores ``--remote-debugging-port`` when already running, so
    existing instances must be closed first. ``--restore-last-session``
    ensures the user's tabs are preserved.

    Args:
        port: The CDP port to use.
        url: Optional URL to open on launch.

    Returns:
        The Popen handle for the Edge process.
    """
    # Kill existing Edge instances
    print(
        "Closing existing Edge instances (they will be restored)...",
        file=sys.stderr,
        flush=True,
    )
    subprocess.run(
        ["taskkill", "/F", "/IM", "msedge.exe"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)

    edge_path = _find_edge_executable()
    user_data = _find_edge_user_data_dir()

    cmd = [
        str(edge_path),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--restore-last-session",
    ]
    if url:
        cmd.append(url)

    print(
        "Launching Edge with remote debugging...",
        file=sys.stderr,
        flush=True,
    )
    return subprocess.Popen(cmd)


def _wait_for_cdp_ready(port: int = _DEFAULT_CDP_PORT, timeout: float = 15.0) -> None:
    """Poll the CDP endpoint until it responds.

    Args:
        port: The CDP port to check.
        timeout: Maximum seconds to wait.

    Raises:
        ProviderError: If the CDP endpoint doesn't respond within timeout.
    """
    import httpx  # noqa: WPS433

    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/json/version"

    while time.monotonic() < deadline:
        try:
            resp = httpx.get(url, timeout=2.0)
            if resp.status_code == 200:
                return
        except (httpx.ConnectError, httpx.TimeoutException, OSError):
            pass
        time.sleep(0.5)

    raise ProviderError(
        f"Edge CDP endpoint did not become ready on port {port} "
        f"within {timeout}s."
    )


# ---------------------------------------------------------------------------
# CDP fetch (sync)
# ---------------------------------------------------------------------------

def _fetch_with_cdp_browser(
    url: str,
    *,
    timeout: float = 30.0,
    max_length: int = _DEFAULT_MAX_LENGTH,
    cdp_port: int = _DEFAULT_CDP_PORT,
    login_timeout: float = _DEFAULT_LOGIN_TIMEOUT,
) -> str:
    """Fetch a URL via CDP connection to the user's real Edge browser (sync).

    Args:
        url: The URL to fetch.
        timeout: Page load timeout in seconds.
        max_length: Maximum characters to return.
        cdp_port: CDP port for Edge.
        login_timeout: Seconds to wait for AAD login to complete.

    Returns:
        Extracted text from the page body.

    Raises:
        ProviderError: If Edge/CDP connection fails or page fetch fails.
    """
    _launch_edge_with_cdp(port=cdp_port, url=url)
    _wait_for_cdp_ready(port=cdp_port)

    timeout_ms = timeout * 1000

    try:
        launcher = _get_sync_playwright()
    except ImportError:
        raise ProviderError(
            "Playwright is required for browser_auth='cdp'. "
            "Install it with: pip install llm-extender[browser] "
            "&& playwright install chromium"
        ) from None

    try:
        with launcher() as pw:
            browser = pw.chromium.connect_over_cdp(
                f"http://127.0.0.1:{cdp_port}"
            )

            # Find the target tab or use the last page
            page = _find_target_page(browser, url)

            # If on AAD login, wait for user to complete
            if detect_aad_redirect(page.url):
                print(
                    "Waiting for AAD login (sign in if prompted)...",
                    file=sys.stderr,
                    flush=True,
                )
                wait_for_aad_login(page, timeout=login_timeout)

            # Wait for SPA to render
            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:
                pass  # best-effort

            text = page.inner_text("body")

            # Disconnect from CDP — don't close the user's browser
            browser.close()
    except ProviderError:
        raise
    except Exception as exc:
        raise ProviderError(
            _CDP_CONNECT_MSG.format(port=cdp_port, error=exc)
        ) from exc

    if len(text) > max_length:
        text = text[:max_length]
    return text


# ---------------------------------------------------------------------------
# CDP fetch (async)
# ---------------------------------------------------------------------------

async def _afetch_with_cdp_browser(
    url: str,
    *,
    timeout: float = 30.0,
    max_length: int = _DEFAULT_MAX_LENGTH,
    cdp_port: int = _DEFAULT_CDP_PORT,
    login_timeout: float = _DEFAULT_LOGIN_TIMEOUT,
) -> str:
    """Fetch a URL via CDP connection to the user's real Edge browser (async).

    Args:
        url: The URL to fetch.
        timeout: Page load timeout in seconds.
        max_length: Maximum characters to return.
        cdp_port: CDP port for Edge.
        login_timeout: Seconds to wait for AAD login to complete.

    Returns:
        Extracted text from the page body.

    Raises:
        ProviderError: If Edge/CDP connection fails or page fetch fails.
    """
    from llm_extender.auth.aad_browser import (
        await_for_aad_login as _await_for_aad_login,
    )

    # Launch Edge (sync — this is a fire-and-forget process start)
    _launch_edge_with_cdp(port=cdp_port, url=url)
    _wait_for_cdp_ready(port=cdp_port)

    timeout_ms = timeout * 1000

    try:
        launcher = _get_async_playwright()
    except ImportError:
        raise ProviderError(
            "Playwright is required for browser_auth='cdp'. "
            "Install it with: pip install llm-extender[browser] "
            "&& playwright install chromium"
        ) from None

    try:
        async with launcher() as pw:
            browser = await pw.chromium.connect_over_cdp(
                f"http://127.0.0.1:{cdp_port}"
            )

            # Find the target tab or use the last page
            page = _find_target_page(browser, url)

            if detect_aad_redirect(page.url):
                print(
                    "Waiting for AAD login (sign in if prompted)...",
                    file=sys.stderr,
                    flush=True,
                )
                await _await_for_aad_login(page, timeout=login_timeout)

            try:
                await page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:
                pass

            text = await page.inner_text("body")
            await browser.close()
    except ProviderError:
        raise
    except Exception as exc:
        raise ProviderError(
            _CDP_CONNECT_MSG.format(port=cdp_port, error=exc)
        ) from exc

    if len(text) > max_length:
        text = text[:max_length]
    return text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_target_page(browser: Any, target_url: str) -> Any:
    """Find the page matching the target URL, or fall back to the last tab.

    Args:
        browser: The Playwright CDP browser connection.
        target_url: The URL we're trying to fetch.

    Returns:
        A Playwright Page object.

    Raises:
        ProviderError: If no browser tabs are available.
    """
    target_lower = target_url.lower()
    contexts = browser.contexts

    for ctx in contexts:
        for page in ctx.pages:
            if target_lower in page.url.lower():
                return page

    # Fall back to last page in first context
    if contexts and contexts[0].pages:
        return contexts[0].pages[-1]

    raise ProviderError(
        "No browser tabs found in Edge. Make sure Edge launched correctly."
    )
