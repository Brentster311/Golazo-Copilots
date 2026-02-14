# EES-00012 — Design Doc: V2 Rule Grammar GUI Display + Live LLM Status

## Summary

Update the Tkinter GUI to properly display v2 rule grammar (CHANGE_STATE / RULED_OUT / GAP with optional ELSE branches) and add a continuously-updating status bar showing real-time LLM extraction progress.

## Problem Statement

After EES-00010 (v2 model) and EES-00013 (multi-turn tool-calling extractor), the GUI still references v1 rule attributes (`rule.type`, `rule.then.value`, `rule.then.noun`, `rule.requires`, `rule.produces`). The v1 code paths will render incorrectly or fail on v2 `RuleOutput` objects. Additionally, extraction now runs a multi-turn agentic loop that can take many seconds — users have no visibility into what the LLM is doing.

## Business Case

- **Why now:** EES-00010 (v2 model) and EES-00013 (multi-turn extractor) are complete. The GUI is the last layer still rendering v1 data.
- **Impact:** Users cannot see CHANGE_STATE / RULED_OUT / GAP semantics or ELSE branches. During extraction, the static "Extracting facts via LLM..." message gives no feedback.
- **KPIs:** All v2 rules display correctly; users see real-time extraction progress.

## Stakeholders

- Knowledge engineers (primary users of the GUI)

## Functional Requirements

### FR-1: v2 Rule Display in Rules Treeview
- `rules_to_rows()` must use `RuleOutput.kind` and `RuleOutput.description` instead of v1 attributes.
- Add an "else" column to proposed rules and KB rules treeviews showing the ELSE branch (blank if none).

### FR-2: v2 Rule Detail Dialog
- `_show_rule_detail()` must display `RuleOutput` objects — showing `kind(description)` format.
- Display ELSE branch when present.
- Remove references to deprecated `rule.type`, `rule.then.noun`, `rule.requires`, `rule.produces`.

### FR-3: v2 Evaluation Display
- `eval_result_to_display()` should use `result.outputs` (with branch info) instead of deprecated `.root_causes` / `.ruled_out` / `.gap_rules` properties.
- `_format_eval_display()` should show which branch fired (THEN vs ELSE) for each rule.
- Display v2 categories: CHANGE_STATE, RULED_OUT, GAP (replacing old root_cause/ruleout names).

### FR-4: Live LLM Status During Extraction
- Add an optional `on_status: Callable[[str], None] | None` parameter to `FactExtractor.extract()`.
- Emit status messages at key points in the agentic loop:
  - `"Turn N: calling LLM..."` before each API call
  - `"Turn N: tool_name(args_summary)..."` for each tool call processed
  - `"Turn N: N facts, N rules collected"` after processing all tools in a turn
- Wire up in `app.py` to thread-safely update `status_var` via `root.after(0, ...)`.

## Non-Functional Requirements

- No new dependencies.
- Existing GUI patterns and styles.
- Thread-safety for status callbacks (must use `root.after`).
- Backward compatibility: `on_status` defaults to `None`; existing callers unaffected.

## Proposed Approach

### Phase 1: Live Status Callback (fact_extractor.py + app.py)

1. Add `on_status: Callable[[str], None] | None = None` parameter to `extract()`.
2. Insert `on_status` calls at strategic points in the agentic loop.
3. In `_extract_facts()`, create a closure that calls `self.root.after(0, self.status_var.set, msg)` and pass it as `on_status`.

### Phase 2: Adapter Updates (adapters.py)

1. Update `rules_to_rows()`:
   - Use `_then_display()` (already exists for eval) instead of v1 logic.
   - Add `else` key using `_then_display`-style logic on `rule.else_`.

2. Update `eval_result_to_display()`:
   - Use `result.outputs` list with its `branch` field.
   - Build display grouped by output kind (CHANGE_STATE, RULED_OUT, GAP).

### Phase 3: GUI Updates (app.py)

1. Add "else" column to both rules treeviews.
2. Update `_show_rule_detail()` to use v2 `RuleOutput` attributes.
3. Update `_format_eval_display()` to show branch (THEN/ELSE) and v2 output kinds.
4. Update KB double-click to include else column in display.

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| Separate status label widget | Unnecessary — existing `status_var` is sufficient and visible |
| Progress percentage bar | Not feasible — we don't know how many turns the LLM will need |
| Polling-based status | More complex, less responsive than callback pattern |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Thread-safety of status updates | Use `root.after(0, ...)` for all GUI mutations from worker thread |
| v1 backward compatibility break | `_then_display()` already handles v1 `RuleThen` via `isinstance` check |
| `on_status` performance impact | Callback is a simple string set; negligible overhead |

## Dependencies

- EES-00010 (v2 model) — **complete**
- EES-00013 (multi-turn extractor) — **complete**

## Migration / Rollout / Rollback

- Pure display change + optional callback. No data migration needed.
- Rollback: revert commits.

## Observability

- Logger messages already exist in `fact_extractor.py` — status callbacks supplement, not replace.

## Test Strategy Summary

| Area | Approach |
|------|----------|
| `rules_to_rows()` v2 | Unit test: v2 Rule with RuleOutput → correct row dict |
| `rules_to_rows()` with ELSE | Unit test: Rule with `else_` → row includes else display |
| `eval_result_to_display()` v2 | Unit test: EvaluationResult with outputs → correct display dict |
| `_show_rule_detail()` | Manual: double-click rule shows v2 detail |
| Live status callback | Unit test: `extract()` with `on_status` mock → called with expected messages |
| Thread safety | Integration: extraction in worker → status_var updated without crash |

## Files to Modify

| File | Changes |
|------|---------|
| `src/ees/fact_extractor.py` | Add `on_status` parameter, emit status messages |
| `src/ees/gui/adapters.py` | Update `rules_to_rows()`, `eval_result_to_display()` for v2 |
| `src/ees/gui/app.py` | Add else column, update detail dialog, update eval display, wire status callback |
| `tests/test_fact_extractor.py` | Add tests for `on_status` callback |
| `tests/test_adapters.py` | Add/update tests for v2 rule display |
