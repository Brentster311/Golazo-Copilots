"""Tests for fact extractor (LLM integration)."""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ees.exceptions import LLMError
from ees.fact_extractor import FactExtractor
from ees.models import Fact, LLMResponse, OntologyNoun, OntologyProperty


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_llm_response(fixtures_dir):
    with open(fixtures_dir / "mock_llm_response.json") as f:
        return json.load(f)


@pytest.fixture
def mock_llm_empty(fixtures_dir):
    with open(fixtures_dir / "mock_llm_empty.json") as f:
        return json.load(f)


def _make_mock_openai_response(content: str):
    """Create a mock that mimics Azure OpenAI chat completion response."""
    mock_message = MagicMock()
    mock_message.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


class TestFactExtractorHappyPath:
    """TC-01: Extract facts from incident text via LLM."""

    def test_extract_facts(self, mock_llm_response):
        """TC-01: LLM returns valid facts."""
        extractor = FactExtractor.__new__(FactExtractor)
        extractor.client = MagicMock()
        extractor.deployment = "gpt-4o"

        mock_resp = _make_mock_openai_response(json.dumps(mock_llm_response))
        extractor.client.chat.completions.create.return_value = mock_resp

        result = extractor.extract("Some incident text", [])

        assert isinstance(result, LLMResponse)
        assert len(result.facts) == 3
        assert result.facts[0].noun == "Server"
        assert result.facts[0].operator == ">"
        assert result.root_cause == "Resource Exhaustion"
        assert len(result.rules) == 1

    def test_extract_with_ontology_context(self, mock_llm_response):
        """LLM receives ontology as context."""
        extractor = FactExtractor.__new__(FactExtractor)
        extractor.client = MagicMock()
        extractor.deployment = "gpt-4o"

        mock_resp = _make_mock_openai_response(json.dumps(mock_llm_response))
        extractor.client.chat.completions.create.return_value = mock_resp

        ontology = [OntologyNoun("Server", [OntologyProperty("CPUUsage", "numeric")])]
        result = extractor.extract("text", ontology)

        # Verify ontology was included in the prompt
        call_args = extractor.client.chat.completions.create.call_args
        messages = call_args.kwargs.get("messages") or call_args[1].get("messages")
        prompt_text = str(messages)
        assert "Server" in prompt_text or "CPUUsage" in prompt_text


class TestFactExtractorEmptyResponse:
    """TC-04: LLM returns no facts."""

    def test_empty_facts(self, mock_llm_empty):
        extractor = FactExtractor.__new__(FactExtractor)
        extractor.client = MagicMock()
        extractor.deployment = "gpt-4o"

        mock_resp = _make_mock_openai_response(json.dumps(mock_llm_empty))
        extractor.client.chat.completions.create.return_value = mock_resp

        result = extractor.extract("Some text", [])
        assert len(result.facts) == 0
        assert result.root_cause is None


class TestFactExtractorLLMFailure:
    """TC-25: LLM API failure."""

    def test_api_unreachable(self):
        """TC-25: LLM API call fails."""
        extractor = FactExtractor.__new__(FactExtractor)
        extractor.client = MagicMock()
        extractor.deployment = "gpt-4o"

        extractor.client.chat.completions.create.side_effect = Exception("Connection refused")

        with pytest.raises(LLMError, match="LLM API call failed"):
            extractor.extract("text", [])

    def test_malformed_response_retries(self):
        """TC-25 related (MJ-2): Malformed LLM response triggers retry, then fails."""
        extractor = FactExtractor.__new__(FactExtractor)
        extractor.client = MagicMock()
        extractor.deployment = "gpt-4o"

        # Both attempts return garbage
        bad_resp = _make_mock_openai_response("not json at all {{{")
        extractor.client.chat.completions.create.return_value = bad_resp

        with pytest.raises(LLMError, match="Could not parse LLM response"):
            extractor.extract("text", [])
        # Should have been called twice (initial + retry)
        assert extractor.client.chat.completions.create.call_count == 2


class TestFactExtractorAuth:
    """Authentication uses ChainedTokenCredential per best practices."""

    @patch("ees.fact_extractor.AzureCliCredential")
    @patch("ees.fact_extractor.ManagedIdentityCredential")
    @patch("ees.fact_extractor.ChainedTokenCredential")
    @patch("ees.fact_extractor.AzureOpenAI")
    def test_uses_chained_credential(self, mock_aoai, mock_chained, mock_msi, mock_cli):
        """Auth uses ChainedTokenCredential(AzureCli, MSI), NOT DefaultAzureCredential."""
        import os
        env = {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "gpt-4o",
        }
        with patch.dict(os.environ, env):
            extractor = FactExtractor()

        mock_cli.assert_called_once()
        mock_msi.assert_called_once()
        mock_chained.assert_called_once()
        # Verify DefaultAzureCredential is NOT used
        mock_aoai.assert_called_once()
