# SFI-007: Refactor Expert Notes

## Date: 2026-02-04

## Code Review

### Code Smells Identified

1. **Duplicate Modal Setup (Minor)**
   - Both `DetailModal` and `ItemDetailsModal` have similar init code
   - Pattern: geometry, transient, grab_set, center, escape binding
   - **Decision**: Not refactoring now - would require base class extraction
   - **Future Work**: Consider `BaseModal` class in SFI-008

2. **Import Statement Location (Minor)**
   - `import re` inside `format_field_label()` function
   - `import json` inside `format_field_value()` function
   - **Decision**: Acceptable for small, rarely-called functions
   - Moving to top would work but is low priority

### No Changes Made
The code is clean and well-organized. The identified items are minor and would be better addressed as a dedicated refactoring work item.

### Tests Verified
- All 31 tests pass
- No behavior changes

## Recommendation for Future
Create SFI-008: Extract `BaseModal` class to reduce duplication between:
- `DetailModal`
- `ItemDetailsModal`
- Any future modal dialogs
