# SFI-022 — Project Owner Assistant Decision Notes

## Work Item
**SFI-022**: View & Manage Saved LLM Analyses

## Decisions Made

### Why a Separate Story
- The Project Owner explicitly stated "NOT in memory only. I don't want to lose it." — SFI-020 handles the initial save, but viewing/managing saved results is a distinct user interaction.
- This story has its own happy path: right-click → see "View Saved Analysis" → load from disk → display instantly.
- It's independently testable: create a saved JSON file manually, verify the UI loads and displays it.

### Scope
- Add "View Saved Analysis" to the right-click context menu (conditional on a saved file existing).
- Load and display saved analysis in the same modal used by SFI-020.
- Re-analyze option overwrites the saved file (no version history).
- Graceful handling of corrupted/unreadable saved files.

### Interface / Platform / Persistence / User Type
- Same as SFI-020: GUI (tkinter), Windows, reads from `%LOCALAPPDATA%/GUI/analyses/`, technical users.

### Key Design Decisions
1. **Dynamic context menu**: Menu options change based on whether a saved analysis exists. This keeps the UI clean — no disabled/greyed-out options.
2. **Same modal for saved and fresh analysis**: Reduces UI complexity. A "Saved on [timestamp]" header distinguishes the two.
3. **No version history**: Overwrite on re-analyze. Version history would add significant complexity for low value at this stage.
4. **Schema version field**: Future-proofs the JSON format so later stories can migrate old analysis files if the format changes.

## Risks
- Users may expect version history or comparison features — explicitly out of scope, could be a follow-up.
- Accumulated stale analysis files may consume disk space — cleanup/management not in scope.
