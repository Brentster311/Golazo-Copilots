# SFI-022 Program Manager Role Decision Notes

## Design Approach

Chose the minimal-change approach: enhance existing context menus and `AnalysisModal` rather than creating new UI components. This keeps the change surface small and testable.

## Key Decisions

1. **Conditional menu item**: "View Saved Analysis" only appears when `analysis_exists()` returns True. This avoids confusing users with a menu item that would just show an error.
2. **Reuse AnalysisModal**: Added `saved` flag rather than a separate modal class. The only visual difference is a "Saved on [timestamp]" header.
3. **Error handling on corrupted files**: User sees a messagebox with fallback guidance ("Use Analyze with LLM"). No crash, no silent failure.
4. **No new dependencies**: Everything uses existing `llm_storage` functions.

## Scope Confirmation

All 5 acceptance criteria from the user story are addressable with the proposed design.
