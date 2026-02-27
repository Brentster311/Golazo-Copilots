# SFI-035 — Refactor Expert Decision Notes

## Assessment
The implementation is already clean and follows existing patterns:
- `FetchResult` and `AnalysisResult` are minimal dataclasses — no duplication, clear naming
- `format_sources_card` is a pure function — easy to test, no coupling
- `_fetch_with_provenance` is a thin wrapper around `fetch_all_urls` — no redundancy
- Caller changes are minimal (3 lines in `dialogs.py`, 1 new kwarg in `copilot_panel.py`)

## Refactoring Opportunities Considered
None identified. The change is small and idiomatic. No code smells, no duplication, no unnecessary complexity.

## Tests
All 30 tests (SFI-034 + SFI-035) pass — no behavior changes.
