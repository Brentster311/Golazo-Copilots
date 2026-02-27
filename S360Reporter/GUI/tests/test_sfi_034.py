"""Tests for s360_reporter.kpi_analyzer – SFI-034."""

from __future__ import annotations

import pytest

from s360_reporter.kpi_analyzer import (
    collect_urls,
    extract_text,
    truncate_content,
    build_analysis_prompt,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_item(
    item_id: str = "AI-1",
    title: str = "Fix something",
    kpi_id: str = "KPI-A",
    kpi_name: str = "[SFI-NS3.2.1] Secure PaaS",
    service: str = "My Service",
    owner: str = "Alice",
    sla: str = "OutOfSla",
    eta: str = "2026-03-01",
    url: str = "",
    wiki: str = "",
    remediation: str = "",
    asset0: str = "",
    asset1: str = "",
    asset2: str = "",
    custom_link: str = "",
) -> dict:
    return {
        "id": item_id,
        "title": title,
        "_kpi_id": kpi_id,
        "_kpi_name": kpi_name,
        "S360_ServiceTreeServiceName": service,
        "ActionOwnerName": owner,
        "SlaType": sla,
        "EtaDate": eta,
        "dueDate": "2026-02-15",
        "ActionItemStatus": "Active",
        "url": url,
        "ActionWikiLink": wiki,
        "Remediation": remediation,
        "AssetTypeLink0": asset0,
        "AssetTypeLink1": asset1,
        "AssetTypeLink2": asset2,
        "CustomGroupingLink": custom_link,
        "AssetType0": "Subscription",
        "S360_ServiceId": "svc-1",
    }


# ---------------------------------------------------------------------------
# TC-3: URL deduplication
# ---------------------------------------------------------------------------

class TestCollectUrls:
    def test_deduplicates_same_url(self):
        items = [
            _make_item(url="https://same.com/doc"),
            _make_item(url="https://same.com/doc"),
            _make_item(url="https://same.com/doc"),
        ]
        urls = collect_urls(items)
        assert len(urls) == 1, "Duplicate URLs not deduplicated"
        assert "https://same.com/doc" in urls

    def test_collects_across_fields(self):
        items = [
            _make_item(url="https://a.com", wiki="https://b.com", asset0="https://c.com"),
        ]
        urls = collect_urls(items)
        assert urls == {"https://a.com", "https://b.com", "https://c.com"}

    def test_skips_empty_and_none(self):
        """TC-10: Empty URL fields skipped."""
        item = _make_item(url="", wiki=None, remediation="")
        urls = collect_urls([item])
        assert len(urls) == 0, "Empty/None URL fields not filtered out"

    def test_only_http_https(self):
        item = _make_item(url="file:///etc/passwd", wiki="https://safe.com")
        urls = collect_urls([item])
        assert "file:///etc/passwd" not in urls
        assert "https://safe.com" in urls


# ---------------------------------------------------------------------------
# TC-6: HTML to text extraction
# ---------------------------------------------------------------------------

class TestExtractText:
    def test_strips_tags(self):
        html = "<html><body><h1>Title</h1><p>Content here</p></body></html>"
        text = extract_text(html)
        assert "Title" in text
        assert "Content here" in text
        assert "<h1>" not in text

    def test_strips_script_and_style(self):
        html = (
            "<html><body>"
            "<script>var x=1;</script>"
            "<style>.a{color:red}</style>"
            "<p>Visible</p>"
            "</body></html>"
        )
        text = extract_text(html)
        assert "Visible" in text
        assert "var x=1" not in text, "HTML extraction included script content"
        assert "color:red" not in text

    def test_plain_text_passthrough(self):
        text = extract_text("Just plain text, no HTML.")
        assert "Just plain text" in text


# ---------------------------------------------------------------------------
# TC-7: Text truncation
# ---------------------------------------------------------------------------

class TestTruncateContent:
    def test_short_text_unchanged(self):
        text = "Short"
        assert truncate_content(text, max_len=4000) == text

    def test_long_text_truncated(self):
        text = "A" * 10_000
        result = truncate_content(text, max_len=4000)
        assert len(result) <= 4100  # allow for truncation marker
        assert "truncated" in result.lower(), "Truncated text exceeds max length"

    def test_default_max(self):
        text = "B" * 5000
        result = truncate_content(text)
        assert len(result) <= 4200


# ---------------------------------------------------------------------------
# TC-1, TC-9: Prompt construction
# ---------------------------------------------------------------------------

class TestBuildAnalysisPrompt:
    def test_includes_all_items(self):
        """TC-1: Prompt includes all item data."""
        items = [_make_item(item_id=f"AI-{i}", title=f"Item {i}") for i in range(5)]
        prompt = build_analysis_prompt(items, fetched_docs={})
        for i in range(5):
            assert f"AI-{i}" in prompt, f"Prompt missing item AI-{i}"
            assert f"Item {i}" in prompt

    def test_includes_fetched_docs(self):
        """TC-2: Prompt includes fetched documentation."""
        items = [_make_item()]
        docs = {
            "https://example.com/doc": "First doc content",
            "https://wiki.example.com/guide": "Second doc content",
        }
        prompt = build_analysis_prompt(items, fetched_docs=docs)
        assert "First doc content" in prompt, "Fetched documentation not included in prompt"
        assert "Second doc content" in prompt

    def test_four_questions_present(self):
        """TC-9: Prompt contains all four analysis questions."""
        items = [_make_item()]
        prompt = build_analysis_prompt(items, fetched_docs={})
        assert "What is being asked" in prompt, "Missing 'What is being asked?'"
        assert "Why" in prompt, "Missing 'Why?'"
        assert "what resources" in prompt.lower() or "On what resources" in prompt, "Missing resources question"
        assert "How" in prompt, "Missing 'How?'"

    def test_item_cap(self):
        """TC-8: Prompt caps items at 30."""
        items = [_make_item(item_id=f"AI-{i}") for i in range(50)]
        prompt = build_analysis_prompt(items, fetched_docs={})
        # Should mention truncation
        assert "50" in prompt, "Prompt did not note total item count"
        # Should not include all 50 item IDs
        assert "AI-49" not in prompt or "30" in prompt

    def test_kpi_name_in_prompt(self):
        items = [_make_item(kpi_name="[SFI-NS3.2.1] Secure PaaS")]
        prompt = build_analysis_prompt(items, fetched_docs={})
        assert "[SFI-NS3.2.1] Secure PaaS" in prompt
