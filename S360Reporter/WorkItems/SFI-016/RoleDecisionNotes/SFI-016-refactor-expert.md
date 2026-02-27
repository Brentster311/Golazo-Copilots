# SFI-016 — Refactor Expert Notes

## Code Review Summary
**Verdict**: No refactoring needed. Code quality is acceptable.

## Observations (Not Actionable)
1. **`fetch_kpi_grid` inner function (~55 lines)**: Long but cohesive — handles column cache check, discovery, and data fetch as a single logical unit. Extracting would add complexity without benefit since it captures `service_ids`, `kpi_names`, `failed_kpis`, `status_lock`, etc. from the closure.
2. **`_on_retry_complete` (~65 lines)**: Contains inline KPI stat recomputation. Could extract a `_recompute_kpi_stats()` helper, but it's only used in one place and the logic is straightforward.
3. **Lazy imports in retry methods**: `from sfi_reporter.data import ...` inside method body. This is intentional — avoids circular imports and matches the existing pattern in `do_refresh`.

## What's Good
- Singleton pattern is minimal and correct (3 lines of logic).
- Thread safety uses existing `status_lock` — no new synchronization primitives.
- Retry button visibility logic is clean — `pack_forget()` / `pack()` toggle.
- Error messages include KPI names, not just IDs — good UX.
- `failed_kpis` dict shape is consistent across all usage sites.

## Tests Verified
All 84 S360Reporter tests pass. No behavior changes made.
