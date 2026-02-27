# SFI-020 — Quality Assurance Decision Notes

## Work Item
**SFI-020**: Right-Click KPI Row → Analyze with LLM (Core)

## QA Review of Design Doc

### Coverage Assessment
- **17 test cases** cover all 5 acceptance criteria:
  - AC1 (Context menu on right-click): TC-11, TC-12
  - AC2 (LLM call + structured modal): TC-3, TC-4, TC-5, TC-13
  - AC3 (Save to disk): TC-7, TC-8, TC-9, TC-10, TC-14
  - AC4 (UI responsive / background thread): Covered implicitly by threading model in TC-13, TC-14
  - AC5 (Error handling): TC-2, TC-6, TC-15, TC-16
- **Security**: TC-17 (key masking)
- **Assessment**: Good coverage. No gaps found.

### Test Feasibility
- All tests are mockable without real Azure OpenAI calls ✅
- tkinter tests follow existing `test_tk_app.py` patterns ✅
- Storage tests use `tmp_path` fixture (standard pytest) ✅

### Edge Cases Noted
1. **Concurrent analysis**: What if user closes progress modal mid-flight? Thread should handle gracefully (daemon=True ensures cleanup).
2. **Empty detailed_items**: If `current_data['detailed_items']` is empty for a KPI, the handler should show a meaningful message rather than sending empty data to the LLM.
3. **Very long action item title**: Could overflow modal title bar — use truncation.

### Recommendations for Developer
- Add edge case test: trigger analysis when `detailed_items` list has no matching items for the selected KPI → should show error, not crash.
- Ensure `AnalysisProgressModal` handles window close (WM_DELETE_WINDOW) by ignoring it (prevent user from closing mid-analysis).

## Sign-off
- Design is testable, modular, and well-scoped.
- Test cases are sufficient for acceptance criteria validation.
- **QA Status**: ✅ Approved for development
