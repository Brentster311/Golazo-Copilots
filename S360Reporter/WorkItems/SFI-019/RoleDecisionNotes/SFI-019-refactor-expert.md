# SFI-019 Refactor Expert Notes

## Review Findings

### Applied Fixes
1. **N-1 — `callable` type hints**: Changed `on_saved: callable`, `on_choice: callable`, `on_complete: callable` to untyped defaults (`=None`). The builtin `callable` is a function, not a type — using it as a type annotation is misleading.
2. **C-2 — Sequential save comment**: Added clarifying comment in `BulkEtaProgressDialog._run_bulk()` explaining that one-at-a-time saves are intentional for per-item error tracking.

### Identified But Deferred
| Issue | Reason to Defer |
|-------|-----------------|
| D-1/D-2: BaseDialog class for centering boilerplate | Would touch 6+ existing dialogs — scope exceeds SFI-019 |
| D-3: Shared `_render_summary()` helper | Minimal duplication (2 instances), not worth the abstraction overhead |
| C-1: Extract stat recomputation from `_on_eta_update_complete` | Works correctly, tested via TC-09/TC-10 — extract when a third caller appears |
| C-3: Deferred imports | Likely needed to avoid circular imports; existing pattern in codebase |

## Test Results After Refactor
- S360Reporter: **147 passed**
- No behavior changes — all tests green before and after
