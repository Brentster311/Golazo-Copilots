"""Tests for LLM client (llm_client.py)."""
import os
import pytest
from unittest.mock import MagicMock, patch

from sfi_reporter.llm_client import (
    LLMConfig,
    LLMConfigError,
    LLMError,
    AnalysisResult,
    build_prompt,
    analyze_item,
    _parse_sections,
    _format_item_for_prompt,
    _truncate,
)


# ── Sample action item fixture ───────────────────────────────────────────
SAMPLE_ITEM = {
    "id": "AI-12345",
    "_kpi_id": "KPI-67890",
    "title": "Remediate Azure SQL TDE encryption",
    "ActionItemStatus": "Active",
    "SlaType": 2,
    "dueDate": "2026-02-15T00:00:00Z",
    "EtaDate": "2026-02-10T00:00:00Z",
    "EtaStatus": "On Track",
    "createdDate": "2026-01-01T00:00:00Z",
    "S360_ServiceTreeDivisionName": "Cloud + AI",
    "S360_ServiceTreeGroupName": "Azure Data",
    "S360_ServiceTreeOrganizationName": "SQL Platform",
    "S360_ServiceTreeServiceName": "Azure SQL Database",
    "S360_AssignedToName": "Jane Doe",
    "ActionOwnerName": "John Smith",
    "ActionOwnerAlias": "jsmith",
    "Remediation": "Enable TDE on all Azure SQL databases.",
    "Details": "Detailed information about the remediation steps.",
    "Clouds": "Public",
    "Environments": "Production",
    "ResourceURIs": "https://portal.azure.com/#resource/123",
    "ActionWikiLink": "https://wiki.example.com/tde-remediation",
}


# ── TC-1: LLM Config Loads from Environment Variables ─────────────────

class TestLLMConfigFromEnv:
    def test_loads_required_vars(self, monkeypatch):
        """TC-1 Step 1: Config loads from env vars."""
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://myresource.openai.azure.com/")
        monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

        config = LLMConfig.from_env()
        assert config.endpoint == "https://myresource.openai.azure.com/"

    def test_custom_deployment(self, monkeypatch):
        """TC-1 Step 2: Custom deployment name from env."""
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://myresource.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

        config = LLMConfig.from_env()
        assert config.deployment == "gpt-4o-mini"

    def test_default_deployment(self, monkeypatch):
        """TC-1 Step 3: Default deployment when env var not set."""
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://myresource.openai.azure.com/")
        monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

        config = LLMConfig.from_env()
        assert config.deployment == "gpt-4o"


# ── TC-2: LLM Config Raises on Missing Required Vars ─────────────────

class TestLLMConfigErrors:
    def test_missing_endpoint(self, monkeypatch):
        """TC-2 Step 1: Missing endpoint raises LLMConfigError."""
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)

        with pytest.raises(LLMConfigError, match="AZURE_OPENAI_ENDPOINT"):
            LLMConfig.from_env()

    def test_missing_both(self, monkeypatch):
        """Missing endpoint gives error."""
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)

        with pytest.raises(LLMConfigError, match="AZURE_OPENAI_ENDPOINT"):
            LLMConfig.from_env()


# ── TC-3: Prompt Builder Includes Key Fields ──────────────────────────

class TestBuildPrompt:
    def test_includes_key_fields(self):
        """TC-3 Step 1-2: Prompt includes title, SLA, dates, ownership, remediation."""
        messages = build_prompt(SAMPLE_ITEM)

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

        user_msg = messages[1]["content"]
        assert "Remediate Azure SQL TDE encryption" in user_msg
        assert "Azure SQL Database" in user_msg
        assert "Jane Doe" in user_msg
        assert "Enable TDE" in user_msg
        assert "2026-02-15" in user_msg

    def test_empty_remediation(self):
        """TC-3 Step 3: Empty remediation field handled gracefully."""
        item = {**SAMPLE_ITEM, "Remediation": ""}
        messages = build_prompt(item)
        user_msg = messages[1]["content"]
        assert "Remediation" in user_msg  # Label still present

    def test_large_remediation_truncated(self):
        """TC-3 Step 4: Very large remediation is truncated."""
        item = {**SAMPLE_ITEM, "Remediation": "x" * 5000}
        messages = build_prompt(item)
        user_msg = messages[1]["content"]
        assert "[truncated]" in user_msg


# ── TC-4: Prompt Builder Accepts Optional URL Content ─────────────────

class TestBuildPromptURLContent:
    def test_no_url_content(self):
        """TC-4 Step 1: No URL content → no URL section."""
        messages = build_prompt(SAMPLE_ITEM, url_content=None)
        user_msg = messages[1]["content"]
        assert "Additional Context from URLs" not in user_msg

    def test_with_url_content(self):
        """TC-4 Step 2: URL content included in prompt."""
        url_content = {"https://wiki.example.com/page": "This is the wiki page content."}
        messages = build_prompt(SAMPLE_ITEM, url_content=url_content)
        user_msg = messages[1]["content"]
        assert "Additional Context from URLs" in user_msg
        assert "wiki page content" in user_msg


# ── TC-5: Analyze Item Returns Structured Result ──────────────────────

class TestAnalyzeItem:
    def _make_config(self):
        return LLMConfig(
            endpoint="https://test.openai.azure.com/",
            deployment="gpt-4o",
        )

    def test_returns_structured_result(self, mocker):
        """TC-5 Step 1-3: Mock API returns well-formed response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "### 🎯 Mission\nRemediate TDE encryption.\n\n"
            "### ✅ Steps to Done\n1. Enable TDE.\n2. Verify.\n\n"
            "### 🔧 Resources Needing Repair\nAzure SQL DB instance-123.\n\n"
            "### ⚠️ Risk of Delay\nOut of SLA, compliance risk.\n"
        )
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 450
        mock_response.usage.completion_tokens = 200

        mock_client_cls = mocker.patch("sfi_reporter.llm_client.AzureOpenAI", create=True)
        # The import inside analyze_item does `from openai import AzureOpenAI`
        mocker.patch.dict("sys.modules", {
            "openai": MagicMock(AzureOpenAI=mock_client_cls),
            "azure.identity": MagicMock(),
        })
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = analyze_item(SAMPLE_ITEM, self._make_config())

        assert isinstance(result, AnalysisResult)
        assert result.action_item_id == "AI-12345"
        assert result.kpi_id == "KPI-67890"
        assert "Remediate TDE" in result.mission
        assert "Enable TDE" in result.steps_to_done
        assert "Azure SQL DB" in result.resources
        assert "compliance" in result.risk_of_delay
        assert result.prompt_tokens == 450
        assert result.completion_tokens == 200
        assert "T" in result.timestamp  # ISO format


# ── TC-6: Analyze Item Handles API Errors ─────────────────────────────

class TestAnalyzeItemErrors:
    def _make_config(self):
        return LLMConfig(
            endpoint="https://test.openai.azure.com/",
        )

    def test_api_connection_error(self, mocker):
        """TC-6 Step 1: Connection error raises LLMError."""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = ConnectionError("refused")
        mock_openai.AzureOpenAI.return_value = mock_client
        mocker.patch.dict("sys.modules", {
            "openai": mock_openai,
            "azure.identity": MagicMock(),
        })

        with pytest.raises(LLMError, match="ConnectionError"):
            analyze_item(SAMPLE_ITEM, self._make_config())

    def test_generic_exception(self, mocker):
        """TC-6 Step 4: Generic exception wrapped in LLMError."""
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("something broke")
        mock_openai.AzureOpenAI.return_value = mock_client
        mocker.patch.dict("sys.modules", {
            "openai": mock_openai,
            "azure.identity": MagicMock(),
        })

        with pytest.raises(LLMError, match="RuntimeError"):
            analyze_item(SAMPLE_ITEM, self._make_config())


# ── TC-17: LLM Config Repr Masks API Key ─────────────────────────────

class TestLLMConfigRepr:
    def test_repr_format(self):
        """TC-17 Step 1: repr() has expected fields."""
        config = LLMConfig(
            endpoint="https://test.openai.azure.com/",
        )
        r = repr(config)
        assert "test.openai.azure.com" in r
        assert "gpt-4o" in r


# ── Section parser tests ──────────────────────────────────────────────

class TestParseSections:
    def test_parses_all_sections(self):
        """All four sections are parsed from well-formed LLM output."""
        text = (
            "### 🎯 Mission\nDo the thing.\n\n"
            "### ✅ Steps to Done\n1. Step one.\n2. Step two.\n\n"
            "### 🔧 Resources Needing Repair\nResource A.\n\n"
            "### ⚠️ Risk of Delay\nBad things happen.\n"
        )
        sections = _parse_sections(text)
        assert "Do the thing" in sections["mission"]
        assert "Step one" in sections["steps_to_done"]
        assert "Resource A" in sections["resources"]
        assert "Bad things" in sections["risk_of_delay"]

    def test_empty_response(self):
        """Empty response returns empty sections."""
        sections = _parse_sections("")
        assert all(v == "" for v in sections.values())

    def test_no_headers(self):
        """Response without section headers returns empty sections."""
        sections = _parse_sections("Just some random text without headers.")
        assert all(v == "" for v in sections.values())


# ── Truncation tests ──────────────────────────────────────────────────

class TestTruncate:
    def test_short_text_unchanged(self):
        assert _truncate("hello", 100) == "hello"

    def test_long_text_truncated(self):
        result = _truncate("x" * 200, 50)
        assert len(result) < 200
        assert result.endswith("[truncated]")

    def test_empty_string(self):
        assert _truncate("", 100) == ""

    def test_none_value(self):
        assert _truncate(None, 100) == ""


# ── SFI-021: URL Content Enrichment Tests ─────────────────────────────

class TestFetchActionItemUrls:
    """TC-21-1 through TC-21-9: fetch_action_item_urls() function."""

    ITEM_ALL_URLS = {
        "id": "AI-99999",
        "title": "Test item",
        "ResourceURIs": "https://example.com/resource",
        "ActionWikiLink": "https://wiki.example.com/page",
        "CustomGroupingLink": "https://example.com/group",
        "AssetTypeLink0": "https://example.com/asset0",
        "AssetTypeLink1": "https://example.com/asset1",
        "AssetTypeLink2": "https://example.com/asset2",
    }

    def test_extracts_all_url_fields(self, mocker):
        """TC-21-1: All 6 URL fields are extracted and fetched."""
        from sfi_reporter.llm_client import fetch_action_item_urls

        mock_fetch = mocker.patch(
            "sfi_reporter.llm_client.fetch_url",
            return_value="content",
        )

        result = fetch_action_item_urls(self.ITEM_ALL_URLS)

        assert len(result) == 6, f"Expected 6 URLs fetched, got {len(result)}"
        assert mock_fetch.call_count == 6

    def test_skips_empty_url_fields(self, mocker):
        """TC-21-2: Only non-empty URL fields are fetched."""
        from sfi_reporter.llm_client import fetch_action_item_urls

        item = {
            "id": "AI-99999",
            "title": "Sparse item",
            "ActionWikiLink": "https://wiki.example.com/page",
            "ResourceURIs": "",
            "CustomGroupingLink": None,
        }

        mock_fetch = mocker.patch(
            "sfi_reporter.llm_client.fetch_url",
            return_value="wiki content",
        )

        result = fetch_action_item_urls(item)

        assert len(result) == 1, f"Expected 1 URL fetched for sparse item, got {len(result)}"
        assert mock_fetch.call_count == 1
        assert result["https://wiki.example.com/page"] == "wiki content"

    def test_timed_out_url_skipped(self, mocker):
        """TC-21-4: Timed-out URL is skipped, successful URL retained."""
        from sfi_reporter.llm_client import fetch_action_item_urls
        from llm_extender.exceptions import ProviderError

        def side_effect(url, **kwargs):
            if "wiki" in url:
                return "good content"
            raise ProviderError("timed out")

        mocker.patch(
            "sfi_reporter.llm_client.fetch_url",
            side_effect=side_effect,
        )

        item = {
            "ActionWikiLink": "https://wiki.example.com/page",
            "ResourceURIs": "https://example.com/timeout",
        }

        result = fetch_action_item_urls(item)

        assert len(result) == 1, "Timed out URL should be skipped, not raise"
        assert "https://wiki.example.com/page" in result

    def test_all_urls_fail_returns_empty(self, mocker):
        """TC-21-5: When all URLs fail, returns empty dict."""
        from sfi_reporter.llm_client import fetch_action_item_urls
        from llm_extender.exceptions import ProviderError

        mocker.patch(
            "sfi_reporter.llm_client.fetch_url",
            side_effect=ProviderError("error"),
        )

        item = {
            "ActionWikiLink": "https://fail1.example.com",
            "ResourceURIs": "https://fail2.example.com",
        }

        result = fetch_action_item_urls(item)

        assert result == {}, "All-fail scenario should return empty dict"

    def test_auth_gated_url_skipped(self, mocker):
        """TC-21-6: 401/403 auth-gated URLs are skipped gracefully."""
        from sfi_reporter.llm_client import fetch_action_item_urls
        from llm_extender.exceptions import ProviderError

        mocker.patch(
            "sfi_reporter.llm_client.fetch_url",
            side_effect=ProviderError("HTTP 403"),
        )

        item = {"ActionWikiLink": "https://auth-gated.example.com"}

        result = fetch_action_item_urls(item)

        assert result == {}, "Auth-gated URL should be skipped gracefully"

    def test_resource_uris_multiple_urls(self, mocker):
        """TC-21-8: ResourceURIs with multiple semicolon-separated URLs."""
        from sfi_reporter.llm_client import fetch_action_item_urls

        mocker.patch(
            "sfi_reporter.llm_client.fetch_url",
            return_value="content",
        )

        item = {"ResourceURIs": "https://a.com/1;https://b.com/2"}

        result = fetch_action_item_urls(item)

        assert len(result) == 2, f"Multiple ResourceURIs should be split and fetched, got {len(result)}"

    def test_no_url_fields_returns_empty(self, mocker):
        """TC-21-9: Item with no URL fields returns empty dict."""
        from sfi_reporter.llm_client import fetch_action_item_urls

        mock_fetch = mocker.patch(
            "sfi_reporter.llm_client.fetch_url",
            return_value="content",
        )

        item = {"id": "AI-99999", "title": "No URLs here"}

        result = fetch_action_item_urls(item)

        assert result == {}, "Item with no URLs should return empty dict without fetching"
        assert mock_fetch.call_count == 0


class TestBuildPromptURLContentTruncation:
    """TC-21-7: URL content truncation in prompt."""

    def test_large_url_content_truncated_in_prompt(self):
        """TC-21-7: Large URL content is truncated in the prompt."""
        url_content = {"https://example.com/big": "x" * 5000}
        messages = build_prompt(SAMPLE_ITEM, url_content=url_content)
        user_msg = messages[1]["content"]

        assert "Additional Context from URLs" in user_msg
        assert "[truncated]" in user_msg, "Large URL content should be truncated in prompt"


class TestAnalyzeItemURLContent:
    """TC-21-10: analyze_item passes url_content through."""

    def test_url_content_flows_through(self, mocker):
        """TC-21-10: url_content is passed through to the prompt."""
        config = LLMConfig(
            endpoint="https://test.openai.azure.com/",
            deployment="gpt-4o",
        )

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "### 🎯 Mission\nDo stuff.\n\n"
            "### ✅ Steps to Done\n1. Step.\n\n"
            "### 🔧 Resources Needing Repair\nRes.\n\n"
            "### ⚠️ Risk of Delay\nRisk.\n"
        )
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 500
        mock_response.usage.completion_tokens = 200

        mock_client_cls = mocker.patch("sfi_reporter.llm_client.AzureOpenAI", create=True)
        mocker.patch.dict("sys.modules", {
            "openai": MagicMock(AzureOpenAI=mock_client_cls),
            "azure.identity": MagicMock(),
        })
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_cls.return_value = mock_client

        url_content = {"https://wiki.example.com": "Wiki page about remediation steps."}

        result = analyze_item(SAMPLE_ITEM, config, url_content=url_content)

        # Verify the prompt sent to OpenAI contained URL content
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs.get("messages") or call_args[1].get("messages")
        user_msg = messages[1]["content"]

        assert "Additional Context from URLs" in user_msg, "url_content should flow through analyze_item to the prompt"
        assert "Wiki page about remediation" in user_msg
