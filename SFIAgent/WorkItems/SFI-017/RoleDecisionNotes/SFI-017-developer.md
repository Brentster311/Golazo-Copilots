# SFI-017 — Developer Notes

## Implementation Summary
- Created `query_builder.py` (530 lines) — new module with pure logic + tkinter UI
- Added 🔍 Query button to main controls bar in `tk_app.py` (disabled until data loads)
- 32 new tests covering all 20 test cases from design
- All 171 tests pass (39 + 116 + 16)
- Exe rebuilt with `--hidden-import sfi_reporter.query_builder` (20MB)

## Key design decisions during implementation
- `_get_today()` extracted as separate function for test mocking
- `_parse_item_date()` strips time component for date-only comparison
- Value combobox populated with up to 500 distinct values per field
- Program IDs resolved to names in value suggestions for S360_ProgramIds field
