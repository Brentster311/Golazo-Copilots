# SFI-017 — Action Item Query Builder

**Status**: IMPLEMENTED

## User Story

- **Title**: Action Item Query Builder
- **As a**: SFI lead / manager using the S360Reporter desktop app
- **I want**: a generic clause-based query builder (similar to ADO/IcM query editor) where I can dynamically add filter clauses with And/Or logic on any available field, using contextual operators and values — then see a summary (Total / Out of SLA / Invalid ETA) grouped by Program and drill into the filtered results
- **So that**: I can build ad-hoc queries to answer questions like "show me items for these 3 services due within 7 days" or "what does this lead's breakdown look like by program?" without being limited to a fixed set of filters

## Out of Scope

- Named/saved query presets with a save-as UX (future work item)
- Export filtered results to CSV/Excel
- Server-side filtering (all filtering is client-side on already-loaded data)
- Changes to the existing main page summary tables
- Nested/grouped clause logic (parentheses) — flat And/Or only for v1

## Assumptions

- **Assumption (explicit)**: The query builder opens as a new Toplevel window launched from a button on the main page — consistent with the existing DetailModal pattern.
- **Assumption (explicit)**: Filtering operates on the in-memory `action_items` list already fetched. No additional API calls required.
- **Assumption (explicit)**: Items titled "USSec Shadow Action Item" are excluded by default. A checkbox at the top of the form allows including them.
- **Assumption (explicit)**: Available fields are dynamically discovered from the loaded data columns + resolved lookup fields (program names, KPI names). The `DISPLAY_NAMES` mapping provides friendly labels.
- **Assumption (explicit)**: Operators are contextual to field type — string fields get `equals`, `not equals`, `contains`; date fields get `equals`, `on or before`, `on or after`, `between`; date fields also support relative expressions like `@Today - 7`.
- **Assumption (explicit)**: Value input is a Combobox populated with distinct values from the data for that field (type-ahead searchable), or free-text entry for expressions.
- **Assumption (explicit)**: The current set of query clauses is cached to `%TEMP%/GUI/` (same cache directory as existing data cache) as a JSON file. On form open, the last-used clauses are restored automatically. No explicit save/load UI needed.

## Acceptance Criteria

- [ ] A "🔍 Query" button is visible on the main page controls bar that opens the query builder window
- [ ] The query builder displays a clause list where each clause has: **And/Or** toggle (first row has none), **Field** dropdown, **Operator** dropdown (contextual to field type), and **Value** combobox/entry — with ➕ (add) and ✕ (remove) buttons per row
- [ ] An "➕ Add new clause" link/button appends a new empty clause row to the list
- [ ] String operators include: `equals`, `not equals`, `contains`; date operators include: `on or before`, `on or after`, `equals`; date values support `@Today - N` expressions
- [ ] Clicking "▶ Run Query" evaluates all clauses against the loaded action items and displays a results summary grouped by Program: columns **Program**, **Total**, **Out of SLA**, **Invalid ETA**
- [ ] Double-clicking a program row in the results drills into the filtered action items list (reusing the existing DetailModal pattern)
- [ ] A "🗑 Clear" button removes all clauses, resets the form, and clears the cached query

## Non-Functional Requirements

- Filtering must be responsive (< 500ms) since it's client-side on typically < 5,000 rows
- Form layout should be consistent with existing tkinter styling (same fonts, colors, padding)
- Value comboboxes should support type-ahead / search for large distinct value lists
- Clause rows should be scrollable if more than ~6 are added
- Query clauses cached as JSON in `%TEMP%/GUI/query_clauses.json` — survives app close/reopen with no user action

## Telemetry / Metrics Expected

- Log query execution to `sfi_reporter.log` at DEBUG level (clause count, result count)

## Rollout / Rollback Notes

- Feature is additive — new button + new window. No changes to existing main page behavior.
- Rollback: remove the query button and QueryBuilder class.
