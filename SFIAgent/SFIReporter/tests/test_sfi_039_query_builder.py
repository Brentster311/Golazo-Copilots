"""SFI-039 – Additional query_builder tests targeting ≥70% coverage.

Covers:
  • Pure logic edge cases (get_field_type suffix, @Today, _parse_item_date,
    _match_clause with _resolved_program, list operators, None date, Or connector,
    USSec filtering, aggregate edge cases, cache corruption/IOError)
  • ClauseRow Tk widget lifecycle (init, field selection, get/set clause, destroy)
  • QueryBuilder Tk widget lifecycle (init, enrich, field metadata,
    add/remove clause rows, run query, clear all, apply filter, load cached)
"""
import tkinter as tk
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from sfi_reporter.query_builder import (
    QueryClause,
    get_field_type,
    resolve_date_expression,
    _parse_item_date,
    _match_clause,
    _match_string_clause,
    _match_date_clause,
    evaluate_clauses,
    aggregate_results_by_program,
    save_clause_cache,
    load_clause_cache,
    clear_clause_cache,
    ClauseRow,
    QueryBuilder,
    FILTER_FIELDS,
    COLUMN_DISPLAY_NAMES,
    STRING_OPERATORS,
    DATE_OPERATORS,
    CLAUSE_CACHE_FILENAME,
)

# ---------------------------------------------------------------------------
# Tk root fixture (one per module — hidden)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def tk_root():
    """Create a single Tk root for the module, don't show it."""
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


# ---------------------------------------------------------------------------
# Shared data helpers
# ---------------------------------------------------------------------------

def _make_items():
    """Standard set of action items for tests."""
    return [
        {
            "title": "Fix security vulnerability",
            "ActionOwnerName": "John Doe",
            "S360_ServiceTreeServiceName": "Svc-A",
            "SlaType": "OutOfSla",
            "dueDate": "2026-02-10T00:00:00Z",
            "EtaDate": "2026-02-08T00:00:00Z",
            "S360_ProgramIds": ["prog-1", "prog-2"],
            "myExceptionStatus": "",
        },
        {
            "title": "Update compliance scan",
            "ActionOwnerName": "Jane Smith",
            "S360_ServiceTreeServiceName": "Svc-B",
            "SlaType": "InSla",
            "dueDate": "2026-03-01T00:00:00Z",
            "EtaDate": "2026-02-25T00:00:00Z",
            "S360_ProgramIds": ["prog-1"],
            "myExceptionStatus": "Approved",
        },
        {
            "title": "USSec Shadow Action Item - baseline",
            "ActionOwnerName": "John Doe",
            "S360_ServiceTreeServiceName": "Svc-A",
            "SlaType": "InSla",
            "dueDate": "2026-04-01T00:00:00Z",
            "EtaDate": None,
            "S360_ProgramIds": ["prog-3"],
            "myExceptionStatus": "",
        },
        {
            "title": "Patch AKS cluster",
            "ActionOwnerName": "John Doe",
            "S360_ServiceTreeServiceName": "Svc-C",
            "SlaType": "OutOfSla",
            "dueDate": "2026-01-15T00:00:00Z",
            "EtaDate": "",
            "S360_ProgramIds": ["prog-2"],
            "myExceptionStatus": "",
        },
    ]


_PROGRAM_NAMES = {
    "prog-1": "Security Compliance",
    "prog-2": "Infrastructure Hardening",
    "prog-3": "Shadow Program",
}
_SERVICE_NAMES = {"Svc-A": "Service A", "Svc-B": "Service B"}
_SERVICE_OWNERS = {"Svc-A": ["Alice Owner"], "Svc-B": ["Bob Owner"]}


# ===================================================================
# 1. Pure logic – edge-case coverage
# ===================================================================

class TestGetFieldTypeSuffix:
    """Cover line 106 — suffix-based date detection."""

    def test_field_ending_in_date_suffix(self):
        assert get_field_type("SomeCustomDate") == "date"

    def test_field_ending_in_time_suffix(self):
        assert get_field_type("LastModifiedTime") == "date"

    def test_field_ending_in_eta_suffix(self):
        assert get_field_type("S360_TwoWayEta") == "date"

    def test_non_date_field(self):
        assert get_field_type("randomField") == "string"


class TestResolveDateExpressionEdge:
    """Cover line 124 — @Today expressions."""

    def test_at_today_minus_zero(self):
        fixed = datetime(2026, 3, 1)
        with patch("sfi_reporter.query_builder._get_today", return_value=fixed):
            assert resolve_date_expression("@Today - 0") == fixed

    def test_at_today_minus_positive(self):
        fixed = datetime(2026, 3, 10)
        with patch("sfi_reporter.query_builder._get_today", return_value=fixed):
            assert resolve_date_expression("@Today - 5") == datetime(2026, 3, 5)

    def test_empty_string_returns_none(self):
        assert resolve_date_expression("") is None

    def test_none_input_returns_none(self):
        assert resolve_date_expression(None) is None

    def test_plain_iso_with_tz(self):
        result = resolve_date_expression("2026-05-01T12:00:00Z")
        assert result == datetime(2026, 5, 1)

    def test_garbage_input(self):
        assert resolve_date_expression("not-a-date") is None


class TestParseItemDate:
    """Cover lines 156-157 — empty / None / whitespace."""

    def test_none_returns_none(self):
        assert _parse_item_date(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_item_date("") is None

    def test_whitespace_only_returns_none(self):
        assert _parse_item_date("   ") is None

    def test_valid_iso_date(self):
        result = _parse_item_date("2026-02-10T14:30:00Z")
        assert result == datetime(2026, 2, 10)

    def test_invalid_string(self):
        assert _parse_item_date("xyz") is None


class TestMatchClauseResolvedProgram:
    """Cover line 174 — _resolved_program path in _match_clause."""

    def test_uses_resolved_program_when_present(self):
        item = {
            "S360_ProgramIds": ["prog-1"],
            "_resolved_program": "Security Compliance",
        }
        clause = QueryClause("Where", "S360_ProgramIds", "equals", "Security Compliance")
        assert _match_clause(item, clause) is True

    def test_falls_back_to_raw_when_no_resolved(self):
        item = {"S360_ProgramIds": ["prog-1"]}
        clause = QueryClause("Where", "S360_ProgramIds", "contains", "prog-1")
        assert _match_clause(item, clause) is True


class TestMatchStringClauseList:
    """Cover lines 193-235 — list-valued field with all 4 operators."""

    def test_list_equals(self):
        assert _match_string_clause(["alpha", "beta"], "equals", "Alpha") is True

    def test_list_equals_no_match(self):
        assert _match_string_clause(["alpha", "beta"], "equals", "gamma") is False

    def test_list_not_equals(self):
        assert _match_string_clause(["alpha", "beta"], "not equals", "gamma") is True

    def test_list_not_equals_false(self):
        assert _match_string_clause(["alpha"], "not equals", "alpha") is False

    def test_list_contains(self):
        assert _match_string_clause(["alpha", "beta"], "contains", "lph") is True

    def test_list_contains_no_match(self):
        assert _match_string_clause(["alpha", "beta"], "contains", "xyz") is False

    def test_list_not_contains(self):
        assert _match_string_clause(["alpha", "beta"], "not contains", "xyz") is True

    def test_list_not_contains_false(self):
        assert _match_string_clause(["alpha"], "not contains", "alph") is False

    def test_list_unknown_operator(self):
        assert _match_string_clause(["alpha"], "starts with", "a") is False

    def test_scalar_unknown_operator(self):
        assert _match_string_clause("alpha", "starts with", "a") is False

    def test_none_value_becomes_empty(self):
        assert _match_string_clause(None, "equals", "") is True


class TestMatchDateClauseEdge:
    """Cover line 235+ — None / unparseable dates."""

    def test_none_item_date_returns_false(self):
        assert _match_date_clause(None, "on or before", "2026-01-01") is False

    def test_empty_item_date_returns_false(self):
        assert _match_date_clause("", "on or before", "2026-01-01") is False

    def test_bad_target_returns_false(self):
        assert _match_date_clause("2026-01-01", "on or before", "nope") is False

    def test_unknown_operator_returns_false(self):
        assert _match_date_clause("2026-01-01", "before", "2026-02-01") is False


class TestEvaluateClausesEdge:
    """Cover lines 312, 315 — USSec filtering, Or connector."""

    def test_ussec_excluded(self):
        items = _make_items()
        result = evaluate_clauses(items, [], include_ussec=False)
        assert len(result) == 3
        assert all("ussec shadow" not in it["title"].lower() for it in result)

    def test_or_connector(self):
        items = _make_items()
        clauses = [
            QueryClause("Where", "ActionOwnerName", "equals", "Jane Smith"),
            QueryClause("Or", "SlaType", "equals", "OutOfSla"),
        ]
        result = evaluate_clauses(items, clauses, include_ussec=True)
        # Jane Smith (1) OR OutOfSla (2) — but item 1 matches both, total = 3
        assert len(result) == 3

    def test_incomplete_clause_skipped(self):
        items = _make_items()
        clauses = [QueryClause("Where", "", "", "")]
        assert len(evaluate_clauses(items, clauses)) == 4


class TestAggregateEdge:
    """Cover lines 348, 361-362, 377 — non-list program_ids, no program."""

    def test_scalar_program_id(self):
        items = [{"S360_ProgramIds": "prog-1", "SlaType": "InSla", "EtaDate": "2099-01-01T00:00:00Z"}]
        result = aggregate_results_by_program(items, _PROGRAM_NAMES)
        assert "Security Compliance" in result
        assert result["Security Compliance"]["count"] == 1

    def test_empty_program_none(self):
        items = [{"S360_ProgramIds": None, "SlaType": "InSla", "EtaDate": "2099-01-01T00:00:00Z"}]
        result = aggregate_results_by_program(items, _PROGRAM_NAMES)
        assert "(No Program)" in result

    def test_empty_list(self):
        items = [{"S360_ProgramIds": [], "SlaType": "OutOfSla", "EtaDate": None}]
        result = aggregate_results_by_program(items, _PROGRAM_NAMES)
        assert "(No Program)" in result
        assert result["(No Program)"]["sla"] == 1
        assert result["(No Program)"]["invalid_eta"] == 1


# ===================================================================
# 2. Clause cache – IOError / corruption
# ===================================================================

class TestClauseCacheExtended:

    def test_save_ioerror_logged(self, tmp_path):
        """Cover line 405 — IOError during save."""
        read_only = tmp_path / "readonly"
        read_only.mkdir()
        # Write a directory in place of the file to force IOError
        (read_only / CLAUSE_CACHE_FILENAME).mkdir()
        # Should not raise
        save_clause_cache(
            [QueryClause("Where", "title", "equals", "x")],
            cache_dir=read_only,
        )

    def test_load_corrupt_json(self, tmp_path):
        """Cover corruption branch in load_clause_cache."""
        (tmp_path / CLAUSE_CACHE_FILENAME).write_text("{bad", encoding="utf-8")
        clauses, ussec = load_clause_cache(cache_dir=tmp_path)
        assert clauses == []
        assert ussec is False

    def test_load_missing_keys(self, tmp_path):
        """Cache file with missing keys returns defaults."""
        (tmp_path / CLAUSE_CACHE_FILENAME).write_text("{}", encoding="utf-8")
        clauses, ussec = load_clause_cache(cache_dir=tmp_path)
        assert clauses == []
        assert ussec is False

    def test_clear_nonexistent(self, tmp_path):
        """Clearing cache when no file — no error."""
        clear_clause_cache(cache_dir=tmp_path)

    def test_roundtrip_with_ussec_true(self, tmp_path):
        clauses = [QueryClause("Where", "SlaType", "equals", "OutOfSla")]
        save_clause_cache(clauses, include_ussec=True, cache_dir=tmp_path)
        loaded, ussec = load_clause_cache(cache_dir=tmp_path)
        assert len(loaded) == 1
        assert ussec is True


# ===================================================================
# 3. ClauseRow Tk widget tests
# ===================================================================

@pytest.fixture
def clause_row_parts(tk_root):
    """Common helpers for building a ClauseRow."""
    fields = ["S360_ServiceTreeServiceName", "dueDate", "ActionOwnerName"]
    display = {f: COLUMN_DISPLAY_NAMES.get(f, f) for f in fields}
    data_vals = {
        "S360_ServiceTreeServiceName": ["Svc-A", "Svc-B"],
        "dueDate": [],
        "ActionOwnerName": ["John Doe", "Jane Smith"],
    }
    parent = tk.ttk.Frame(tk_root)
    parent.pack()
    return parent, fields, display, data_vals


class TestClauseRowInit:
    """Cover lines 429-488 — __init__ widget creation."""

    def test_index_zero_shows_where_label(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 0, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        assert row.connector_var.get() == "Where"
        assert hasattr(row, "connector_label")
        row.destroy()

    def test_index_nonzero_shows_combo(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 1, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        assert row.connector_var.get() == "And"
        assert hasattr(row, "connector_combo")
        row.destroy()


class TestClauseRowFieldSelected:
    """Cover lines 492-504 — _on_field_selected."""

    def test_selecting_string_field_sets_string_operators(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 0, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        row.field_var.set("Service Name")
        row._on_field_selected()
        ops = list(row.operator_combo.cget("values"))
        assert ops == STRING_OPERATORS
        row.destroy()

    def test_selecting_date_field_sets_date_operators(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 0, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        row.field_var.set("Due Date")
        row._on_field_selected()
        ops = list(row.operator_combo.cget("values"))
        assert ops == DATE_OPERATORS
        row.destroy()

    def test_operator_reset_on_type_change(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 0, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        # Set a string operator
        row.operator_var.set("contains")
        # Switch to date field — "contains" not in DATE_OPERATORS → reset
        row.field_var.set("Due Date")
        row._on_field_selected()
        assert row.operator_var.get() in DATE_OPERATORS
        row.destroy()

    def test_value_combo_populated(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 0, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        row.field_var.set("Action Owner")
        row._on_field_selected()
        vals = list(row.value_combo.cget("values"))
        assert "John Doe" in vals
        row.destroy()


class TestClauseRowGetSetDestroy:
    """Cover lines 508-510, 519-525, 529."""

    def test_get_clause_returns_query_clause(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 0, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        row.field_var.set("Service Name")
        row._on_field_selected()
        row.operator_var.set("equals")
        row.value_var.set("Svc-A")
        clause = row.get_clause()
        assert isinstance(clause, QueryClause)
        assert clause.field == "S360_ServiceTreeServiceName"
        assert clause.operator == "equals"
        assert clause.value == "Svc-A"
        assert clause.connector == "Where"
        row.destroy()

    def test_set_clause_restores_state(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 1, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        clause = QueryClause("Or", "dueDate", "on or before", "2026-06-01")
        row.set_clause(clause)
        assert row.field_var.get() == "Due Date"
        assert row.operator_var.get() == "on or before"
        assert row.value_var.get() == "2026-06-01"
        assert row.connector_var.get() == "Or"
        row.destroy()

    def test_destroy_removes_frame(self, clause_row_parts):
        parent, fields, display, data_vals = clause_row_parts
        row = ClauseRow(parent, 0, fields, display, data_vals,
                        on_add=lambda: None, on_remove=lambda: None)
        assert row.frame.winfo_exists()
        row.destroy()
        assert not row.frame.winfo_exists()


# ===================================================================
# 4. QueryBuilder Tk widget tests
# ===================================================================

@pytest.fixture
def qb(tk_root, tmp_path):
    """Create a QueryBuilder instance with test data, patching cache dir."""
    items = _make_items()
    with patch("sfi_reporter.query_builder.get_cache_dir", return_value=str(tmp_path)):
        builder = QueryBuilder(
            parent=tk_root,
            action_items=items,
            program_names=dict(_PROGRAM_NAMES),
            service_names=dict(_SERVICE_NAMES),
            is_manager=True,
            service_owners=dict(_SERVICE_OWNERS),
            on_apply=MagicMock(),
        )
    builder.withdraw()
    yield builder
    try:
        builder.destroy()
    except tk.TclError:
        pass


class TestQueryBuilderInit:
    """Cover lines 545-575 — __init__ + transient, geometry, fields."""

    def test_creates_toplevel(self, qb):
        assert isinstance(qb, tk.Toplevel)

    def test_title_set(self, qb):
        assert "Filter" in qb.title()

    def test_clause_rows_created(self, qb):
        # At least one default clause row
        assert len(qb._clause_rows) >= 1

    def test_is_manager_adds_service_owner_field(self, qb):
        assert "_service_owner" in qb._fields

    def test_non_manager_excludes_service_owner(self, tk_root, tmp_path):
        items = _make_items()
        with patch("sfi_reporter.query_builder.get_cache_dir", return_value=str(tmp_path)):
            builder = QueryBuilder(
                parent=tk_root,
                action_items=items,
                program_names=dict(_PROGRAM_NAMES),
                service_names=dict(_SERVICE_NAMES),
                is_manager=False,
            )
        builder.withdraw()
        assert "_service_owner" not in builder._fields
        builder.destroy()


class TestQueryBuilderEnrich:
    """Cover lines 583-595 — _enrich_items."""

    def test_resolved_program_set(self, qb):
        for item in qb._items:
            assert "_resolved_program" in item

    def test_resolved_program_first_pid(self, qb):
        item = qb._items[0]  # prog-1 → Security Compliance
        assert item["_resolved_program"] == "Security Compliance"

    def test_service_owner_set(self, qb):
        svc_a = [i for i in qb._items if i.get("S360_ServiceTreeServiceName") == "Svc-A"]
        for item in svc_a:
            assert item["_service_owner"] == "Alice Owner"

    def test_service_owner_empty_when_no_match(self, qb):
        svc_c = [i for i in qb._items if i.get("S360_ServiceTreeServiceName") == "Svc-C"]
        for item in svc_c:
            assert item["_service_owner"] == ""


class TestQueryBuilderFieldMetadata:
    """Cover lines 599-631 — _build_field_metadata."""

    def test_fields_contain_filter_fields(self, qb):
        for f in FILTER_FIELDS:
            assert f in qb._fields

    def test_display_names_match(self, qb):
        for f in qb._fields:
            assert f in qb._field_display
            assert qb._field_display[f] == COLUMN_DISPLAY_NAMES.get(f, f)

    def test_data_values_populated(self, qb):
        # ActionOwnerName should have distinct owner names
        owners = qb._data_values.get("ActionOwnerName", [])
        assert "Jane Smith" in owners
        assert "John Doe" in owners

    def test_program_values_use_resolved_names(self, qb):
        pgm = qb._data_values.get("S360_ProgramIds", [])
        assert "Security Compliance" in pgm


class TestQueryBuilderAddRemoveRows:
    """Cover lines 724-735, 739-747."""

    def test_add_clause_row_increases_count(self, qb):
        initial = len(qb._clause_rows)
        qb._add_clause_row()
        assert len(qb._clause_rows) == initial + 1

    def test_remove_clause_row_decreases_count(self, qb):
        qb._add_clause_row()
        qb._add_clause_row()
        count = len(qb._clause_rows)
        qb._remove_clause_row(0)
        assert len(qb._clause_rows) == count - 1

    def test_cannot_remove_last_row(self, qb):
        # Reset to 1 row
        while len(qb._clause_rows) > 1:
            qb._remove_clause_row(0)
        assert len(qb._clause_rows) == 1
        qb._remove_clause_row(0)
        assert len(qb._clause_rows) == 1  # Still 1

    def test_remove_out_of_range_safe(self, qb):
        count = len(qb._clause_rows)
        qb._add_clause_row()  # ensure >1
        qb._remove_clause_row(999)
        # No crash, count unchanged (999 is out of range)
        assert len(qb._clause_rows) == count + 1


class TestQueryBuilderRunQuery:
    """Cover lines 761-811 — _run_query."""

    def test_run_query_populates_results(self, qb):
        # Set up a clause that matches something
        row = qb._clause_rows[0]
        row.field_var.set("Action Owner")
        row._on_field_selected()
        row.operator_var.set("equals")
        row.value_var.set("John Doe")

        qb._run_query()

        # Should have filtered items
        assert len(qb._filtered_items) > 0
        # Result tree should have children
        children = qb._result_tree.get_children()
        assert len(children) > 0
        # Result count label should be set
        assert qb._result_count_var.get() != ""

    def test_run_query_no_match(self, qb):
        row = qb._clause_rows[0]
        row.field_var.set("Action Owner")
        row._on_field_selected()
        row.operator_var.set("equals")
        row.value_var.set("Nobody Here")

        qb._run_query()
        assert len(qb._filtered_items) == 0

    def test_run_query_ussec_excluded(self, qb):
        qb._ussec_var.set(False)
        # Empty clause → all items minus USSec
        qb._run_query()
        titles = [it["title"] for it in qb._filtered_items]
        assert not any("ussec shadow" in t.lower() for t in titles)


class TestQueryBuilderClearAll:
    """Cover lines 819-836 — _clear_all."""

    def test_clear_resets_to_one_row(self, qb):
        qb._add_clause_row()
        qb._add_clause_row()
        qb._clear_all()
        assert len(qb._clause_rows) == 1

    def test_clear_empties_results(self, qb):
        # Run query first
        qb._run_query()
        qb._clear_all()
        assert qb._result_count_var.get() == ""
        assert qb._result_tree.get_children() == ()

    def test_clear_resets_ussec(self, qb):
        qb._ussec_var.set(True)
        qb._clear_all()
        assert qb._ussec_var.get() is False


class TestQueryBuilderApplyFilter:
    """Cover lines 865-878 — _apply_filter."""

    def test_apply_calls_on_apply_callback(self, qb):
        qb._apply_filter()
        assert qb._on_apply.called

    def test_apply_passes_filtered_items(self, qb):
        qb._apply_filter()
        args = qb._on_apply.call_args[0]
        # First arg is list of filtered items, second is list of clauses
        assert isinstance(args[0], list)
        assert isinstance(args[1], list)


class TestQueryBuilderLoadCached:
    """Cover lines 840-861 — _load_cached."""

    def test_cached_clauses_restored(self, tk_root, tmp_path):
        # Pre-save a clause to cache
        saved = [QueryClause("Where", "ActionOwnerName", "equals", "John Doe")]
        save_clause_cache(saved, include_ussec=True, cache_dir=tmp_path)

        with patch("sfi_reporter.query_builder.get_cache_dir", return_value=str(tmp_path)):
            builder = QueryBuilder(
                parent=tk_root,
                action_items=_make_items(),
                program_names=dict(_PROGRAM_NAMES),
                service_names=dict(_SERVICE_NAMES),
            )
        builder.withdraw()

        # The builder should have loaded the cached clause
        assert len(builder._clause_rows) == 1
        clause = builder._clause_rows[0].get_clause()
        assert clause.field == "ActionOwnerName"
        assert clause.operator == "equals"
        assert clause.value == "John Doe"
        assert builder._ussec_var.get() is True
        builder.destroy()

    def test_no_cache_file_keeps_default(self, tk_root, tmp_path):
        with patch("sfi_reporter.query_builder.get_cache_dir", return_value=str(tmp_path)):
            builder = QueryBuilder(
                parent=tk_root,
                action_items=_make_items(),
                program_names=dict(_PROGRAM_NAMES),
                service_names=dict(_SERVICE_NAMES),
            )
        builder.withdraw()
        # Should have the single default empty row
        assert len(builder._clause_rows) == 1
        builder.destroy()


class TestQueryBuilderGetClauses:
    """Cover _get_clauses helper (line 757)."""

    def test_returns_list_of_query_clauses(self, qb):
        clauses = qb._get_clauses()
        assert isinstance(clauses, list)
        assert all(isinstance(c, QueryClause) for c in clauses)


class TestQueryBuilderUpdateRemoveButtons:
    """Cover lines 751-753 — _update_remove_buttons."""

    def test_single_row_remove_disabled(self, qb):
        while len(qb._clause_rows) > 1:
            qb._remove_clause_row(0)
        assert len(qb._clause_rows) == 1
        state = str(qb._clause_rows[0].remove_btn.cget("state"))
        assert "disabled" in state

    def test_multiple_rows_remove_enabled(self, qb):
        qb._add_clause_row()
        for row in qb._clause_rows:
            state = str(row.remove_btn.cget("state"))
            assert "disabled" not in state
