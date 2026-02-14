# EES-00012 — Architect Decision Notes

## Architecture Review Summary

Design is architecturally sound. Changes are strictly presentation-layer and callback-plumbing. No new external dependencies, no data model changes, no security surface changes.

## Key Architectural Decisions

1. **Optional `on_status` keyword-only parameter**: Backward compatible. Defaulting to `None` means no existing caller breaks.

2. **Error isolation in `on_status`**: Wrap callback invocations in try/except to prevent status reporting failures from crashing extraction. This is important since the callback crosses the thread boundary (worker → GUI).

3. **`_then_display()` as module-level helper**: Promotes reuse between `rules_to_rows()` and `eval_result_to_display()`. Pure function, easily testable.

4. **`eval_result_to_display()` contract evolution**: Replace deprecated backward-compat keys (`root_causes`, `ruled_out`, `gap_rules`) with `outputs` list containing `{rule_id, branch, kind, description}` dicts. The only consumer (`_format_eval_display` in `app.py`) is updated in the same changeset.

## Capability Impact

- **fact-extraction**: `on_status` param added — additive, no contract break
- **gui**: Adapter outputs change, display logic updated — internal, no external contract
- **cli-orchestration**: Transitive dependent — no changes needed (doesn't call adapters directly)

## Risks

- None significant. All changes are internal display-layer. Rollback is a simple git revert.
