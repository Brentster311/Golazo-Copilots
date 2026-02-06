"""Tests for query_builder module."""
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from sfi_reporter.query_builder import (
    QueryClause,
    evaluate_clauses,
    get_field_type,
    resolve_date_expression,
    aggregate_results_by_program,
    save_clause_cache,
    load_clause_cache,
    clear_clause_cache,
    CLAUSE_CACHE_FILENAME,
)


# --- Sample data fixtures ---

@pytest.fixture
def sample_items():
    """Sample action items for testing."""
    return [
        {
            "title": "Fix security vulnerability",
            "ActionOwnerName": "John Doe",
            "S360_ServiceTreeServiceName": "Service-A",
            "SlaType": "OutOfSla",
            "dueDate": "2026-02-10T00:00:00Z",
            "EtaDate": "2026-02-08T00:00:00Z",
            "S360_ProgramIds": ["prog-1", "prog-2"],
            "_kpi_id": "kpi-1",
        },
        {
            "title": "Update compliance scan",
            "ActionOwnerName": "Jane Smith",
            "S360_ServiceTreeServiceName": "Service-B",
            "SlaType": "InSla",
            "dueDate": "2026-03-01T00:00:00Z",
            "EtaDate": "2026-02-25T00:00:00Z",
            "S360_ProgramIds": ["prog-1"],
            "_kpi_id": "kpi-2",
        },
        {
            "title": "USSec Shadow Action Item",
            "ActionOwnerName": "John Doe",
            "S360_ServiceTreeServiceName": "Service-A",
            "SlaType": "InSla",
            "dueDate": "2026-04-01T00:00:00Z",
            "EtaDate": None,
            "S360_ProgramIds": ["prog-3"],
            "_kpi_id": "kpi-1",
        },
        {
            "title": "Patch AKS cluster",
            "ActionOwnerName": "John Doe",
            "S360_ServiceTreeServiceName": "Service-C",
            "SlaType": "OutOfSla",
            "dueDate": "2026-01-15T00:00:00Z",
            "EtaDate": "",
            "S360_ProgramIds": ["prog-2"],
            "_kpi_id": "kpi-3",
        },
    ]


@pytest.fixture
def program_names():
    """Program name lookup."""
    return {
        "prog-1": "Security Compliance",
        "prog-2": "Infrastructure Hardening",
        "prog-3": "Shadow Program",
    }


@pytest.fixture
def tmp_cache_dir(tmp_path):
    """Temporary cache directory."""
    return tmp_path


# --- TC-01: Basic string equals filter ---

class TestEvaluateClauses:

    def test_string_equals(self, sample_items):
        """TC-01: String equals filter matches case-insensitively."""
        clauses = [QueryClause("Where", "ActionOwnerName", "equals", "John Doe")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 3
        assert all(item["ActionOwnerName"] == "John Doe" for item in result)

    def test_string_equals_case_insensitive(self, sample_items):
        """TC-01 variant: Case-insensitive matching."""
        clauses = [QueryClause("Where", "ActionOwnerName", "equals", "john doe")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 3

    def test_string_contains(self, sample_items):
        """TC-02: String contains filter."""
        clauses = [QueryClause("Where", "title", "contains", "compliance")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 1
        assert "compliance" in result[0]["title"].lower()

    def test_string_not_equals(self, sample_items):
        """TC-03: String not equals filter."""
        clauses = [QueryClause("Where", "SlaType", "not equals", "OutOfSla")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert all(item["SlaType"] != "OutOfSla" for item in result)
        assert len(result) == 2

    def test_string_not_contains(self, sample_items):
        """String not contains filter."""
        clauses = [QueryClause("Where", "title", "not contains", "shadow")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 3

    def test_date_on_or_before(self, sample_items):
        """TC-04: Date on or before filter."""
        clauses = [QueryClause("Where", "dueDate", "on or before", "2026-02-13")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        # Items due on or before Feb 13: item 0 (Feb 10) and item 3 (Jan 15)
        assert len(result) == 2

    def test_date_on_or_after(self, sample_items):
        """Date on or after filter."""
        clauses = [QueryClause("Where", "dueDate", "on or after", "2026-03-01")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        # Items due on or after Mar 1: item 1 (Mar 1) and item 2 (Apr 1)
        assert len(result) == 2

    def test_date_equals(self, sample_items):
        """Date equals filter."""
        clauses = [QueryClause("Where", "dueDate", "equals", "2026-02-10")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 1

    def test_today_expression(self, sample_items):
        """TC-05: @Today - N expression."""
        # Set a fixed 'today' for predictability
        fixed_today = datetime(2026, 2, 10)
        with patch("sfi_reporter.query_builder._get_today", return_value=fixed_today):
            clauses = [QueryClause("Where", "dueDate", "on or before", "@Today - 0")]
            result = evaluate_clauses(sample_items, clauses, include_ussec=True)
            # Due on or before Feb 10: item 0 (Feb 10) and item 3 (Jan 15)
            assert len(result) == 2

    def test_today_minus_days(self, sample_items):
        """TC-05 variant: @Today - 7."""
        fixed_today = datetime(2026, 2, 20)
        with patch("sfi_reporter.query_builder._get_today", return_value=fixed_today):
            clauses = [QueryClause("Where", "dueDate", "on or before", "@Today - 7")]
            result = evaluate_clauses(sample_items, clauses, include_ussec=True)
            # Due on or before Feb 13: item 0 (Feb 10) and item 3 (Jan 15)
            assert len(result) == 2

    def test_multiple_and_clauses(self, sample_items):
        """TC-06: Multiple And clauses (both must match)."""
        clauses = [
            QueryClause("Where", "SlaType", "equals", "OutOfSla"),
            QueryClause("And", "ActionOwnerName", "equals", "John Doe"),
        ]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 2
        assert all(
            item["SlaType"] == "OutOfSla" and item["ActionOwnerName"] == "John Doe"
            for item in result
        )

    def test_or_clause(self, sample_items):
        """TC-07: Or clause (either matches)."""
        clauses = [
            QueryClause("Where", "S360_ServiceTreeServiceName", "equals", "Service-A"),
            QueryClause("Or", "S360_ServiceTreeServiceName", "equals", "Service-B"),
        ]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 3  # 2 from Service-A + 1 from Service-B

    def test_ussec_exclusion(self, sample_items):
        """TC-08: USSec Shadow exclusion when include_ussec=False."""
        result = evaluate_clauses(sample_items, [], include_ussec=False)
        assert len(result) == 3
        assert not any("ussec shadow" in item["title"].lower() for item in result)

    def test_ussec_inclusion(self, sample_items):
        """TC-09: USSec Shadow included when include_ussec=True."""
        result = evaluate_clauses(sample_items, [], include_ussec=True)
        assert len(result) == 4

    def test_empty_clause_skipped(self, sample_items):
        """TC-10: Incomplete clause is skipped."""
        clauses = [QueryClause("Where", "", "", "")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 4  # All items returned

    def test_no_clauses_returns_all(self, sample_items):
        """TC-11: No clauses returns all items (minus USSec if excluded)."""
        result = evaluate_clauses(sample_items, [], include_ussec=True)
        assert len(result) == 4

    def test_list_field_contains(self, sample_items):
        """TC-18: Contains on list-valued field checks elements."""
        clauses = [QueryClause("Where", "S360_ProgramIds", "contains", "prog-1")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        assert len(result) == 2  # Items 0 and 1 have prog-1

    def test_none_date_field_excluded(self, sample_items):
        """TC-19: None date field doesn't match date comparisons."""
        clauses = [QueryClause("Where", "EtaDate", "on or before", "2026-12-31")]
        result = evaluate_clauses(sample_items, clauses, include_ussec=True)
        # Item 2 has EtaDate=None, item 3 has EtaDate="" — both should be excluded
        assert len(result) == 2


# --- TC-12/13: Field type detection ---

class TestGetFieldType:

    def test_date_fields(self):
        """TC-12: Date fields detected correctly."""
        assert get_field_type("dueDate") == "date"
        assert get_field_type("EtaDate") == "date"
        assert get_field_type("createdDate") == "date"
        assert get_field_type("closedDate") == "date"
        assert get_field_type("OriginalPublishTime") == "date"

    def test_string_fields(self):
        """TC-13: Non-date fields default to string."""
        assert get_field_type("title") == "string"
        assert get_field_type("SlaType") == "string"
        assert get_field_type("ActionOwnerName") == "string"
        assert get_field_type("S360_ProgramIds") == "string"


# --- TC-14/15: Date expression parsing ---

class TestResolveDateExpression:

    def test_today_minus_7(self):
        """TC-14: @Today - 7 resolves correctly."""
        fixed_today = datetime(2026, 2, 10)
        with patch("sfi_reporter.query_builder._get_today", return_value=fixed_today):
            result = resolve_date_expression("@Today - 7")
            assert result == datetime(2026, 2, 3)

    def test_today_minus_0(self):
        """TC-14: @Today - 0 resolves to today."""
        fixed_today = datetime(2026, 2, 10)
        with patch("sfi_reporter.query_builder._get_today", return_value=fixed_today):
            result = resolve_date_expression("@Today - 0")
            assert result == datetime(2026, 2, 10)

    def test_today_minus_30(self):
        """TC-14: @Today - 30 resolves correctly."""
        fixed_today = datetime(2026, 2, 10)
        with patch("sfi_reporter.query_builder._get_today", return_value=fixed_today):
            result = resolve_date_expression("@Today - 30")
            assert result == datetime(2026, 1, 11)

    def test_invalid_expression(self):
        """TC-15: Invalid expression returns None."""
        assert resolve_date_expression("not a date") is None

    def test_invalid_tomorrow(self):
        """TC-15: @Tomorrow not supported."""
        assert resolve_date_expression("@Tomorrow - 5") is None

    def test_plain_date_string(self):
        """Plain date string parses correctly."""
        result = resolve_date_expression("2026-02-10")
        assert result == datetime(2026, 2, 10)


# --- TC-16/17: Clause cache ---

class TestClauseCache:

    def test_save_load_roundtrip(self, tmp_cache_dir):
        """TC-16: Save and load clauses round-trips correctly."""
        clauses = [
            QueryClause("Where", "SlaType", "equals", "OutOfSla"),
            QueryClause("And", "ActionOwnerName", "contains", "John"),
        ]
        save_clause_cache(clauses, include_ussec=False, cache_dir=tmp_cache_dir)
        loaded_clauses, loaded_ussec = load_clause_cache(cache_dir=tmp_cache_dir)

        assert len(loaded_clauses) == 2
        assert loaded_clauses[0].connector == "Where"
        assert loaded_clauses[0].field == "SlaType"
        assert loaded_clauses[0].operator == "equals"
        assert loaded_clauses[0].value == "OutOfSla"
        assert loaded_clauses[1].connector == "And"
        assert loaded_ussec is False

    def test_clear_deletes_file(self, tmp_cache_dir):
        """TC-17: Clear deletes the cache file."""
        clauses = [QueryClause("Where", "title", "contains", "test")]
        save_clause_cache(clauses, include_ussec=True, cache_dir=tmp_cache_dir)
        assert (tmp_cache_dir / CLAUSE_CACHE_FILENAME).exists()

        clear_clause_cache(cache_dir=tmp_cache_dir)
        assert not (tmp_cache_dir / CLAUSE_CACHE_FILENAME).exists()

    def test_load_missing_file(self, tmp_cache_dir):
        """Load from missing file returns empty defaults."""
        clauses, include_ussec = load_clause_cache(cache_dir=tmp_cache_dir)
        assert clauses == []
        assert include_ussec is False

    def test_load_corrupt_file(self, tmp_cache_dir):
        """Load from corrupt file returns empty defaults."""
        cache_file = tmp_cache_dir / CLAUSE_CACHE_FILENAME
        cache_file.write_text("not json!!!", encoding="utf-8")
        clauses, include_ussec = load_clause_cache(cache_dir=tmp_cache_dir)
        assert clauses == []
        assert include_ussec is False


# --- TC-20: Aggregate by program ---

class TestAggregateByProgram:

    def test_aggregate_results(self, sample_items, program_names):
        """TC-20: Aggregate filtered items by program."""
        # Exclude USSec item for realistic scenario
        filtered = [i for i in sample_items if "ussec shadow" not in i["title"].lower()]
        result = aggregate_results_by_program(filtered, program_names)

        # prog-1 (Security Compliance): items 0, 1
        assert "Security Compliance" in result
        sc = result["Security Compliance"]
        assert sc["count"] == 2
        assert sc["sla"] == 1  # item 0 is OutOfSla
        # invalid_eta: item 0 EtaDate is future (valid), item 1 EtaDate is future (valid)
        # so depends on current time — check it's a number
        assert isinstance(sc["invalid_eta"], int)

        # prog-2 (Infrastructure Hardening): items 0, 3
        assert "Infrastructure Hardening" in result
        ih = result["Infrastructure Hardening"]
        assert ih["count"] == 2
        assert ih["sla"] == 2  # both OutOfSla

    def test_aggregate_unknown_program(self, sample_items):
        """Programs not in lookup show as ID."""
        filtered = [sample_items[0]]  # Has prog-1, prog-2
        result = aggregate_results_by_program(filtered, {})
        # Should use raw IDs since no lookup
        assert "prog-1" in result or "prog-2" in result
