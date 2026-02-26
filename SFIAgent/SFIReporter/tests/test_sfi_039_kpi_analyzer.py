"""SFI-039: Coverage boost for sfi_reporter.kpi_analyzer (59 % → ≥ 70 %).

Targets the uncovered lines identified in the coverage report:
  202-205, 264-267, 321-367, 376-397, 437-439, 452-463, 536-537, 551,
  559-562, 600-639, 698, 713-739, 752-811, 846, 871, 884-911, 951,
  1067-1096, 1117-1172.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest

from sfi_reporter.kpi_analyzer import (
    AnalysisResult,
    FetchResult,
    _HTMLTextExtractor,
    _copy_edge_profile,
    _discover_relevant_urls,
    _fetch_via_cdp,
    _fetch_via_edge_cdp,
    _fetch_via_urllib,
    _fetch_with_bearer_token,
    _fetch_with_provenance,
    _find_edge_work_profile,
    _get_edge_user_data_dir,
    _is_js_shell,
    _is_login_page,
    _safe_filename,
    _sanitize_text,
    _save_fetched_docs,
    analyze_kpi,
    build_analysis_prompt,
    collect_urls,
    extract_text,
    fetch_url_content,
    format_sources_card,
    truncate_content,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_item(
    item_id="AI-1",
    title="Fix something",
    kpi_id="KPI-A",
    kpi_name="[SFI-NS3.2.1] Secure PaaS",
    url="",
    wiki="",
    remediation="",
    sla="OutOfSla",
):
    return {
        "id": item_id,
        "title": title,
        "_kpi_id": kpi_id,
        "_kpi_name": kpi_name,
        "S360_ServiceTreeServiceName": "My Service",
        "ActionOwnerName": "Alice",
        "SlaType": sla,
        "EtaDate": "2026-03-01",
        "dueDate": "2026-02-15",
        "ActionItemStatus": "Active",
        "url": url,
        "ActionWikiLink": wiki,
        "Remediation": remediation,
        "AssetTypeLink0": "",
        "AssetTypeLink1": "",
        "AssetTypeLink2": "",
        "CustomGroupingLink": "",
        "AssetType0": "Subscription",
        "S360_ServiceId": "svc-1",
    }


# ===================================================================
# _is_js_shell — edge cases (lines 202-205)
# ===================================================================

class TestIsJsShellEdge:
    """Cover the short-text / low-word-count branches."""

    def test_empty_string_returns_false(self):
        assert _is_js_shell("") is False

    def test_short_no_indicator_few_words(self):
        """< _MIN_USEFUL_CHARS and < 50 words → True (line 205)."""
        text = "Hello world " * 10  # 20 words, well under 50
        assert len(text) < 400
        assert _is_js_shell(text) is True

    def test_short_with_js_indicator(self):
        """Matches _JS_SHELL_RE → True."""
        assert _is_js_shell("Please enable JavaScript to continue.") is True

    def test_long_text_not_shell(self):
        """≥ _MIN_USEFUL_CHARS → False regardless of content."""
        text = "word " * 200  # 1000 chars, > 400
        assert _is_js_shell(text) is False

    def test_short_but_enough_words(self):
        """Short overall length but ≥ 50 words → False."""
        # 51 short words = ~152 chars, under _MIN_USEFUL_CHARS
        text = " ".join(f"w{i}" for i in range(51))
        assert len(text) < 400
        assert _is_js_shell(text) is False

    def test_loading_ellipsis_detected(self):
        assert _is_js_shell("Loading...") is True
        assert _is_js_shell("Loading\u2026") is True


# ===================================================================
# _is_login_page — edge cases (lines 264-267)
# ===================================================================

class TestIsLoginPageEdge:
    """Cover the sign-in-count / unique-word branches."""

    def test_empty_text(self):
        assert _is_login_page("") is False

    def test_no_login_indicators(self):
        """No match for _LOGIN_PAGE_RE → False early."""
        assert _is_login_page("Perfectly normal documentation page about deployment.") is False

    def test_login_indicator_few_unique_words(self):
        """Matches login indicators AND < 30 unique words + < 80 words → True."""
        text = "Sign in to your account. Please sign in options. Enter your email."
        assert _is_login_page(text) is True

    def test_sign_in_count_branch(self):
        """sign_in_count >= 2, unique_words < 60 → True (line 264-267)."""
        # Needs: match _LOGIN_PAGE_RE, sign_in_count >= 2, unique_words < 60
        # Use enough words to exceed the first check (≥80 words or ≥30 unique)
        # but stay under 60 unique for the second branch
        words = " ".join(f"w{i}" for i in range(50))
        text = f"Sign in to your account. {words} Please sign in options here."
        assert _is_login_page(text) is True

    def test_lots_of_unique_words_not_login(self):
        """Many unique words → False even with one sign-in indicator."""
        words = " ".join(f"unique{i}" for i in range(70))
        text = f"sign in to your account {words}"
        assert _is_login_page(text) is False


# ===================================================================
# _fetch_via_cdp (lines 321-367)
# ===================================================================

class TestFetchViaCdp:
    """Cover CDP fetch: import error, auth redirect, success, exception."""

    def test_playwright_not_installed(self):
        """ImportError branch → error='playwright not installed'."""
        with patch.dict("sys.modules", {"playwright.sync_api": None}):
            with patch("builtins.__import__", side_effect=ImportError("no pw")):
                result = _fetch_via_cdp("https://example.com")
        assert result["error"] == "playwright not installed"
        assert result["method"] == "cdp"

    def test_auth_redirect_detected(self):
        """CDP lands on login domain → auth_redirect."""
        mock_page = MagicMock()
        mock_page.url = "https://login.microsoftonline.com/common/oauth2"
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_pw_ctx = MagicMock()
        mock_pw_ctx.chromium.launch.return_value = mock_browser

        mock_sync_pw = MagicMock()
        mock_sync_pw.__enter__ = MagicMock(return_value=mock_pw_ctx)
        mock_sync_pw.__exit__ = MagicMock(return_value=False)

        with patch("sfi_reporter.kpi_analyzer.sync_playwright", create=True) as mock_sp:
            # Patch the import inside the function
            import sfi_reporter.kpi_analyzer as mod
            original = mod.__dict__.get("sync_playwright")
            try:
                mock_sp.return_value = mock_sync_pw
                with patch.dict(mod.__dict__, {"sync_playwright": mock_sp}):
                    # We need to patch the dynamic import
                    mock_module = MagicMock()
                    mock_module.sync_playwright = mock_sp
                    with patch.dict("sys.modules", {"playwright.sync_api": mock_module}):
                        result = _fetch_via_cdp("https://internal.ms/page")
            finally:
                if original is not None:
                    mod.__dict__["sync_playwright"] = original

        assert result["error"] == "auth_redirect"
        assert result["method"] == "cdp"

    def test_exception_in_cdp(self):
        """Playwright raises → error string returned."""
        mock_module = MagicMock()
        mock_cm = MagicMock()
        mock_cm.__enter__ = MagicMock(side_effect=RuntimeError("boom"))
        mock_cm.__exit__ = MagicMock(return_value=False)
        mock_module.sync_playwright.return_value = mock_cm

        with patch.dict("sys.modules", {"playwright.sync_api": mock_module}):
            result = _fetch_via_cdp("https://example.com")
        assert "boom" in result["error"]
        assert result["method"] == "cdp"

    def test_success_with_content(self):
        """CDP succeeds with content and discovered URLs."""
        mock_page = MagicMock()
        mock_page.url = "https://docs.microsoft.com/page"
        mock_page.content.return_value = "<html><body><p>Real content here</p></body></html>"
        mock_page.eval_on_selector_all.return_value = [
            "https://learn.microsoft.com/extra",
            "https://login.microsoftonline.com/skip",
        ]
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_pw_ctx = MagicMock()
        mock_pw_ctx.chromium.launch.return_value = mock_browser

        mock_sync_pw = MagicMock()
        mock_sync_pw.__enter__ = MagicMock(return_value=mock_pw_ctx)
        mock_sync_pw.__exit__ = MagicMock(return_value=False)

        mock_module = MagicMock()
        mock_module.sync_playwright.return_value = mock_sync_pw

        with patch.dict("sys.modules", {"playwright.sync_api": mock_module}):
            result = _fetch_via_cdp("https://docs.microsoft.com/page")

        assert result["method"] == "cdp"
        assert result["content"]  # non-empty
        # login URL should be filtered out
        assert "https://login.microsoftonline.com/skip" not in result.get("discovered_urls", [])
        assert "https://learn.microsoft.com/extra" in result.get("discovered_urls", [])


# ===================================================================
# _fetch_via_urllib (lines 376-397)
# ===================================================================

class TestFetchViaUrllib:
    """Cover urllib fetch: success, non-text content-type, HTTP error, generic exception."""

    def test_success_html(self):
        """Successful fetch with text/html content."""
        mock_resp = MagicMock()
        mock_resp.headers = MagicMock()
        mock_resp.headers.get.return_value = "text/html; charset=utf-8"
        mock_resp.headers.get_content_charset.return_value = "utf-8"
        mock_resp.read.return_value = b"<html><body><p>Hello docs</p></body></html>"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = _fetch_via_urllib("https://example.com/doc")

        assert result["method"] == "urllib"
        assert result["error"] == ""
        assert "Hello docs" in result["content"]

    def test_non_text_content_type(self):
        """Non-text content-type → error returned."""
        mock_resp = MagicMock()
        mock_resp.headers = MagicMock()
        mock_resp.headers.get.return_value = "application/pdf"
        mock_resp.headers.get_content_charset.return_value = None
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = _fetch_via_urllib("https://example.com/file.pdf")

        assert "Non-text content type" in result["error"]
        assert result["content"] == ""

    def test_http_error(self):
        """HTTPError → formatted error."""
        import urllib.error
        exc = urllib.error.HTTPError(
            "https://example.com", 403, "Forbidden", {}, None
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            result = _fetch_via_urllib("https://example.com")

        assert result["error"] == "HTTP 403"
        assert result["method"] == "urllib"

    def test_generic_exception(self):
        """Generic exception → error string."""
        with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            result = _fetch_via_urllib("https://example.com")

        assert "timed out" in result["error"]

    def test_extra_headers_sent(self):
        """Extra headers (bearer token) get added to request."""
        mock_resp = MagicMock()
        mock_resp.headers = MagicMock()
        mock_resp.headers.get.return_value = "text/html"
        mock_resp.headers.get_content_charset.return_value = "utf-8"
        mock_resp.read.return_value = b"<p>ok</p>"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            result = _fetch_via_urllib(
                "https://example.com",
                extra_headers={"Authorization": "Bearer xyz"},
            )

        assert result["error"] == ""
        # Verify Request had the header
        req_arg = mock_open.call_args[0][0]
        assert req_arg.get_header("Authorization") == "Bearer xyz"


# ===================================================================
# _fetch_with_bearer_token (lines 437-439, 452-463)
# ===================================================================

class TestFetchWithBearerToken:
    """Cover bearer-token fetch: import error, token failure, login page, JS shell, success."""

    def test_azure_identity_not_installed(self):
        """ImportError → 'azure-identity not installed'."""
        with patch.dict("sys.modules", {"azure.identity": None}):
            with patch("builtins.__import__", side_effect=ImportError("no azure")):
                result = _fetch_with_bearer_token("https://portal.azure.com")
        assert result["error"] == "azure-identity not installed"
        assert result["method"] == "bearer"

    def test_token_acquisition_fails(self):
        """Credential raises → token_failed error."""
        mock_az = MagicMock()
        mock_cred = MagicMock()
        mock_cred.get_token.side_effect = Exception("CLI not logged in")
        mock_az.AzureCliCredential.return_value = mock_cred

        with patch.dict("sys.modules", {"azure.identity": mock_az}):
            result = _fetch_with_bearer_token("https://portal.azure.com")
        assert "token_failed" in result["error"]
        assert result["method"] == "bearer"

    def test_bearer_gets_login_page(self):
        """Bearer fetch content is a login page → bearer_rejected."""
        mock_az = MagicMock()
        mock_cred = MagicMock()
        mock_cred.get_token.return_value = SimpleNamespace(token="tok123")
        mock_az.AzureCliCredential.return_value = mock_cred

        login_page_content = "Sign in to your account. Enter your email. Sign in options."
        with patch.dict("sys.modules", {"azure.identity": mock_az}):
            with patch(
                "sfi_reporter.kpi_analyzer._fetch_via_urllib",
                return_value={"url": "https://x.com", "content": login_page_content,
                              "error": "", "method": "urllib"},
            ):
                result = _fetch_with_bearer_token("https://x.com")
        assert result["error"] == "bearer_rejected"
        assert result["method"] == "bearer"

    def test_bearer_gets_js_shell(self):
        """Bearer fetch content is a JS shell → bearer_js_shell."""
        mock_az = MagicMock()
        mock_cred = MagicMock()
        mock_cred.get_token.return_value = SimpleNamespace(token="tok123")
        mock_az.AzureCliCredential.return_value = mock_cred

        shell_content = "Loading..."  # short + matches JS shell indicator
        with patch.dict("sys.modules", {"azure.identity": mock_az}):
            with patch(
                "sfi_reporter.kpi_analyzer._fetch_via_urllib",
                return_value={"url": "https://x.com", "content": shell_content,
                              "error": "", "method": "urllib"},
            ):
                result = _fetch_with_bearer_token("https://x.com")
        assert result["error"] == "bearer_js_shell"
        assert result["method"] == "bearer"

    def test_bearer_success(self):
        """Bearer fetch succeeds with real content."""
        mock_az = MagicMock()
        mock_cred = MagicMock()
        mock_cred.get_token.return_value = SimpleNamespace(token="tok123")
        mock_az.AzureCliCredential.return_value = mock_cred

        good_content = "word " * 200  # 1000 chars, passes all heuristics
        with patch.dict("sys.modules", {"azure.identity": mock_az}):
            with patch(
                "sfi_reporter.kpi_analyzer._fetch_via_urllib",
                return_value={"url": "https://x.com", "content": good_content,
                              "error": "", "method": "urllib"},
            ):
                result = _fetch_with_bearer_token("https://x.com")
        assert result["method"] == "bearer"
        assert result["content"] == good_content


# ===================================================================
# _get_edge_user_data_dir (lines 452-463)
# ===================================================================

class TestGetEdgeUserDataDir:
    """Cover Windows NT and posix branches."""

    def test_windows_path_exists(self, tmp_path):
        edge_dir = tmp_path / "Microsoft" / "Edge" / "User Data"
        edge_dir.mkdir(parents=True)
        with patch("os.name", "nt"), \
             patch.dict(os.environ, {"LOCALAPPDATA": str(tmp_path)}):
            result = _get_edge_user_data_dir()
        assert result == str(edge_dir)

    def test_windows_path_missing(self, tmp_path):
        with patch("os.name", "nt"), \
             patch.dict(os.environ, {"LOCALAPPDATA": str(tmp_path)}):
            result = _get_edge_user_data_dir()
        assert result is None

    def test_posix_darwin(self, tmp_path):
        edge_dir = tmp_path / "Library" / "Application Support" / "Microsoft Edge" / "Default"
        edge_dir.mkdir(parents=True)
        with patch("os.name", "posix"), \
             patch("sys.platform", "darwin"), \
             patch("os.path.expanduser", return_value=str(tmp_path)):
            result = _get_edge_user_data_dir()
        assert result == str(edge_dir)

    def test_posix_linux(self, tmp_path):
        edge_dir = tmp_path / ".config" / "microsoft-edge"
        edge_dir.mkdir(parents=True)
        with patch("os.name", "posix"), \
             patch("sys.platform", "linux"), \
             patch("os.path.expanduser", return_value=str(tmp_path)):
            result = _get_edge_user_data_dir()
        assert result == str(edge_dir)

    def test_unknown_os(self):
        with patch("os.name", "java"):
            result = _get_edge_user_data_dir()
        assert result is None


# ===================================================================
# _find_edge_work_profile (lines 489-530)
# ===================================================================

class TestFindEdgeWorkProfile:
    def test_no_local_state_file(self, tmp_path):
        assert _find_edge_work_profile(str(tmp_path)) is None

    def test_work_profile_found(self, tmp_path):
        data = {
            "profile": {
                "info_cache": {
                    "Profile 1": {"name": "Personal"},
                    "Profile 2": {"name": "Work"},
                },
                "last_used": "Profile 1",
            }
        }
        (tmp_path / "Local State").write_text(json.dumps(data), encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) == "Profile 2"

    def test_managed_profile_found(self, tmp_path):
        data = {
            "profile": {
                "info_cache": {
                    "Profile 1": {"name": "Someone", "hosted_domain": "corp.com"},
                },
                "last_used": "Profile 1",
            }
        }
        (tmp_path / "Local State").write_text(json.dumps(data), encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) == "Profile 1"

    def test_falls_back_to_last_used(self, tmp_path):
        data = {
            "profile": {
                "info_cache": {
                    "Profile 1": {"name": "Personal"},
                },
                "last_used": "Profile 1",
            }
        }
        (tmp_path / "Local State").write_text(json.dumps(data), encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) == "Profile 1"

    def test_corrupt_json(self, tmp_path):
        (tmp_path / "Local State").write_text("{bad json", encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) is None


# ===================================================================
# _copy_edge_profile (lines 536-562)
# ===================================================================

class TestCopyEdgeProfile:
    def test_profile_dir_missing(self, tmp_path):
        assert _copy_edge_profile(str(tmp_path), "NoSuchProfile") is None

    def test_copies_profile_successfully(self, tmp_path):
        # Create source profile with a file and a sub-dir
        profile = tmp_path / "MyProfile"
        profile.mkdir()
        (profile / "Cookies").write_text("cookie data", encoding="utf-8")
        sub = profile / "Bookmarks"
        sub.mkdir()
        (sub / "data.json").write_text("{}", encoding="utf-8")

        # Create Local State
        (tmp_path / "Local State").write_text("{}", encoding="utf-8")

        # Create a skip dir (should not be copied)
        cache_dir = profile / "Cache"
        cache_dir.mkdir()
        (cache_dir / "big_file").write_text("x" * 100, encoding="utf-8")

        temp_dir = _copy_edge_profile(str(tmp_path), "MyProfile")
        try:
            assert temp_dir is not None
            default_dir = Path(temp_dir) / "Default"
            assert (default_dir / "Cookies").exists()
            assert (default_dir / "Bookmarks" / "data.json").exists()
            # Cache should be skipped
            assert not (default_dir / "Cache").exists()
            # Local State should be copied
            assert (Path(temp_dir) / "Local State").exists()
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_listdir_oserror(self, tmp_path):
        """OSError reading profile dir → None + cleanup."""
        profile = tmp_path / "BadProfile"
        profile.mkdir()
        with patch("os.listdir", side_effect=OSError("perm denied")):
            result = _copy_edge_profile(str(tmp_path), "BadProfile")
        assert result is None


# ===================================================================
# _fetch_via_edge_cdp (lines 600-639)
# ===================================================================

class TestFetchViaEdgeCdp:
    def test_playwright_not_installed(self):
        original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

        def selective_import(name, *args, **kwargs):
            if name == "playwright.sync_api":
                raise ImportError("no pw")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=selective_import):
            result = _fetch_via_edge_cdp("https://example.com")
        assert result["error"] == "playwright not installed"
        assert result["method"] == "edge_cdp"

    def test_no_edge_profile(self):
        with patch("sfi_reporter.kpi_analyzer._get_edge_user_data_dir", return_value=None):
            result = _fetch_via_edge_cdp("https://example.com")
        assert result["error"] == "edge_profile_not_found"

    def test_copy_failed(self):
        with patch("sfi_reporter.kpi_analyzer._get_edge_user_data_dir", return_value="/fake/dir"), \
             patch("sfi_reporter.kpi_analyzer._find_edge_work_profile", return_value="Default"), \
             patch("sfi_reporter.kpi_analyzer._copy_edge_profile", return_value=None):
            mock_module = MagicMock()
            with patch.dict("sys.modules", {"playwright.sync_api": mock_module}):
                result = _fetch_via_edge_cdp("https://example.com")
        assert result["error"] == "edge_profile_copy_failed"

    def test_auth_redirect(self, tmp_path):
        mock_page = MagicMock()
        mock_page.url = "https://login.microsoftonline.com/xyz"
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_pw_ctx = MagicMock()
        mock_pw_ctx.chromium.launch_persistent_context.return_value = mock_browser

        mock_sync_pw = MagicMock()
        mock_sync_pw.__enter__ = MagicMock(return_value=mock_pw_ctx)
        mock_sync_pw.__exit__ = MagicMock(return_value=False)

        mock_module = MagicMock()
        mock_module.sync_playwright.return_value = mock_sync_pw

        with patch.dict("sys.modules", {"playwright.sync_api": mock_module}), \
             patch("sfi_reporter.kpi_analyzer._get_edge_user_data_dir", return_value=str(tmp_path)), \
             patch("sfi_reporter.kpi_analyzer._find_edge_work_profile", return_value="Default"), \
             patch("sfi_reporter.kpi_analyzer._copy_edge_profile", return_value=str(tmp_path / "tmp")):
            result = _fetch_via_edge_cdp("https://internal.ms")
        assert result["error"] == "edge_auth_redirect"

    def test_login_page_detected(self, tmp_path):
        mock_page = MagicMock()
        mock_page.url = "https://internal.ms/page"
        mock_page.content.return_value = "<p>Sign in to your account. Enter your email. Sign in options.</p>"
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_pw_ctx = MagicMock()
        mock_pw_ctx.chromium.launch_persistent_context.return_value = mock_browser

        mock_sync_pw = MagicMock()
        mock_sync_pw.__enter__ = MagicMock(return_value=mock_pw_ctx)
        mock_sync_pw.__exit__ = MagicMock(return_value=False)

        mock_module = MagicMock()
        mock_module.sync_playwright.return_value = mock_sync_pw

        with patch.dict("sys.modules", {"playwright.sync_api": mock_module}), \
             patch("sfi_reporter.kpi_analyzer._get_edge_user_data_dir", return_value=str(tmp_path)), \
             patch("sfi_reporter.kpi_analyzer._find_edge_work_profile", return_value="Default"), \
             patch("sfi_reporter.kpi_analyzer._copy_edge_profile", return_value=str(tmp_path / "tmp")):
            result = _fetch_via_edge_cdp("https://internal.ms")
        assert result["error"] == "edge_auth_wall"

    def test_js_shell_detected(self, tmp_path):
        mock_page = MagicMock()
        mock_page.url = "https://internal.ms/spa"
        mock_page.content.return_value = "<html><body>Loading...</body></html>"
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_pw_ctx = MagicMock()
        mock_pw_ctx.chromium.launch_persistent_context.return_value = mock_browser

        mock_sync_pw = MagicMock()
        mock_sync_pw.__enter__ = MagicMock(return_value=mock_pw_ctx)
        mock_sync_pw.__exit__ = MagicMock(return_value=False)

        mock_module = MagicMock()
        mock_module.sync_playwright.return_value = mock_sync_pw

        with patch.dict("sys.modules", {"playwright.sync_api": mock_module}), \
             patch("sfi_reporter.kpi_analyzer._get_edge_user_data_dir", return_value=str(tmp_path)), \
             patch("sfi_reporter.kpi_analyzer._find_edge_work_profile", return_value="Default"), \
             patch("sfi_reporter.kpi_analyzer._copy_edge_profile", return_value=str(tmp_path / "tmp")):
            result = _fetch_via_edge_cdp("https://internal.ms/spa")
        assert result["error"] == "edge_js_shell"

    def test_success(self, tmp_path):
        good_html = "<html><body>" + "<p>Documentation content here. </p>" * 50 + "</body></html>"
        mock_page = MagicMock()
        mock_page.url = "https://docs.ms.com/page"
        mock_page.content.return_value = good_html
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_pw_ctx = MagicMock()
        mock_pw_ctx.chromium.launch_persistent_context.return_value = mock_browser

        mock_sync_pw = MagicMock()
        mock_sync_pw.__enter__ = MagicMock(return_value=mock_pw_ctx)
        mock_sync_pw.__exit__ = MagicMock(return_value=False)

        mock_module = MagicMock()
        mock_module.sync_playwright.return_value = mock_sync_pw

        with patch.dict("sys.modules", {"playwright.sync_api": mock_module}), \
             patch("sfi_reporter.kpi_analyzer._get_edge_user_data_dir", return_value=str(tmp_path)), \
             patch("sfi_reporter.kpi_analyzer._find_edge_work_profile", return_value="Default"), \
             patch("sfi_reporter.kpi_analyzer._copy_edge_profile", return_value=str(tmp_path / "tmp")):
            result = _fetch_via_edge_cdp("https://docs.ms.com/page")
        assert result["error"] == ""
        assert result["method"] == "edge_cdp"
        assert "Documentation content" in result["content"]

    def test_exception_in_playwright(self, tmp_path):
        mock_module = MagicMock()
        mock_cm = MagicMock()
        mock_cm.__enter__ = MagicMock(side_effect=RuntimeError("browser crash"))
        mock_cm.__exit__ = MagicMock(return_value=False)
        mock_module.sync_playwright.return_value = mock_cm

        with patch.dict("sys.modules", {"playwright.sync_api": mock_module}), \
             patch("sfi_reporter.kpi_analyzer._get_edge_user_data_dir", return_value=str(tmp_path)), \
             patch("sfi_reporter.kpi_analyzer._find_edge_work_profile", return_value="Default"), \
             patch("sfi_reporter.kpi_analyzer._copy_edge_profile", return_value=str(tmp_path / "tmp")):
            result = _fetch_via_edge_cdp("https://example.com")
        assert "browser crash" in result["error"]


# ===================================================================
# fetch_url_content — cascade logic (lines 698, ~660-700)
# ===================================================================

class TestFetchUrlContent:
    """Cover the auth cascade: CDP→bearer→edge→urllib fallback."""

    def test_cdp_auth_redirect_then_bearer_success(self):
        """Auth redirect from CDP, bearer succeeds."""
        with patch("sfi_reporter.kpi_analyzer._fetch_via_cdp",
                    return_value={"url": "https://x.com", "content": "", "error": "auth_redirect", "method": "cdp"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_with_bearer_token",
                    return_value={"url": "https://x.com", "content": "bearer docs", "error": "", "method": "bearer"}):
            result = fetch_url_content("https://x.com")
        assert result["method"] == "bearer"
        assert result["content"] == "bearer docs"

    def test_cdp_auth_redirect_bearer_fail_edge_success(self):
        """Auth redirect, bearer fails, edge succeeds."""
        with patch("sfi_reporter.kpi_analyzer._fetch_via_cdp",
                    return_value={"url": "https://x.com", "content": "", "error": "auth_redirect", "method": "cdp"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_with_bearer_token",
                    return_value={"url": "https://x.com", "content": "", "error": "token_failed", "method": "bearer"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_via_edge_cdp",
                    return_value={"url": "https://x.com", "content": "edge docs", "error": "", "method": "edge_cdp"}):
            result = fetch_url_content("https://x.com")
        assert result["method"] == "edge_cdp"
        assert result["content"] == "edge docs"

    def test_cdp_auth_redirect_all_fail(self):
        """Auth redirect, all auth methods fail → auth_redirect error."""
        with patch("sfi_reporter.kpi_analyzer._fetch_via_cdp",
                    return_value={"url": "https://x.com", "content": "", "error": "auth_redirect", "method": "cdp"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_with_bearer_token",
                    return_value={"url": "https://x.com", "content": "", "error": "token_failed", "method": "bearer"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_via_edge_cdp",
                    return_value={"url": "https://x.com", "content": "", "error": "edge_err", "method": "edge_cdp"}):
            result = fetch_url_content("https://x.com")
        assert result["error"] == "auth_redirect"

    def test_cdp_success(self):
        """CDP returns content → return directly."""
        with patch("sfi_reporter.kpi_analyzer._fetch_via_cdp",
                    return_value={"url": "https://x.com", "content": "cdp data", "error": "", "method": "cdp"}):
            result = fetch_url_content("https://x.com")
        assert result["content"] == "cdp data"
        assert result["method"] == "cdp"

    def test_cdp_no_content_urllib_fallback(self):
        """CDP no content, no auth_redirect → fall back to urllib."""
        long_content = "urllib documentation data " * 50  # > 400 chars
        with patch("sfi_reporter.kpi_analyzer._fetch_via_cdp",
                    return_value={"url": "https://x.com", "content": "", "error": "timeout", "method": "cdp"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_via_urllib",
                    return_value={"url": "https://x.com", "content": long_content, "error": "", "method": "urllib"}):
            result = fetch_url_content("https://x.com")
        assert result["content"] == long_content

    def test_urllib_js_shell_error(self):
        """urllib returns a JS shell → content cleared, error set."""
        with patch("sfi_reporter.kpi_analyzer._fetch_via_cdp",
                    return_value={"url": "https://x.com", "content": "", "error": "pw_err", "method": "cdp"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_via_urllib",
                    return_value={"url": "https://x.com", "content": "Loading...", "error": "", "method": "urllib"}):
            result = fetch_url_content("https://x.com")
        assert result["content"] == ""
        assert "js_shell" in result["error"]

    def test_urllib_no_content_cdp_error_merged(self):
        """urllib fails + CDP also failed → merged error message."""
        with patch("sfi_reporter.kpi_analyzer._fetch_via_cdp",
                    return_value={"url": "https://x.com", "content": "", "error": "render_fail", "method": "cdp"}), \
             patch("sfi_reporter.kpi_analyzer._fetch_via_urllib",
                    return_value={"url": "https://x.com", "content": "", "error": "HTTP 403", "method": "urllib"}):
            result = fetch_url_content("https://x.com")
        assert "render_fail" in result["error"]
        assert "HTTP 403" in result["error"]


# ===================================================================
# _fetch_with_provenance (lines 752-811)
# ===================================================================

class TestFetchWithProvenance:
    def test_empty_urls(self):
        docs, results = _fetch_with_provenance(set())
        assert docs == {}
        assert results == []

    def test_success_and_failure(self):
        def mock_fetch(url, timeout=10):
            if "good" in url:
                return {"url": url, "content": "word " * 100, "error": "", "method": "cdp"}
            return {"url": url, "content": "", "error": "HTTP 500", "method": "urllib"}

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch):
            docs, results = _fetch_with_provenance({"https://good.com", "https://bad.com"})

        assert len(results) == 2
        ok_results = [r for r in results if r.ok]
        fail_results = [r for r in results if not r.ok]
        assert len(ok_results) == 1
        assert len(fail_results) == 1

    def test_login_page_detected(self):
        login_text = "Sign in to your account. Enter your email. Sign in options."

        def mock_fetch(url, timeout=10):
            return {"url": url, "content": login_text, "error": "", "method": "urllib"}

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch):
            docs, results = _fetch_with_provenance({"https://login.example.com"})

        assert results[0].ok is False
        assert results[0].error == "auth_wall"
        assert "Authentication wall" in docs["https://login.example.com"]

    def test_auth_redirect_result(self):
        def mock_fetch(url, timeout=10):
            return {"url": url, "content": "", "error": "auth_redirect", "method": "cdp"}

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch):
            docs, results = _fetch_with_provenance({"https://auth.example.com"})

        assert results[0].ok is False
        assert results[0].error == "auth_wall"

    def test_js_shell_result(self):
        def mock_fetch(url, timeout=10):
            return {"url": url, "content": "", "error": "js_shell", "method": "urllib"}

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch):
            docs, results = _fetch_with_provenance({"https://spa.example.com"})

        assert results[0].ok is False
        assert results[0].error == "auth_wall"

    def test_discovered_urls_propagated(self):
        def mock_fetch(url, timeout=10):
            return {
                "url": url, "content": "real content " * 50,
                "error": "", "method": "cdp",
                "discovered_urls": ["https://extra.com"],
            }

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch):
            docs, results = _fetch_with_provenance({"https://example.com"})

        assert results[0].discovered_urls == ["https://extra.com"]

    def test_max_urls_cap(self):
        urls = {f"https://example.com/{i}" for i in range(20)}

        def mock_fetch(url, timeout=10):
            return {"url": url, "content": "ok " * 200, "error": "", "method": "urllib"}

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch):
            docs, results = _fetch_with_provenance(urls, max_urls=5)

        assert len(results) == 5


# ===================================================================
# format_sources_card — edge cases (lines 846, 871)
# ===================================================================

class TestFormatSourcesCardEdge:
    def test_zero_urls(self):
        result = AnalysisResult(prompt="p", urls_found=[], fetch_results=[])
        card = format_sources_card(result)
        assert "No documentation URLs" in card

    def test_auth_wall_with_hint(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://x.com"],
            fetch_results=[FetchResult(url="https://x.com", ok=False, chars=0, error="auth_wall")],
        )
        card = format_sources_card(result)
        assert "\U0001f512" in card
        assert "login / auth wall" in card
        # Should include auth hint
        assert "Edge" in card or "edge" in card.lower()

    def test_discovered_urls_shown(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://a.com"],
            fetch_results=[
                FetchResult(
                    url="https://a.com", ok=True, chars=500, error="",
                    discovered_urls=["https://new1.com", "https://new2.com"],
                ),
            ],
        )
        card = format_sources_card(result)
        assert "discovered" in card
        assert "https://new1.com" in card

    def test_generic_error_in_card(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://x.com"],
            fetch_results=[FetchResult(url="https://x.com", ok=False, chars=0, error="HTTP 500")],
        )
        card = format_sources_card(result)
        assert "HTTP 500" in card
        assert "\u274c" in card


# ===================================================================
# _safe_filename (line 884)
# ===================================================================

class TestSafeFilename:
    def test_basic_url(self):
        name = _safe_filename("https://learn.microsoft.com/en-us/azure/security")
        assert name.endswith(".txt")
        assert "learn_microsoft_com" in name

    def test_long_path_truncated(self):
        long_url = "https://example.com/" + "a" * 200
        name = _safe_filename(long_url)
        # Filename should be reasonable length
        assert len(name) < 200

    def test_deterministic(self):
        url = "https://example.com/page"
        assert _safe_filename(url) == _safe_filename(url)


# ===================================================================
# _save_fetched_docs (lines 884-951)
# ===================================================================

class TestSaveFetchedDocs:
    def test_saves_files_and_manifest(self, tmp_path):
        docs = {
            "https://a.com/doc": "Doc A content",
            "https://b.com/fail": "(Could not fetch: HTTP 500)",
        }
        with patch("tempfile.gettempdir", return_value=str(tmp_path)):
            docs_dir = _save_fetched_docs(docs, "KPI-Test")

        assert docs_dir.exists()
        manifest = docs_dir / "_manifest.txt"
        assert manifest.exists()
        manifest_text = manifest.read_text(encoding="utf-8")
        assert "KPI-Test" in manifest_text
        assert "[OK]" in manifest_text
        assert "[FAILED]" in manifest_text

        # Check individual doc files
        files = list(docs_dir.glob("*.txt"))
        # _manifest.txt + 2 doc files
        assert len(files) == 3

    def test_sanitizes_kpi_name(self, tmp_path):
        docs = {"https://a.com": "content"}
        with patch("tempfile.gettempdir", return_value=str(tmp_path)):
            docs_dir = _save_fetched_docs(docs, "KPI<>:\"/|?*Bad")
        # Should create directory without illegal chars
        assert docs_dir.exists()


# ===================================================================
# build_analysis_prompt — docs_dir mode (lines 960+)
# ===================================================================

class TestBuildAnalysisPromptDocsDir:
    def test_no_items(self):
        assert build_analysis_prompt([], {}) == "No items found for this KPI."

    def test_docs_dir_with_readable_docs(self):
        items = [_make_item()]
        docs = {"https://a.com": "Real documentation content"}
        prompt = build_analysis_prompt(items, docs, docs_dir="/tmp/docs")
        assert "read_fetched_doc" in prompt
        assert "https://a.com" in prompt

    def test_docs_dir_all_blocked(self):
        items = [_make_item()]
        docs = {"https://a.com": "(Authentication wall — blocked)"}
        prompt = build_analysis_prompt(items, docs, docs_dir="/tmp/docs")
        assert "Do NOT call read_fetched_doc" in prompt

    def test_docs_dir_mixed(self):
        items = [_make_item()]
        docs = {
            "https://good.com": "Real docs here " * 50,
            "https://bad.com": "(Could not fetch: HTTP 403)",
        }
        prompt = build_analysis_prompt(items, docs, docs_dir="/tmp/docs")
        assert "read_fetched_doc" in prompt
        assert "BLOCKED" in prompt

    def test_inline_mode_no_docs_dir(self):
        items = [_make_item()]
        docs = {"https://a.com": "inline content"}
        prompt = build_analysis_prompt(items, docs)
        assert "inline content" in prompt
        assert "Do NOT call any tools" in prompt

    def test_truncation_note_for_many_items(self):
        items = [_make_item(item_id=f"AI-{i}") for i in range(40)]
        prompt = build_analysis_prompt(items, {})
        assert "40" in prompt
        assert "30" in prompt


# ===================================================================
# _discover_relevant_urls (lines 1067-1096)
# ===================================================================

class TestDiscoverRelevantUrls:
    def test_empty_inputs(self):
        result = _discover_relevant_urls({}, [], set())
        assert result == set()

    def test_from_cdp_discovered(self):
        fr = FetchResult(
            url="https://a.com", ok=True, chars=100, error="",
            discovered_urls=["https://learn.microsoft.com/new-doc"],
        )
        result = _discover_relevant_urls({}, [fr], set())
        assert "https://learn.microsoft.com/new-doc" in result

    def test_from_text_content(self):
        docs = {
            "https://a.com": "See https://aka.ms/security-guide for details.",
        }
        result = _discover_relevant_urls(docs, [], set())
        assert "https://aka.ms/security-guide" in result

    def test_excludes_login_urls(self):
        fr = FetchResult(
            url="https://a.com", ok=True, chars=100, error="",
            discovered_urls=["https://login.microsoftonline.com/oauth2"],
        )
        result = _discover_relevant_urls({}, [fr], set())
        assert len(result) == 0

    def test_excludes_already_known(self):
        fr = FetchResult(
            url="https://a.com", ok=True, chars=100, error="",
            discovered_urls=["https://learn.microsoft.com/known"],
        )
        result = _discover_relevant_urls({}, [fr], {"https://learn.microsoft.com/known"})
        assert len(result) == 0

    def test_caps_at_max_discovered(self):
        discovered = [f"https://learn.microsoft.com/doc{i}" for i in range(20)]
        fr = FetchResult(url="https://a.com", ok=True, chars=100, error="",
                         discovered_urls=discovered)
        result = _discover_relevant_urls({}, [fr], set(), max_discovered=3)
        assert len(result) == 3

    def test_skips_failed_content(self):
        docs = {
            "https://a.com": "(Could not fetch: HTTP 500) https://aka.ms/should-skip",
        }
        result = _discover_relevant_urls(docs, [], set())
        # Content starting with "(Could not fetch:" is skipped
        assert len(result) == 0

    def test_irrelevant_urls_filtered(self):
        """URLs not matching _RELEVANT_URL_PATTERNS are excluded."""
        fr = FetchResult(
            url="https://a.com", ok=True, chars=100, error="",
            discovered_urls=["https://random-unrelated-site.com/page"],
        )
        result = _discover_relevant_urls({}, [fr], set())
        assert len(result) == 0


# ===================================================================
# analyze_kpi — integration (lines 1117-1172)
# ===================================================================

class TestAnalyzeKpi:
    def test_no_matching_items(self):
        app = MagicMock()
        app.current_data = {"detailed_items": [_make_item(kpi_id="OTHER")]}
        result = analyze_kpi(app, "KPI-MISSING")
        assert isinstance(result, AnalysisResult)
        assert "No action items found" in result.prompt

    def test_no_data(self):
        app = MagicMock()
        app.current_data = None
        result = analyze_kpi(app, "KPI-A")
        assert "No action items found" in result.prompt

    def test_full_flow(self, tmp_path):
        """End-to-end: items → URL collection → fetch → prompt."""
        items = [
            _make_item(kpi_id="KPI-X", kpi_name="Test KPI",
                       url="https://docs.example.com/page"),
        ]
        app = MagicMock()
        app.current_data = {"detailed_items": items}

        def mock_fetch(url, timeout=10):
            return {"url": url, "content": "word " * 200, "error": "", "method": "urllib"}

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch), \
             patch("tempfile.gettempdir", return_value=str(tmp_path)):
            result = analyze_kpi(app, "KPI-X")

        assert isinstance(result, AnalysisResult)
        assert "Test KPI" in result.prompt
        assert len(result.urls_found) >= 1
        assert len(result.fetch_results) >= 1
        assert result.docs_dir  # non-empty

    def test_discovery_pass(self, tmp_path):
        """Verify recursive URL discovery is attempted."""
        items = [
            _make_item(kpi_id="KPI-D", kpi_name="Discovery KPI",
                       url="https://learn.microsoft.com/start"),
        ]
        app = MagicMock()
        app.current_data = {"detailed_items": items}

        call_count = {"n": 0}

        def mock_fetch(url, timeout=10):
            call_count["n"] += 1
            # First call returns content with a discoverable URL
            if call_count["n"] == 1:
                return {
                    "url": url,
                    "content": "See https://aka.ms/remediation for guidance. " + ("word " * 100),
                    "error": "", "method": "cdp",
                    "discovered_urls": [],
                }
            return {"url": url, "content": "extra content " * 50, "error": "", "method": "urllib"}

        with patch("sfi_reporter.kpi_analyzer.fetch_url_content", side_effect=mock_fetch), \
             patch("tempfile.gettempdir", return_value=str(tmp_path)):
            result = analyze_kpi(app, "KPI-D")

        # Should have fetched more than just the initial URL
        assert len(result.urls_found) >= 2
        assert call_count["n"] >= 2
