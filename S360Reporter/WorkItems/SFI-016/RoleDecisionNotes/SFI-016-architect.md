# SFI-016 — Architect Notes

## Review Summary
Approved with **two bugs fixed** during review.

## Bugs Found & Fixed
1. **`failed_kpis` NameError**: The `failed_kpis` list was used in the inner function `fetch_kpi_grid()` and in the outer return statements, but was never initialized as a local variable. Added `failed_kpis: list[dict] = []` before the inner function definition.
2. **Early return type mismatch**: `return []` when inputs are empty should be `return [], []` to match the declared `tuple[list[dict], list[dict]]` return type. Fixed.
3. **Stale type annotation**: Updated function signature from `-> list[dict]` to `-> tuple[list[dict], list[dict]]` and corrected docstring.

## Architectural Decisions Validated
- **Singleton without locking**: Python GIL guarantees atomicity of `_client_instance is None` check. No `threading.Lock` needed for the singleton itself.
- **Mutable list in closure**: `failed_kpis` is a list (mutable), so the inner function can `.append()` without `nonlocal`. Mutations are protected by `status_lock`.
- **No retry backoff**: Desktop app with user-initiated retry — exponential backoff is unnecessary. The user decides when to retry.

## Security & Privacy
- No new data paths introduced. Failed KPI names are already visible in logs and the UI.
- No credentials stored or transmitted differently.

## Scalability
- Singleton eliminates N×token overhead. For 25 workers, this reduces cold-start from ~25 token fetches to 1.
- Retry fetches only failed KPIs — proportional to failure count, not total KPI count.
