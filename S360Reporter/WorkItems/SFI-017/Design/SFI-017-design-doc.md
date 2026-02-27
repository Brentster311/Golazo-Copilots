# SFI-017 Design Doc — Action Item Query Builder

## Summary

Add a clause-based query builder window (inspired by ADO/IcM query editor) to S360Reporter. Users build ad-hoc queries by adding `(And/Or, Field, Operator, Value)` clauses against any column in the loaded action item data. Results show a per-program summary (Total / Out of SLA / Invalid ETA) with drill-down into filtered items.

## Problem Statement

SFI leads/managers currently can only explore data by double-clicking through the main page's fixed summary tables. They cannot answer cross-cutting questions like:
- "Show me items due within 7 days for these specific services"
- "What's the breakdown by program for a specific lead?"
- "Filter out all USSec Shadow Action Items and show me what's left"

## Business Case

**Why now:** Direct feedback from stakeholders requesting filter capabilities. The data is already loaded — we just need a UI to query it.

**Impact:** Reduces time-to-answer from "many clicks through drill-downs" to a single query.

## Stakeholders

- SFI leads and managers (primary users)
- Project owner (Brent)

## Functional Requirements

### FR-1: Query Button on Main Page
- Add "🔍 Query" button to the controls bar (after Retry, before status area)
- Disabled when no data is loaded; enabled after data loads

### FR-2: QueryBuilder Window
- `tk.Toplevel` window, non-modal (user can keep main page visible)
- Size: 1000x650, centered on parent

### FR-3: Clause Builder Area (top half)
- Scrollable frame of clause rows
- Each clause row contains:
  - **And/Or** Combobox (first row shows "Where" label instead)
  - **Field** Combobox (all available fields with friendly display names)
  - **Operator** Combobox (contextual to field type)
  - **Value** Combobox (populated with distinct values from data, editable for free-text)
  - **➕** Add button (adds new row after this one)
  - **✕** Remove button (removes this row; disabled if only 1 clause)
- "➕ Add new clause" link at the bottom
- Field type detection:
  - Date fields: keys ending in `Date`, `Time`, `Eta` → date operators
  - All others → string operators
- String operators: `equals`, `not equals`, `contains`, `not contains`
- Date operators: `equals`, `on or before`, `on or after`
- Date value expressions: `@Today - N` where N is days (e.g., `@Today - 7`)

### FR-4: USSec Shadow Checkbox
- Checkbox: "☐ Include USSec Shadow Action Items" (unchecked by default)
- When unchecked, items with `title` matching "USSec Shadow Action Item" (case-insensitive substring) are excluded from results

### FR-5: Action Buttons
- "▶ Run Query" — evaluates clauses, shows results
- "🗑 Clear All" — removes all clauses, clears results, deletes cached clauses file

### FR-6: Results Area (bottom half)
- SortableTreeview showing per-program summary: Program | Total | Out of SLA | Invalid ETA
- A totals row at the bottom (or label showing total filtered count)
- Double-click a program row → opens DetailModal with the filtered items for that program

### FR-7: Clause Caching
- On "Run Query", serialize current clauses to `%TEMP%/GUI/query_clauses.json`
- On window open, load cached clauses and restore the UI
- Cache format: `{"clauses": [{"connector": "And", "field": "...", "operator": "...", "value": "..."}], "include_ussec": false}`

## Non-Functional Requirements

- < 500ms filter execution on ~5,000 rows
- Value combobox type-ahead for large lists
- Clause area scrollable for 6+ clauses
- Consistent with existing tkinter styling (Segoe UI, same padding)

## Proposed Approach

### New Module: `query_builder.py`

Create a new file `GUI/src/sfi_reporter/query_builder.py` containing:

1. **`QueryClause` dataclass** — `connector`, `field`, `operator`, `value`
2. **`ClauseRow` class** — Single tkinter row with combo/entry widgets
3. **`QueryBuilder(tk.Toplevel)`** — Main window class:
   - `__init__` receives `parent`, `action_items: list[dict]`, `program_names: dict`, `service_names: dict`
   - `_load_cached_clauses()` / `_save_clauses_to_cache()`
   - `_add_clause_row()` / `_remove_clause_row()`
   - `_on_field_change()` — update operators and value list
   - `_run_query()` — evaluate, aggregate, display
   - `_clear_all()` — reset form + cache
4. **`evaluate_clauses(items, clauses, include_ussec)`** — Pure function for testability:
   - Iterates items, applies each clause with And/Or logic
   - Returns filtered list
5. **`get_field_type(field_name)`** — Returns `"date"` or `"string"`
6. **`resolve_date_expression(expr)`** — Parses `@Today - N` → `datetime`

### Integration in `tk_app.py`

- Import `QueryBuilder` 
- Add `self.query_btn` to controls bar in `_build_ui()`
- Disable button until data loaded; enable in `_update_tables()`
- `_on_query()` opens `QueryBuilder` with current data

### Cache Location

- `%TEMP%/GUI/query_clauses.json` — uses existing `get_cache_dir()` from `cache.py`

## Alternatives Considered

1. **Fixed filter dropdowns** — Simpler but inflexible; rejected per user feedback wanting generic query capability
2. **Inline filters on main page** — Would clutter existing layout; user explicitly said "off the main page"
3. **SQL-like text query** — Too steep a learning curve for non-technical users

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Large distinct value lists slow down combobox | Limit to first 500 unique values; type-ahead for search |
| Date expression parsing edge cases | Strict regex `@Today\s*-\s*\d+`; fallback to literal string comparison |
| Users confused by And/Or logic | First clause is always "Where" (no connector); default And |

## Dependencies

- No new external dependencies
- Relies on existing `SortableTreeview`, `DetailModal`, `is_invalid_eta`, `COLUMN_DISPLAY_NAMES`

## Rollout / Rollback Plan

- **Rollout:** Additive — new button + new window class. Zero changes to existing behavior.
- **Rollback:** Remove query button from controls bar, delete `query_builder.py`

## Observability Plan

- Log at DEBUG: clause count, result count, execution time
- Log at WARNING: malformed date expressions

## Test Strategy Summary

- Unit tests for `evaluate_clauses()` (pure function — easy to test)
- Unit tests for `get_field_type()`, `resolve_date_expression()`
- Unit tests for clause cache save/load
- Integration test: `QueryBuilder` window opens, clause rows can be added/removed
