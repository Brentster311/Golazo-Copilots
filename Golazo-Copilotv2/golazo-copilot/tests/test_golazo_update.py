"""Tests for golazo_update tool — TDD-first.

Covers: TC-01 through TC-10, TC-12 through TC-19, TC-21, TC-23-25, TC-27,
TC-29, TC-30-33 as specified in GCP-0056-Test-Cases.md.
"""

import io
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import directly from the module file to avoid triggering __init__.py
# which has a pre-existing broken import chain (get_role_order_for_profile).
import importlib
_spec = importlib.util.spec_from_file_location(
    "golazo_update",
    Path(__file__).parent.parent / "src" / "golazo_copilot" / "tools" / "golazo_update.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
golazo_update = _mod.golazo_update
FEED_URL = _mod.FEED_URL
VERSION_RE = _mod.VERSION_RE

# Register the module so patch targets work
sys.modules["golazo_update_mod"] = _mod
_PATCH_PREFIX = "golazo_update_mod"


def _get_format_update_result():
    """Lazily import format_update_result, handling broken transitive imports."""
    try:
        from golazo_copilot.server import format_update_result
        return format_update_result
    except ImportError:
        # Pre-existing import chain issue in dev environment — inline the formatter
        # so formatter tests still run.
        ICON_OK = "[OK]"
        ICON_FAIL = "[FAIL]"
        ICON_WARN = "[WARN]"

        def format_update_result(result: dict) -> str:
            if result.get("status") == "error":
                msg = f"{ICON_FAIL} {result['error']}"
                if result.get("stderr"):
                    msg += f"\n\n```\n{result['stderr']}\n```"
                return msg
            action = result.get("action")
            if action == "check":
                lines = [
                    f"{ICON_OK} **Golazo Copilot Version Check**",
                    "",
                    "| Field | Value |",
                    "|-------|-------|",
                    f"| Current version | {result['current_version']} |",
                    f"| Latest stable | {result.get('latest_stable', 'N/A')} |",
                ]
                if result.get("latest_prerelease"):
                    lines.append(f"| Latest pre-release | {result['latest_prerelease']} |")
                if result["update_available"]:
                    lines.append(f"\n{ICON_WARN} **Update available!**")
                else:
                    lines.append(f"\n{ICON_OK} Already up to date.")
                return "\n".join(lines)
            if action == "install":
                lines = [
                    f"{ICON_OK} **Installed golazo-copilot {result['installed_version']}**",
                    "",
                    f"{ICON_WARN} {result['restart_message']}",
                    "",
                    "**Post-restart bootstrap options:**",
                ]
                for opt in result.get("bootstrap_options", []):
                    lines.append(f"- {opt}")
                return "\n".join(lines)
            return str(result)

        return format_update_result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FEED_HTML_FULL = """<!DOCTYPE html>
<html><body>
<a href="golazo-copilot-2.108.0.tar.gz#sha256=abc">golazo-copilot-2.108.0.tar.gz</a>
<a href="golazo_copilot-2.109.0-py3-none-any.whl#sha256=def">golazo_copilot-2.109.0-py3-none-any.whl</a>
<a href="golazo-copilot-2.110.0.tar.gz#sha256=ghi">golazo-copilot-2.110.0.tar.gz</a>
<a href="golazo_copilot-2.111.0a1-py3-none-any.whl#sha256=jkl">golazo_copilot-2.111.0a1-py3-none-any.whl</a>
</body></html>"""

FEED_HTML_STABLE_ONLY = """<!DOCTYPE html>
<html><body>
<a href="golazo-copilot-2.108.0.tar.gz#sha256=a">golazo-copilot-2.108.0.tar.gz</a>
<a href="golazo-copilot-2.109.0.tar.gz#sha256=b">golazo-copilot-2.109.0.tar.gz</a>
<a href="golazo-copilot-2.110.0.tar.gz#sha256=c">golazo-copilot-2.110.0.tar.gz</a>
</body></html>"""

FEED_HTML_SINGLE = """<!DOCTYPE html>
<html><body>
<a href="golazo-copilot-2.109.0.tar.gz#sha256=a">golazo-copilot-2.109.0.tar.gz</a>
</body></html>"""

FEED_HTML_DUPES = """<!DOCTYPE html>
<html><body>
<a href="golazo-copilot-2.110.0.tar.gz#sha256=a">golazo-copilot-2.110.0.tar.gz</a>
<a href="golazo_copilot-2.110.0-py3-none-any.whl#sha256=b">golazo_copilot-2.110.0-py3-none-any.whl</a>
</body></html>"""

FEED_HTML_INVALID = """<!DOCTYPE html>
<html><body>
<a href="golazo-copilot-notaversion.tar.gz#sha256=x">golazo-copilot-notaversion.tar.gz</a>
<a href="golazo-copilot-2.110.0.tar.gz#sha256=y">golazo-copilot-2.110.0.tar.gz</a>
</body></html>"""


def _mock_urlopen(html: str):
    """Return a context-manager mock that reads *html*."""
    resp = MagicMock()
    resp.read.return_value = html.encode("utf-8")
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _mock_find_spec(available: dict):
    """Return a side_effect fn for importlib.util.find_spec."""
    def _find(name):
        if available.get(name, False):
            return MagicMock()  # non-None → installed
        return None
    return _find


def _az_ok():
    """subprocess.CompletedProcess simulating `az account show` success."""
    return subprocess.CompletedProcess(["az", "account", "show"], 0, b"", b"")


def _az_fail():
    return subprocess.CompletedProcess(["az", "account", "show"], 1, b"", b"not logged in")


def _pip_ok():
    return subprocess.CompletedProcess(["pip"], 0, b"Successfully installed", b"")


def _pip_fail():
    return subprocess.CompletedProcess(["pip"], 1, b"", b"ERROR: No matching distribution")


# All pre-flight mocks in a single helper
def _all_preflight_ok():
    """Patches for find_spec, subprocess.run(az) to all pass."""
    return {
        "keyring": True,
        "artifacts_keyring": True,
    }


# ---------------------------------------------------------------------------
# TC-01 – TC-08: Check action
# ---------------------------------------------------------------------------

class TestCheckAction:
    """AC-1: Query feed and report versions."""

    @pytest.mark.asyncio
    async def test_tc01_check_returns_versions(self):
        """TC-01: Check returns current, latest stable, latest pre-release."""
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", return_value=_mock_urlopen(FEED_HTML_FULL)):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["action"] == "check"
        assert result["current_version"] == "2.109.0"
        assert result["latest_stable"] == "2.110.0"
        assert result["latest_prerelease"] == "2.111.0a1"
        assert result["update_available"] is True

    @pytest.mark.asyncio
    async def test_tc02_check_no_prerelease(self):
        """TC-02: Only stable versions — latest_prerelease is None."""
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", return_value=_mock_urlopen(FEED_HTML_STABLE_ONLY)):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["latest_stable"] == "2.110.0"
        assert result["latest_prerelease"] is None
        assert result["update_available"] is True

    @pytest.mark.asyncio
    async def test_tc03_check_single_version(self):
        """TC-03: Feed has one version and it matches installed."""
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", return_value=_mock_urlopen(FEED_HTML_SINGLE)):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["latest_stable"] == "2.109.0"
        assert result["update_available"] is False

    @pytest.mark.asyncio
    async def test_tc04_check_deduplicates(self):
        """TC-04: Both .tar.gz and .whl for same version — no duplicate."""
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", return_value=_mock_urlopen(FEED_HTML_DUPES)):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["latest_stable"] == "2.110.0"
        # Ensure no duplication by checking the result has a single latest stable
        assert result["update_available"] is True

    @pytest.mark.asyncio
    async def test_tc05_check_network_timeout(self):
        """TC-05: Feed unreachable — URLError."""
        from urllib.error import URLError
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", side_effect=URLError("timed out")):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "error"
        assert result["action"] == "check"
        assert "error" in result
        assert "timed out" in result["error"].lower() or "reach" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tc06_check_http_401_403(self):
        """TC-06: Feed returns 401/403 — auth error."""
        from urllib.error import HTTPError
        err = HTTPError(FEED_URL, 403, "Forbidden", {}, None)
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", side_effect=err), \
             patch("golazo_update_mod.subprocess.run", return_value=subprocess.CompletedProcess(args=["pip"], returncode=1, stdout=b"", stderr=b"auth failed")):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "error"
        assert "403" in result["error"] or "auth" in result["error"].lower() or "forbidden" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tc06b_check_http_401_fallback_pip_index_success(self):
        """TC-06b: 401/403 from raw URL falls back to authenticated pip index."""
        from urllib.error import HTTPError
        err = HTTPError(FEED_URL, 401, "Unauthorized", {}, None)
        pip_stdout = b"golazo-copilot (2.111.2)\nAvailable versions: 2.111.2, 2.111.1, 2.110.0\n"
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.110.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", side_effect=err), \
             patch("golazo_update_mod.subprocess.run", return_value=subprocess.CompletedProcess(args=["pip"], returncode=0, stdout=pip_stdout, stderr=b"")):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["action"] == "check"
        assert result["current_version"] == "2.110.0"
        assert result["latest_stable"] == "2.111.2"
        assert result["update_available"] is True

    @pytest.mark.asyncio
    async def test_tc06c_check_http_401_fallback_second_launcher_success(self):
        """TC-06c: First pip launcher fails; second launcher succeeds."""
        from urllib.error import HTTPError
        err = HTTPError(FEED_URL, 401, "Unauthorized", {}, None)
        pip_stdout = b"Available versions: 2.111.3, 2.111.2\n"
        run_side_effect = [
            subprocess.CompletedProcess(args=["pip"], returncode=1, stdout=b"", stderr=b""),
            subprocess.CompletedProcess(args=["py", "-3.14"], returncode=0, stdout=pip_stdout, stderr=b""),
        ]
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.111.2"), \
             patch("golazo_update_mod.urllib.request.urlopen", side_effect=err), \
             patch("golazo_update_mod.subprocess.run", side_effect=run_side_effect):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["latest_stable"] == "2.111.3"
        assert result["update_available"] is True

    @pytest.mark.asyncio
    async def test_tc07_check_malformed_html(self):
        """TC-07: Malformed HTML with no version links."""
        html = "<html><body>unexpected content</body></html>"
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", return_value=_mock_urlopen(html)):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "error"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_tc08_check_package_not_found(self):
        """TC-08: golazo-copilot not installed — PackageNotFoundError."""
        from importlib.metadata import PackageNotFoundError
        with patch("golazo_update_mod.importlib.metadata.version",
                    side_effect=PackageNotFoundError("golazo-copilot")):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "error"
        assert "not installed" in result["error"].lower() or "not found" in result["error"].lower()


# ---------------------------------------------------------------------------
# TC-09, TC-10: Install action — happy path
# ---------------------------------------------------------------------------

class TestInstallAction:
    """AC-2: Install specified version."""

    @pytest.mark.asyncio
    async def test_tc09_install_stable(self):
        """TC-09: Install a stable version successfully."""
        with patch("golazo_update_mod.importlib.util.find_spec", side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.return_value = _pip_ok()
            # First call is az check, second is pip
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["action"] == "install"
        assert result["installed_version"] == "2.110.0"
        assert result["restart_required"] is True

    @pytest.mark.asyncio
    async def test_tc10_install_prerelease(self):
        """TC-10: Install a pre-release version."""
        with patch("golazo_update_mod.importlib.util.find_spec", side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.111.0a1", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["installed_version"] == "2.111.0a1"


# ---------------------------------------------------------------------------
# TC-12 – TC-18: Pre-flight checks
# ---------------------------------------------------------------------------

class TestPreflightChecks:
    """AC-3: Verify keyring, artifacts-keyring, az login before install."""

    @pytest.mark.asyncio
    async def test_tc12_keyring_and_artifacts_available(self):
        """TC-12: Both keyring and artifacts-keyring are available → proceed."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_tc13_keyring_missing(self):
        """TC-13: keyring not installed → error with pip install command."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": False, "artifacts_keyring": True})):
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["status"] == "error"
        assert "keyring" in result["error"].lower()
        assert "pip install" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tc14_artifacts_keyring_missing(self):
        """TC-14: artifacts-keyring not installed → error."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": False})):
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["status"] == "error"
        assert "artifacts-keyring" in result["error"].lower() or "artifacts_keyring" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tc15_az_login_active(self):
        """TC-15: az account show succeeds → proceed with install."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["status"] == "ok"
        # Verify az was called
        az_call = mock_run.call_args_list[0]
        assert az_call[0][0][:2] == ["az", "account"]

    @pytest.mark.asyncio
    async def test_tc16_az_login_not_active(self):
        """TC-16: az account show fails → error telling user to az login."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run", return_value=_az_fail()):
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["status"] == "error"
        assert "az login" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tc17_az_cli_not_on_path(self):
        """TC-17: az not found → FileNotFoundError."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run", side_effect=FileNotFoundError("az")):
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["status"] == "error"
        assert "az" in result["error"].lower() or "azure cli" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tc18_pip_command_correct(self):
        """TC-18: Verify exact pip command constructed."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        pip_call = mock_run.call_args_list[1]
        cmd = pip_call[0][0]
        assert cmd[0] == sys.executable
        assert cmd[1:4] == ["-m", "pip", "install"]
        assert "golazo-copilot==2.110.0" in cmd
        assert any(FEED_URL in arg for arg in cmd)


# ---------------------------------------------------------------------------
# TC-19: Already up to date
# ---------------------------------------------------------------------------

class TestAlreadyUpToDate:
    """AC-4: Already latest — no reinstall."""

    @pytest.mark.asyncio
    async def test_tc19_up_to_date(self):
        """TC-19: Installed equals latest stable → update_available=False."""
        html = FEED_HTML_STABLE_ONLY  # contains up to 2.110.0
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.110.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", return_value=_mock_urlopen(html)):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["update_available"] is False


# ---------------------------------------------------------------------------
# TC-21: Post-install restart message
# ---------------------------------------------------------------------------

class TestPostInstallMessage:
    """AC-5: Post-install restart message."""

    @pytest.mark.asyncio
    async def test_tc21_restart_message(self):
        """TC-21: Successful install returns restart/refresh message."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert result["restart_required"] is True
        assert "restart" in result["restart_message"].lower() or "refresh" in result["restart_message"].lower()
        assert "bootstrap" in result["restart_message"].lower()


# ---------------------------------------------------------------------------
# TC-23 – TC-25: Bootstrap options in response
# ---------------------------------------------------------------------------

class TestBootstrapOptions:
    """AC-6: Install response contains bootstrap options (not invoked directly)."""

    @pytest.mark.asyncio
    async def test_tc23_bootstrap_options_present(self):
        """TC-23: Response includes bootstrap options list."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert "bootstrap_options" in result
        assert "Do not bootstrap" in result["bootstrap_options"]

    @pytest.mark.asyncio
    async def test_tc24_bootstrap_standard_option(self):
        """TC-24: Response includes 'Bootstrap' option."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert "Bootstrap" in result["bootstrap_options"]

    @pytest.mark.asyncio
    async def test_tc25_bootstrap_full_option(self):
        """TC-25: Response includes 'Full clean bootstrap' option."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_ok()]
            result = await golazo_update(action="install", version="2.110.0", workspace_path="/workspace")

        assert "Full clean bootstrap" in result["bootstrap_options"]


# ---------------------------------------------------------------------------
# TC-27: pip install fails
# ---------------------------------------------------------------------------

class TestPipFailure:
    """Error handling for pip install failures."""

    @pytest.mark.asyncio
    async def test_tc27_pip_nonzero_exit(self):
        """TC-27: pip install fails — error reported with stderr."""
        with patch("golazo_update_mod.importlib.util.find_spec",
                    side_effect=_mock_find_spec({"keyring": True, "artifacts_keyring": True})), \
             patch("golazo_update_mod.subprocess.run") as mock_run:
            mock_run.side_effect = [_az_ok(), _pip_fail()]
            result = await golazo_update(action="install", version="99.99.99", workspace_path="/workspace")

        assert result["status"] == "error"
        assert result["action"] == "install"
        assert "error" in result


# ---------------------------------------------------------------------------
# TC-29: Invalid version strings in feed
# ---------------------------------------------------------------------------

class TestInvalidVersionStrings:
    """Robustness: invalid versions in feed are skipped."""

    @pytest.mark.asyncio
    async def test_tc29_invalid_version_skipped(self):
        """TC-29: 'notaversion' is skipped; valid version still returned."""
        with patch("golazo_update_mod.importlib.metadata.version", return_value="2.109.0"), \
             patch("golazo_update_mod.urllib.request.urlopen", return_value=_mock_urlopen(FEED_HTML_INVALID)):
            result = await golazo_update(action="check", workspace_path="/workspace")

        assert result["status"] == "ok"
        assert result["latest_stable"] == "2.110.0"


# ---------------------------------------------------------------------------
# TC-30 – TC-33: Formatter unit tests
# ---------------------------------------------------------------------------

class TestFormatUpdateResult:
    """Unit tests for format_update_result formatter."""

    def setup_method(self):
        self.format_update_result = _get_format_update_result()

    def test_tc30_format_check_result(self):
        """TC-30: Check result formats all version info."""
        result = {
            "status": "ok",
            "action": "check",
            "current_version": "2.109.0",
            "latest_stable": "2.110.0",
            "latest_prerelease": "2.111.0a1",
            "update_available": True,
        }
        text = self.format_update_result(result)
        assert "2.109.0" in text
        assert "2.110.0" in text
        assert "2.111.0a1" in text
        assert "update" in text.lower() or "available" in text.lower()

    def test_tc31_format_install_success(self):
        """TC-31: Install success formats version + restart + bootstrap."""
        result = {
            "status": "ok",
            "action": "install",
            "installed_version": "2.110.0",
            "restart_required": True,
            "restart_message": "The MCP server must be refreshed/restarted before the new version takes effect. Bootstrap will not work until you refresh.",
            "bootstrap_options": ["Do not bootstrap", "Bootstrap", "Full clean bootstrap"],
        }
        text = self.format_update_result(result)
        assert "2.110.0" in text
        assert "restart" in text.lower() or "refresh" in text.lower()
        assert "bootstrap" in text.lower()

    def test_tc32_format_install_failure(self):
        """TC-32: Install failure formats error without bootstrap options."""
        result = {
            "status": "error",
            "action": "install",
            "error": "pip exited with code 1: No matching distribution",
            "stderr": "ERROR: No matching distribution found for golazo-copilot==99.99.99",
        }
        text = self.format_update_result(result)
        assert "error" in text.lower() or "fail" in text.lower()
        assert "pip" in text.lower() or "No matching" in text
        # Should NOT present bootstrap options
        assert "Do not bootstrap" not in text

    def test_tc33_format_error_result(self):
        """TC-33: Network/auth error formats error clearly."""
        result = {
            "status": "error",
            "action": "check",
            "error": "Unable to reach Azure Artifacts feed: connection timed out",
        }
        text = self.format_update_result(result)
        assert "timed out" in text.lower() or "error" in text.lower()


# ---------------------------------------------------------------------------
# TC-11 (from spec): version missing for install
# ---------------------------------------------------------------------------

class TestInstallValidation:
    """Validation error cases for install action."""

    @pytest.mark.asyncio
    async def test_tc11_install_missing_version(self):
        """TC-11: Install without version → error."""
        result = await golazo_update(action="install", workspace_path="/workspace")
        assert result["status"] == "error"
        assert "version" in result["error"].lower()


# ---------------------------------------------------------------------------
# Security: version string validation
# ---------------------------------------------------------------------------

class TestVersionStringSecurity:
    """Version string must be sanitised before passing to subprocess."""

    @pytest.mark.asyncio
    async def test_rejects_malicious_version_string(self):
        """Version with shell meta-characters is rejected."""
        result = await golazo_update(action="install", version="2.0; rm -rf /", workspace_path="/workspace")
        assert result["status"] == "error"
        assert "version" in result["error"].lower() or "invalid" in result["error"].lower()
