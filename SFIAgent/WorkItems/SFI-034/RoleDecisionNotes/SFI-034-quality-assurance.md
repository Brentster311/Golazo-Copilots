# SFI-034 — Quality Assurance Decision Notes

## Review Summary

Design approved with comments. Key items for implementation:
- Connection lifecycle must be handled in `send_analysis_prompt` (Comment #3)
- Thread safety via `root.after(0, ...)` for background→UI handoff (Comment #4)
- URL deduplication before fetching (Comment #2)

## Test Coverage Strategy

- 13 test cases covering all 6 acceptance criteria + NFRs
- Mix of unit tests (prompt building, URL fetching, text extraction) and integration (end-to-end flow)
- TC-4/5 cover graceful degradation scenarios
- TC-11 specifically covers the disconnected panel edge case from review comment #3

## Capability Impact

The feature touches `copilot_panel.py`, `dialogs.py`, and adds `kpi_analyzer.py`. No existing capability contracts are broken — this replaces a stub with working code.
