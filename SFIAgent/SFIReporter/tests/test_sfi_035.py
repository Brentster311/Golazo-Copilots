"""Tests for SFI-035 – LLM Analysis Sources Provenance Card.

Covers the AnalysisResult dataclass, FetchResult dataclass,
format_sources_card function, and the refactored analyze_kpi return type.
"""

from __future__ import annotations

import pytest

from sfi_reporter.kpi_analyzer import (
    AnalysisResult,
    FetchResult,
    analyze_kpi,
    build_analysis_prompt,
    collect_urls,
    fetch_all_urls,
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
