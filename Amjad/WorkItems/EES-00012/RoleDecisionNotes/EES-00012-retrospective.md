# EES-00012 — Retrospective

## What Went Well

- **User story augmentation was smooth:** Adding the live LLM status requirement to an existing user story (originally just GUI display) was handled cleanly without scope creep.
- **`_then_display()` reuse:** The v2-aware helper already existed in `eval_result_to_display()`. Promoting it to module-level eliminated duplication across both `rules_to_rows()` and `eval_result_to_display()`.
- **TDD caught the right things:** 14 tests failed in red phase, all 15 new tests (including the `None` default test which passed immediately) went green after implementation. No iterative fixing needed.
- **Error isolation pattern (A-3):** The architect's recommendation to wrap `on_status` in try/except was implemented and tested. Good defensive coding for cross-thread callbacks.
- **Clean v1→v2 transition:** Removing 5+ v1-only code paths from `_show_rule_detail()` simplified the code significantly.

## What Didn't Go Well

- **Capability-Impact.md gate:** Same issue as EES-00013 — the architect role doesn't auto-create this file, requiring a manual fix after transition failure. This is a recurring process friction.

## Action Items

1. **Consider auto-generating Capability-Impact.md stub** during architect transition when `capabilities.yaml` exists. (Process improvement for Golazo)

## Metrics

- 15 new tests added (268 total)
- 4 production files modified, 888 insertions / 62 deletions
- Zero regressions
- Completed all 9 roles in a single session
