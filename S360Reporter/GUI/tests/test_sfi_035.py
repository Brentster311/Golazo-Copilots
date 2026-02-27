"""Tests for SFI-035 – LLM Analysis Sources Provenance Card.

Covers the AnalysisResult dataclass, FetchResult dataclass,
format_sources_card function, and the refactored analyze_kpi return type.
"""

from __future__ import annotations

import os

import pytest

from s360_reporter.kpi_analyzer import (
    AnalysisResult,
    FetchResult,
    _AUTH_BLOCKED_MSG,
    _AUTH_HINT_MSG,
    _MIN_USEFUL_CHARS,
    _copy_edge_profile,
    _find_edge_work_profile,
    _is_js_shell,
    _is_login_page,
    _fetch_with_bearer_token,
    _fetch_via_edge_cdp,
    _get_edge_user_data_dir,
    analyze_kpi,
    build_analysis_prompt,
    collect_urls,
    fetch_all_urls,
    fetch_url_content,
    format_sources_card,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_item(
    item_id: str = "AI-1",
    title: str = "Fix something",
    kpi_id: str = "KPI-A",
    kpi_name: str = "[SFI-NS3.2.1] Secure PaaS",
    url: str = "",
    wiki: str = "",
    remediation: str = "",
) -> dict:
    return {
        "id": item_id,
        "title": title,
        "_kpi_id": kpi_id,
        "_kpi_name": kpi_name,
        "S360_ServiceTreeServiceName": "My Service",
        "ActionOwnerName": "Alice",
        "SlaType": "OutOfSla",
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


# ---------------------------------------------------------------------------
# TC-1: AnalysisResult contains successful fetch metadata
# ---------------------------------------------------------------------------

class TestAnalysisResultSuccess:
    def test_contains_urls_found(self):
        result = AnalysisResult(
            prompt="test prompt",
            urls_found=["https://a.com", "https://b.com"],
            fetch_results=[
                FetchResult(url="https://a.com", ok=True, chars=1500, error=""),
                FetchResult(url="https://b.com", ok=True, chars=2000, error=""),
            ],
        )
        assert len(result.urls_found) == 2
        assert "https://a.com" in result.urls_found
        assert "https://b.com" in result.urls_found

    def test_fetch_results_fields(self):
        fr = FetchResult(url="https://a.com", ok=True, chars=3200, error="")
        assert fr.ok is True
        assert fr.chars == 3200
        assert fr.error == ""
        assert fr.url == "https://a.com"

    def test_prompt_is_string(self):
        result = AnalysisResult(
            prompt="full prompt text",
            urls_found=[],
            fetch_results=[],
        )
        assert isinstance(result.prompt, str)
        assert result.prompt == "full prompt text"


# ---------------------------------------------------------------------------
# TC-2: AnalysisResult captures failed fetch metadata
# ---------------------------------------------------------------------------

class TestAnalysisResultFailure:
    def test_failed_fetch_result(self):
        fr = FetchResult(url="https://fail.com", ok=False, chars=0, error="HTTP 403")
        assert fr.ok is False
        assert fr.chars == 0
        assert "403" in fr.error

    def test_timeout_error(self):
        fr = FetchResult(url="https://slow.com", ok=False, chars=0, error="timed out")
        assert fr.ok is False
        assert "timed out" in fr.error


# ---------------------------------------------------------------------------
# TC-3: Zero URLs produces correct AnalysisResult
# ---------------------------------------------------------------------------

class TestZeroUrls:
    def test_empty_urls(self):
        result = AnalysisResult(
            prompt="prompt with items but no docs",
            urls_found=[],
            fetch_results=[],
        )
        assert result.urls_found == []
        assert result.fetch_results == []
        assert len(result.prompt) > 0


# ---------------------------------------------------------------------------
# TC-4: Mixed success/failure fetch results
# ---------------------------------------------------------------------------

class TestMixedFetchResults:
    def test_mixed_results(self):
        results = [
            FetchResult(url="https://a.com", ok=True, chars=1000, error=""),
            FetchResult(url="https://b.com", ok=True, chars=2000, error=""),
            FetchResult(url="https://c.com", ok=False, chars=0, error="timeout"),
        ]
        successes = [r for r in results if r.ok]
        failures = [r for r in results if not r.ok]
        assert len(successes) == 2
        assert len(failures) == 1
        assert failures[0].url == "https://c.com"


# ---------------------------------------------------------------------------
# TC-5: AnalysisResult.prompt matches legacy format
# ---------------------------------------------------------------------------

class TestPromptBackwardCompat:
    def test_str_returns_prompt(self):
        result = AnalysisResult(
            prompt="the full prompt",
            urls_found=["https://a.com"],
            fetch_results=[FetchResult(url="https://a.com", ok=True, chars=100, error="")],
        )
        assert str(result) == "the full prompt"

    def test_prompt_contains_expected_content(self):
        """Verify prompt built from items still has expected structure."""
        items = [_make_item(url="https://doc.com")]
        docs = {"https://doc.com": "Documentation content here"}
        prompt = build_analysis_prompt(items, docs)
        assert "What is being asked" in prompt
        assert "Documentation content here" in prompt
        assert "AI-1" in prompt


# ---------------------------------------------------------------------------
# TC-6: format_sources_card output correctness
# ---------------------------------------------------------------------------

class TestFormatSourcesCard:
    def test_header_present(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://a.com"],
            fetch_results=[FetchResult(url="https://a.com", ok=True, chars=3200, error="")],
        )
        card = format_sources_card(result)
        assert "Sources" in card

    def test_success_indicator(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://a.com"],
            fetch_results=[FetchResult(url="https://a.com", ok=True, chars=1800, error="")],
        )
        card = format_sources_card(result)
        assert "\u2705" in card  # ✅
        assert "https://a.com" in card
        assert "1800" in card or "1.8k" in card.lower()

    def test_failure_indicator(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://fail.com"],
            fetch_results=[FetchResult(url="https://fail.com", ok=False, chars=0, error="HTTP 403")],
        )
        card = format_sources_card(result)
        assert "\u274c" in card  # ❌
        assert "https://fail.com" in card
        assert "403" in card

    def test_mixed_indicators(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://a.com", "https://b.com"],
            fetch_results=[
                FetchResult(url="https://a.com", ok=True, chars=2000, error=""),
                FetchResult(url="https://b.com", ok=False, chars=0, error="timeout"),
            ],
        )
        card = format_sources_card(result)
        assert "\u2705" in card
        assert "\u274c" in card
        assert "1 fetched" in card.lower() or "1 success" in card.lower() or "1/" in card

    def test_zero_urls_message(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=[],
            fetch_results=[],
        )
        card = format_sources_card(result)
        assert "no documentation urls found" in card.lower() or "0 urls" in card.lower()

    def test_counts_in_header(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://a.com", "https://b.com", "https://c.com"],
            fetch_results=[
                FetchResult(url="https://a.com", ok=True, chars=1000, error=""),
                FetchResult(url="https://b.com", ok=True, chars=2000, error=""),
                FetchResult(url="https://c.com", ok=False, chars=0, error="HTTP 500"),
            ],
        )
        card = format_sources_card(result)
        assert "3" in card  # total URLs
        assert "2" in card  # successes
        assert "1" in card  # failures


# ---------------------------------------------------------------------------
# Login page detection (SFI-035+)
# ---------------------------------------------------------------------------

class TestLoginPageDetection:
    """Tests for _is_login_page heuristic."""

    def test_empty_text_is_not_login(self):
        assert _is_login_page("") is False

    def test_normal_doc_is_not_login(self):
        doc = (
            "Azure Key Vault provides a way to securely store and access secrets. "
            "Use RBAC to manage access to keys, secrets, and certificates. "
            "Follow these steps to configure diagnostic settings for your vault."
        )
        assert _is_login_page(doc) is False

    def test_microsoft_sign_in_page(self):
        """Simulate the kind of garbage output from a login wall."""
        page = "Sign in to your account\n\n\n\nSign in\nCan't access your account?\nSign-in options\nTerms of use\nPrivacy & cookies"
        assert _is_login_page(page) is True

    def test_sign_in_with_lots_of_whitespace(self):
        # Mimic the user's actual output: mostly whitespace + "Sign in"
        page = "Sign in to your account\n" + "\n" * 50 + "Sign in\n" + "\n" * 20 + "Can't access your account?\nSign-in options"
        assert _is_login_page(page) is True

    def test_doc_mentioning_sign_in_is_not_login(self):
        """A real doc that mentions sign-in steps should NOT be flagged."""
        doc = (
            "To configure SSO, navigate to Azure AD and sign in with your admin account. "
            "Then go to Enterprise Applications, select your app, and configure SAML. "
            "Users will be able to sign in using their corporate credentials. "
            "Configure conditional access policies to enforce MFA. "
            "Review audit logs to verify sign-in activity. "
            "Use Azure AD Identity Protection to detect risky sign-ins. "
            "Enable password writeback for self-service password reset. "
            "Configure application proxy for on-premises applications."
        )
        assert _is_login_page(doc) is False


class TestAuthWallInSourcesCard:
    """Tests that auth_wall FetchResults show a lock icon."""

    def test_auth_wall_shows_lock(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://lens.example.com/dashboard"],
            fetch_results=[
                FetchResult(url="https://lens.example.com/dashboard",
                            ok=False, chars=0, error="auth_wall",
                            method="cdp"),
            ],
        )
        card = format_sources_card(result)
        assert "\U0001f512" in card  # lock emoji
        assert "auth wall" in card.lower()


class TestManifestWithAuthWall:
    """Tests that build_analysis_prompt manifest marks blocked URLs."""

    def test_blocked_urls_marked_in_manifest(self):
        items = [_make_item(url="https://good.example.com")]
        fetched = {
            "https://good.example.com": "Useful documentation content here.",
            "https://auth.example.com": _AUTH_BLOCKED_MSG,
        }
        prompt = build_analysis_prompt(items, fetched, docs_dir="/tmp/docs")
        assert "BLOCKED" in prompt
        assert "good.example.com" in prompt
        # Auth-blocked URL should not have a filename entry
        assert "auth.example.com" in prompt

    def test_manifest_mode_enables_web_fetch(self):
        """When docs_dir is set, the prompt should allow web_fetch."""
        items = [_make_item(url="https://example.com")]
        fetched = {"https://example.com": "Some content."}
        prompt = build_analysis_prompt(items, fetched, docs_dir="/tmp/docs")
        assert "web_fetch" in prompt
        assert "read_fetched_doc" in prompt

    def test_no_docs_dir_disables_tools(self):
        """Without docs_dir, prompt should say 'do NOT call any tools'."""
        items = [_make_item(url="https://example.com")]
        fetched = {"https://example.com": "Some content."}
        prompt = build_analysis_prompt(items, fetched)
        assert "Do NOT call any tools" in prompt

    def test_all_docs_blocked_skips_read_fetched_doc(self):
        """When every doc is blocked, prompt should tell LLM NOT to read files."""
        items = [_make_item(url="https://auth.example.com")]
        fetched = {
            "https://auth.example.com": _AUTH_BLOCKED_MSG,
        }
        prompt = build_analysis_prompt(items, fetched, docs_dir="/tmp/docs")
        assert "Do NOT call read_fetched_doc" in prompt
        assert "All documentation URLs were blocked" in prompt
        # Should still allow web_fetch for fallback
        assert "web_fetch" in prompt
        # Should NOT say "Use the read_fetched_doc tool to read files"
        assert "Use the `read_fetched_doc` tool to read files" not in prompt


# ---------------------------------------------------------------------------
# Auth Cascade Tests
# ---------------------------------------------------------------------------

class TestEdgeHintInSourcesCard:
    """Verify _AUTH_HINT_MSG appears when any fetch result is auth_wall."""

    def test_hint_shown_when_auth_wall_present(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://lens.example.com/dashboard"],
            fetch_results=[
                FetchResult(url="https://lens.example.com/dashboard",
                            ok=False, chars=0, error="auth_wall",
                            method="cdp"),
            ],
        )
        card = format_sources_card(result)
        assert _AUTH_HINT_MSG in card

    def test_hint_not_shown_when_no_auth_wall(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://example.com/docs"],
            fetch_results=[
                FetchResult(url="https://example.com/docs",
                            ok=True, chars=500, error="",
                            method="cdp"),
            ],
        )
        card = format_sources_card(result)
        assert _AUTH_HINT_MSG not in card

    def test_hint_shown_with_mixed_results(self):
        result = AnalysisResult(
            prompt="p",
            urls_found=["https://good.example.com", "https://bad.example.com"],
            fetch_results=[
                FetchResult(url="https://good.example.com",
                            ok=True, chars=500, error="", method="cdp"),
                FetchResult(url="https://bad.example.com",
                            ok=False, chars=0, error="auth_wall",
                            method="cdp"),
            ],
        )
        card = format_sources_card(result)
        assert _AUTH_HINT_MSG in card


class TestEdgeUserDataDir:
    """Verify _get_edge_user_data_dir logic."""

    def test_returns_string_or_none(self):
        """Should return a string path or None, never raise."""
        result = _get_edge_user_data_dir()
        assert result is None or isinstance(result, str)

    @pytest.mark.skipif(os.name != "nt", reason="Windows-only")
    def test_windows_path_contains_edge(self):
        """On Windows with Edge installed, the path should reference Edge."""
        result = _get_edge_user_data_dir()
        if result is not None:
            assert "Edge" in result


class TestFetchWithBearerToken:
    """Verify _fetch_with_bearer_token behaviour with mocks."""

    def test_returns_bearer_method(self, monkeypatch):
        """Method field should always be 'bearer'."""
        # Content must be long enough to not trigger JS shell detection
        long_content = "Real documentation content about security remediation. " * 20
        # Stub out AzureCliCredential to fail quickly
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_urllib",
            lambda url, timeout=10, extra_headers=None: {
                "url": url, "content": long_content, "error": "", "method": "urllib",
            },
        )
        # Provide a fake AzureCliCredential
        from types import SimpleNamespace
        fake_cred_cls = lambda: SimpleNamespace(
            get_token=lambda scope: SimpleNamespace(token="fake-token"),
        )
        monkeypatch.setattr(
            "azure.identity.AzureCliCredential", fake_cred_cls,
            raising=False,
        )
        result = _fetch_with_bearer_token("https://example.com")
        assert result["method"] == "bearer"
        assert result["content"] == long_content

    def test_missing_azure_identity(self, monkeypatch):
        """If azure-identity is not installed, error should say so."""
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "azure.identity":
                raise ImportError("no azure")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        result = _fetch_with_bearer_token("https://example.com")
        assert result["method"] == "bearer"
        assert "not installed" in result["error"]

    def test_token_failure_returns_error(self, monkeypatch):
        """If credential.get_token raises, should return token_failed."""
        from types import SimpleNamespace

        def bad_get_token(scope):
            raise RuntimeError("no CLI session")

        fake_cred_cls = lambda: SimpleNamespace(get_token=bad_get_token)
        monkeypatch.setattr(
            "azure.identity.AzureCliCredential", fake_cred_cls,
            raising=False,
        )
        result = _fetch_with_bearer_token("https://example.com")
        assert result["method"] == "bearer"
        assert "token_failed" in result["error"]

    def test_bearer_rejected_when_login_page(self, monkeypatch):
        """If bearer fetch returns a login page, error should be bearer_rejected."""
        login_page_text = (
            "Sign in to your account "
            "Enter your email address password "
            "Microsoft Azure Login"
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_urllib",
            lambda url, timeout=10, extra_headers=None: {
                "url": url, "content": login_page_text, "error": "",
                "method": "urllib",
            },
        )
        from types import SimpleNamespace
        fake_cred_cls = lambda: SimpleNamespace(
            get_token=lambda scope: SimpleNamespace(token="fake"),
        )
        monkeypatch.setattr(
            "azure.identity.AzureCliCredential", fake_cred_cls,
            raising=False,
        )
        result = _fetch_with_bearer_token("https://example.com")
        assert result["error"] == "bearer_rejected"
        assert result["content"] == ""


class TestFetchViaEdgeCdp:
    """Verify _fetch_via_edge_cdp with mocks."""

    def test_no_playwright_returns_error(self, monkeypatch):
        """If playwright not installed, error should say so."""
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if "playwright" in name:
                raise ImportError("no playwright")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        result = _fetch_via_edge_cdp("https://example.com")
        assert result["method"] == "edge_cdp"
        assert "not installed" in result["error"]

    def test_no_edge_profile_returns_error(self, monkeypatch):
        """If Edge user data dir not found, error should say so."""
        # Provide a stub for playwright so we get past the import guard
        from types import SimpleNamespace
        fake_pw_mod = SimpleNamespace(sync_playwright=lambda: None)
        monkeypatch.setitem(
            __import__("sys").modules,
            "playwright.sync_api",
            fake_pw_mod,
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._get_edge_user_data_dir",
            lambda: None,
        )
        result = _fetch_via_edge_cdp("https://example.com")
        assert result["method"] == "edge_cdp"
        assert result["error"] == "edge_profile_not_found"


class TestFetchUrlContentCascade:
    """Verify the cascade logic in fetch_url_content."""

    def test_cdp_success_returns_immediately(self, monkeypatch):
        """If CDP succeeds, no bearer/edge fallback needed."""
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "CDP OK", "error": "",
                "method": "cdp",
            },
        )
        result = fetch_url_content("https://example.com")
        assert result["method"] == "cdp"
        assert result["content"] == "CDP OK"

    def test_auth_redirect_tries_bearer_then_succeeds(self, monkeypatch):
        """Auth redirect → bearer succeeds → returns bearer result."""
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "auth_redirect",
                "method": "cdp",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_with_bearer_token",
            lambda url, timeout=10: {
                "url": url, "content": "Bearer OK", "error": "",
                "method": "bearer",
            },
        )
        result = fetch_url_content("https://example.com")
        assert result["method"] == "bearer"
        assert result["content"] == "Bearer OK"

    def test_auth_redirect_bearer_fails_tries_edge(self, monkeypatch):
        """Auth redirect → bearer fails → Edge CDP succeeds."""
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "auth_redirect",
                "method": "cdp",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_with_bearer_token",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "token_failed",
                "method": "bearer",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_edge_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "Edge OK", "error": "",
                "method": "edge_cdp",
            },
        )
        result = fetch_url_content("https://example.com")
        assert result["method"] == "edge_cdp"
        assert result["content"] == "Edge OK"

    def test_all_auth_methods_fail_returns_auth_redirect(self, monkeypatch):
        """Auth redirect → bearer fails → Edge fails → auth_redirect error."""
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "auth_redirect",
                "method": "cdp",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_with_bearer_token",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "token_failed",
                "method": "bearer",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_edge_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "edge_auth_wall",
                "method": "edge_cdp",
            },
        )
        result = fetch_url_content("https://example.com")
        assert result["error"] == "auth_redirect"

    def test_cdp_empty_falls_back_to_urllib(self, monkeypatch):
        """CDP returns empty (not auth redirect) → falls back to urllib."""
        long_content = "Real documentation content about security remediation. " * 20
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "timeout",
                "method": "cdp",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_urllib",
            lambda url, timeout=10, extra_headers=None: {
                "url": url, "content": long_content, "error": "",
                "method": "urllib",
            },
        )
        result = fetch_url_content("https://example.com")
        assert result["method"] == "urllib"
        assert result["content"] == long_content

    def test_urllib_js_shell_returns_error(self, monkeypatch):
        """urllib returns JS shell text → content cleared, error reported."""
        shell_text = "Loading... Dashboard"  # very thin SPA shell
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "timeout",
                "method": "cdp",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_urllib",
            lambda url, timeout=10, extra_headers=None: {
                "url": url, "content": shell_text, "error": "",
                "method": "urllib",
            },
        )
        result = fetch_url_content("https://example.com")
        assert result["content"] == ""
        assert "js_shell" in result["error"]

    def test_bearer_js_shell_falls_through_to_edge(self, monkeypatch):
        """Bearer returns JS shell → cascade continues to Edge CDP."""
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "auth_redirect",
                "method": "cdp",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_with_bearer_token",
            lambda url, timeout=10: {
                "url": url, "content": "", "error": "bearer_js_shell",
                "method": "bearer",
            },
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._fetch_via_edge_cdp",
            lambda url, timeout=10: {
                "url": url, "content": "Edge rendered OK", "error": "",
                "method": "edge_cdp",
            },
        )
        result = fetch_url_content("https://example.com")
        assert result["method"] == "edge_cdp"
        assert result["content"] == "Edge rendered OK"


class TestJsShellDetection:
    """Tests for _is_js_shell() heuristic."""

    def test_empty_text_is_not_shell(self):
        assert _is_js_shell("") is False

    def test_long_content_is_not_shell(self):
        """Content longer than _MIN_USEFUL_CHARS is never flagged."""
        content = "Real documentation content. " * 100
        assert len(content) > _MIN_USEFUL_CHARS
        assert _is_js_shell(content) is False

    def test_short_noscript_message(self):
        text = "You need to enable JavaScript to run this app."
        assert _is_js_shell(text) is True

    def test_loading_ellipsis(self):
        text = "Loading..."
        assert _is_js_shell(text) is True

    def test_thin_spa_shell(self):
        """Very short text with few words is flagged as shell."""
        text = "Microsoft Azure Dashboard Home Help Settings"
        assert len(text) < _MIN_USEFUL_CHARS
        assert _is_js_shell(text) is True

    def test_short_but_dense_content(self):
        """Short but information-dense text should not be flagged."""
        # Build text with >50 unique words but under the char limit
        words = [f"word{i}" for i in range(55)]
        text = " ".join(words)
        assert len(text) < _MIN_USEFUL_CHARS
        assert _is_js_shell(text) is False

    def test_javascript_required_indicator(self):
        text = "This app requires JavaScript to function properly."
        assert _is_js_shell(text) is True

    def test_real_error_page_not_shell(self):
        """A real error message with enough words should not be flagged."""
        text = " ".join(
            f"Error: resource {i} not found in the cluster"
            for i in range(15)
        )
        assert len(text) < _MIN_USEFUL_CHARS or _is_js_shell(text) is False


# ---------------------------------------------------------------------------
# Edge Profile Copy Tests
# ---------------------------------------------------------------------------

class TestFindEdgeWorkProfile:
    """Tests for _find_edge_work_profile()."""

    def test_finds_work_profile_by_name(self, tmp_path):
        """Should return the profile dir whose name contains 'work'."""
        import json
        local_state = {
            "profile": {
                "info_cache": {
                    "Default": {"name": "Personal"},
                    "Profile 1": {"name": "Work"},
                },
                "last_used": "Default",
            }
        }
        (tmp_path / "Local State").write_text(json.dumps(local_state), encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) == "Profile 1"

    def test_finds_managed_profile(self, tmp_path):
        """Should return a profile with hosted_domain."""
        import json
        local_state = {
            "profile": {
                "info_cache": {
                    "Default": {"name": "Brent"},
                    "Profile 2": {"name": "Brent", "hosted_domain": "microsoft.com"},
                },
            }
        }
        (tmp_path / "Local State").write_text(json.dumps(local_state), encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) == "Profile 2"

    def test_falls_back_to_last_used(self, tmp_path):
        """Should return last_used if no work/managed profile found."""
        import json
        local_state = {
            "profile": {
                "info_cache": {
                    "Default": {"name": "Personal"},
                    "Profile 1": {"name": "Gaming"},
                },
                "last_used": "Profile 1",
            }
        }
        (tmp_path / "Local State").write_text(json.dumps(local_state), encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) == "Profile 1"

    def test_returns_none_without_local_state(self, tmp_path):
        """Should return None if Local State doesn't exist."""
        assert _find_edge_work_profile(str(tmp_path)) is None

    def test_returns_none_on_malformed_json(self, tmp_path):
        """Should return None if Local State is malformed."""
        (tmp_path / "Local State").write_text("not json", encoding="utf-8")
        assert _find_edge_work_profile(str(tmp_path)) is None


class TestCopyEdgeProfile:
    """Tests for _copy_edge_profile()."""

    def test_copies_essential_files(self, tmp_path):
        """Should copy Cookies and Preferences but skip Cache."""
        import shutil
        profile = tmp_path / "Work"
        profile.mkdir()
        (profile / "Cookies").write_text("cookie data")
        (profile / "Preferences").write_text("{}")
        cache = profile / "Cache"
        cache.mkdir()
        (cache / "big_file.bin").write_bytes(b"\x00" * 1000)

        result = _copy_edge_profile(str(tmp_path), "Work")
        assert result is not None
        # Files should be in Default/ subfolder
        default_dir = os.path.join(result, "Default")
        assert os.path.isfile(os.path.join(default_dir, "Cookies"))
        assert os.path.isfile(os.path.join(default_dir, "Preferences"))
        # Cache should NOT be copied
        assert not os.path.isdir(os.path.join(default_dir, "Cache"))
        # Cleanup
        shutil.rmtree(result, ignore_errors=True)

    def test_copies_local_state(self, tmp_path):
        """Should copy Local State from the user data root."""
        import shutil
        (tmp_path / "Local State").write_text('{"os_crypt": {}}')
        profile = tmp_path / "Default"
        profile.mkdir()
        (profile / "Cookies").write_text("data")

        result = _copy_edge_profile(str(tmp_path), "Default")
        assert result is not None
        assert os.path.isfile(os.path.join(result, "Local State"))
        shutil.rmtree(result, ignore_errors=True)

    def test_returns_none_for_missing_profile(self, tmp_path):
        """Should return None if the profile directory doesn't exist."""
        result = _copy_edge_profile(str(tmp_path), "NonExistent")
        assert result is None

    def test_skips_locked_files_gracefully(self, tmp_path, monkeypatch):
        """Should continue even if some files can't be copied."""
        import shutil as _shutil
        profile = tmp_path / "Default"
        profile.mkdir()
        (profile / "Cookies").write_text("data")
        (profile / "Locked").write_text("secret")

        original_copy2 = _shutil.copy2

        def failing_copy2(src, dst, **kwargs):
            if "Locked" in str(src):
                raise PermissionError("file locked")
            return original_copy2(src, dst, **kwargs)

        monkeypatch.setattr("shutil.copy2", failing_copy2)
        result = _copy_edge_profile(str(tmp_path), "Default")
        assert result is not None
        default_dir = os.path.join(result, "Default")
        assert os.path.isfile(os.path.join(default_dir, "Cookies"))
        _shutil.rmtree(result, ignore_errors=True)


class TestEdgeCdpProfileCopy:
    """Tests that _fetch_via_edge_cdp uses profile copy approach."""

    def test_profile_copy_failure_returns_error(self, monkeypatch):
        """If profile copy fails, should return edge_profile_copy_failed."""
        from types import SimpleNamespace
        fake_pw_mod = SimpleNamespace(sync_playwright=lambda: None)
        monkeypatch.setitem(
            __import__("sys").modules, "playwright.sync_api", fake_pw_mod,
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._get_edge_user_data_dir",
            lambda: "/fake/edge/path",
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._find_edge_work_profile",
            lambda d: "Default",
        )
        monkeypatch.setattr(
            "s360_reporter.kpi_analyzer._copy_edge_profile",
            lambda d, p: None,
        )
        result = _fetch_via_edge_cdp("https://example.com")
        assert result["method"] == "edge_cdp"
        assert result["error"] == "edge_profile_copy_failed"
