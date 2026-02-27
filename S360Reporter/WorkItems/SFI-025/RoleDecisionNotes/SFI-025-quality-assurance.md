# SFI-025 — Quality Assurance Decision Notes

## Work Item
**ID**: SFI-025  
**Title**: Configure LLM — GUI dialog with manual entry and auto-detect

## Review Decisions

### Design Review
- Design approved with minor refinements (endpoint stripping, explicit defaults)
- No scope changes needed — all acceptance criteria are testable
- Auto-detect error paths are well-covered in design

### Test Strategy
- 13 test cases covering all 7 acceptance criteria
- Auto-detect tests mock `discover_azure_configs()` to avoid Azure SDK dependency in CI
- Config resolution order tested explicitly (TC-10, TC-11)
- Validation tested (TC-13)
- All tests are unit tests — no integration tests needed beyond manual exe testing

### Test Coverage Rationale
- Happy paths: TC-01 through TC-05, TC-09, TC-12
- Error/edge cases: TC-06, TC-07, TC-08, TC-13
- Integration behavior: TC-10, TC-11 (config resolution)
- Manual testing: dialog UX in exe (not automatable with Tkinter unit tests easily)
