"""Golazo Update tool — check for and install updates from Azure Artifacts.

Provides two actions:
  * check  — report installed vs. latest versions
  * install — install a specific version after pre-flight validation
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import re
import subprocess
import sys
import urllib.request
from html.parser import HTMLParser
from typing import Any

from packaging.version import InvalidVersion, Version

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FEED_URL = (
    "https://msazure.pkgs.visualstudio.com/One/_packaging/"
    "azinsights_accia_pkgs/pypi/simple/golazo-copilot/"
)
FEED_INDEX_URL = (
    "https://msazure.pkgs.visualstudio.com/One/_packaging/"
    "azinsights_accia_pkgs/pypi/simple/"
)

# Regex to pull a version string from a PEP 503 filename anchor.
# Matches both dash-separated (sdist) and underscore-separated (wheel) names.
# Uses a lookahead to stop before file extensions (.tar.gz, .whl, .zip, etc.)
VERSION_RE = re.compile(r"golazo[_-]copilot-(\d+\.\d+\.\d+(?:[a-zA-Z0-9.]*[a-zA-Z0-9])?)(?:\.tar|\.whl|\.zip|-py)")

# Only allow safe characters in the user-provided version string.
_SAFE_VERSION_RE = re.compile(r"^[a-zA-Z0-9.\-]+$")
_PIP_VERSIONS_RE = re.compile(r"Available versions:\s*(.+)", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class _AnchorParser(HTMLParser):
    """Minimal HTML parser that collects href values from <a> tags."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value)


def _parse_versions(html: str) -> list[Version]:
    """Extract and deduplicate version objects from Simple API HTML."""
    parser = _AnchorParser()
    parser.feed(html)
    seen: set[str] = set()
    versions: list[Version] = []
    for href in parser.hrefs:
        m = VERSION_RE.search(href)
        if not m:
            continue
        raw = m.group(1)
        if raw in seen:
            continue
        seen.add(raw)
        try:
            versions.append(Version(raw))
        except InvalidVersion:
            continue  # skip unparseable versions (TC-29)
    return versions


def _classify(versions: list[Version]) -> tuple[Version | None, Version | None]:
    """Return (latest_stable, latest_prerelease) from a list of versions."""
    stable = sorted([v for v in versions if not v.is_prerelease], reverse=True)
    pre = sorted([v for v in versions if v.is_prerelease], reverse=True)
    return (stable[0] if stable else None), (pre[0] if pre else None)


def _build_check_result(current: str, versions: list[Version]) -> dict[str, Any]:
    """Build a standardized check result from parsed version objects."""
    latest_stable, latest_pre = _classify(versions)
    latest_stable_str = str(latest_stable) if latest_stable else None
    latest_pre_str = str(latest_pre) if latest_pre else None

    try:
        current_v = Version(current)
    except InvalidVersion:
        current_v = None

    update_available = False
    if current_v and latest_stable:
        update_available = latest_stable > current_v

    return {
        "status": "ok",
        "action": "check",
        "current_version": current,
        "latest_stable": latest_stable_str,
        "latest_prerelease": latest_pre_str,
        "update_available": update_available,
    }


def _get_versions_from_pip_index() -> list[Version] | None:
    """Get package versions via pip index (authenticated via keyring/plugins).

    Returns a list of parsed versions, or None if the query fails.
    """
    base_args = [
        "-m",
        "pip",
        "index",
        "versions",
        "golazo-copilot",
        f"--index-url={FEED_INDEX_URL}",
    ]

    commands = [
        [sys.executable, *base_args],
        ["py", "-3.14", *base_args],
        ["python", *base_args],
    ]

    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

        if result.returncode != 0:
            continue

        stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
        match = _PIP_VERSIONS_RE.search(stdout)
        if not match:
            continue

        versions: list[Version] = []
        for raw in [v.strip() for v in match.group(1).split(",") if v.strip()]:
            try:
                versions.append(Version(raw))
            except InvalidVersion:
                continue

        if versions:
            return versions

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def golazo_update(
    action: str,
    version: str | None = None,
    workspace_path: str | None = None,
) -> dict[str, Any]:
    """Check for or install updates to golazo-copilot.

    Parameters
    ----------
    action : str
        ``"check"`` to report version info, ``"install"`` to install a
        specific version.
    version : str | None
        Target version (required when *action* is ``"install"``).
    workspace_path : str | None
        Workspace root path (required).

    Returns
    -------
    dict
        Structured result dict consumed by ``format_update_result`` in
        ``server.py``.
    """
    if action == "check":
        return await _action_check()
    elif action == "install":
        return await _action_install(version, workspace_path)
    else:
        return {"status": "error", "action": action, "error": f"Unknown action: {action}"}


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

async def _action_check() -> dict[str, Any]:
    """Query the feed and compare with the installed version."""
    # Installed version
    try:
        current = importlib.metadata.version("golazo-copilot")
    except importlib.metadata.PackageNotFoundError:
        return {
            "status": "error",
            "action": "check",
            "error": (
                "golazo-copilot is not installed in the current Python environment. "
                "Install it with: pip install golazo-copilot --index-url=" + FEED_URL
            ),
        }

    # Fetch feed
    try:
        with urllib.request.urlopen(FEED_URL, timeout=10) as resp:
            html = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        code = exc.code
        if code in (401, 403):
            fallback_versions = _get_versions_from_pip_index()
            if fallback_versions:
                return _build_check_result(current, fallback_versions)
        hint = ""
        if code in (401, 403):
            hint = " Ensure you are authenticated — try running `az login`."
        return {
            "status": "error",
            "action": "check",
            "error": f"Azure Artifacts feed returned HTTP {code}.{hint}",
        }
    except (urllib.error.URLError, OSError) as exc:
        return {
            "status": "error",
            "action": "check",
            "error": f"Unable to reach Azure Artifacts feed: {exc}",
        }

    # Parse
    versions = _parse_versions(html)
    if not versions:
        return {
            "status": "error",
            "action": "check",
            "error": "No versions found on the Azure Artifacts feed. The HTML may be malformed.",
        }

    return _build_check_result(current, versions)


# ---------------------------------------------------------------------------
# install — helpers
# ---------------------------------------------------------------------------

def _install_error(error: str, **kwargs: Any) -> dict[str, Any]:
    """Build a standardised install-action error dict."""
    return {"status": "error", "action": "install", "error": error, **kwargs}


def _validate_install_version(version: str | None) -> dict[str, Any] | None:
    """Return an error dict if *version* is missing or unsafe, else ``None``."""
    if not version:
        return _install_error("version parameter is required for action=install")
    if not _SAFE_VERSION_RE.match(version):
        return _install_error(
            f"Invalid version string: '{version}'. "
            "Only alphanumeric characters, dots, and dashes are allowed."
        )
    return None


def _check_auth_prerequisites() -> dict[str, Any] | None:
    """Verify keyring, artifacts-keyring, and ``az login``.

    Returns an error dict on the first failing check, or ``None`` when all
    prerequisites are satisfied.
    """
    if importlib.util.find_spec("keyring") is None:
        return _install_error(
            "keyring is not installed. It is required for Azure Artifacts auth. "
            "Install it with: pip install keyring"
        )

    if importlib.util.find_spec("artifacts_keyring") is None:
        return _install_error(
            "artifacts-keyring is not installed. It is required for Azure Artifacts auth. "
            "Install it with: pip install artifacts-keyring"
        )

    try:
        az_result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            timeout=10,
        )
        if az_result.returncode != 0:
            return _install_error(
                "Azure CLI is not logged in. Run `az login` before installing "
                "from Azure Artifacts."
            )
    except FileNotFoundError:
        return _install_error(
            "Azure CLI (az) is not installed or not on PATH. "
            "Install it from https://aka.ms/installazurecliwindows "
            "or ensure it is on your PATH."
        )
    except subprocess.TimeoutExpired:
        return _install_error(
            "Azure CLI timed out checking login status. "
            "Try running `az account show` manually."
        )

    return None


def _run_pip_install(version: str) -> dict[str, Any]:
    """Execute ``pip install golazo-copilot==<version>`` and return a result dict."""
    pip_cmd = [
        sys.executable, "-m", "pip", "install",
        f"golazo-copilot=={version}",
        f"--index-url={FEED_URL}",
    ]

    try:
        pip_result = subprocess.run(pip_cmd, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return _install_error("pip install timed out after 300 seconds.")

    if pip_result.returncode != 0:
        stderr_text = (
            pip_result.stderr.decode("utf-8", errors="replace")
            if pip_result.stderr else ""
        )
        return _install_error(
            f"pip install failed (exit code {pip_result.returncode})",
            stderr=stderr_text,
        )

    return {
        "status": "ok",
        "action": "install",
        "installed_version": version,
        "restart_required": True,
        "restart_message": (
            "The MCP server must be refreshed/restarted before the new version "
            "takes effect. Bootstrap will not work until you refresh."
        ),
        "bootstrap_options": [
            "Do not bootstrap",
            "Bootstrap",
            "Full clean bootstrap",
        ],
    }


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

async def _action_install(version: str | None, workspace_path: str | None) -> dict[str, Any]:
    """Validate pre-requisites and install the requested version."""
    err = _validate_install_version(version)
    if err:
        return err

    err = _check_auth_prerequisites()
    if err:
        return err

    return _run_pip_install(version)  # type: ignore[arg-type]
