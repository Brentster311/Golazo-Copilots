# SFI-022: View & Manage Saved LLM Analyses

**Status**: IN PROGRESS

---

## User Story

**Title**: View previously saved LLM analyses from the KPI context menu

**As a**: SFI engineer using the S360Reporter desktop app  
**I want**: To right-click a KPI row and see whether a saved analysis exists, view it without re-calling the LLM, and optionally re-analyze to get a fresh result  
**So that**: I can quickly revisit prior analysis work without waiting for the LLM again, and I can refresh the analysis when circumstances change

---

## Out of Scope

- Exporting analyses to PDF, Word, or email
- Comparing two analysis versions side-by-side
- Searching or filtering across saved analyses
- Bulk management (delete all, export all)
- Editing the saved analysis text manually

---

## Assumptions

- **Assumption (explicit)**: SFI-020 (core Analyze with LLM + save to disk) is already implemented — saved analyses exist as JSON files under `%LOCALAPPDATA%/GUI/analyses/`
- **Assumption (explicit)**: The right-click context menu will show "View Saved Analysis" when a saved analysis exists for that action item, in addition to "Analyze with LLM" (re-analyze)
- **Assumption (explicit)**: Viewing a saved analysis uses the same modal as a fresh analysis, but loads instantly from disk with a "Saved on [timestamp]" indicator
- **Assumption (explicit)**: Re-analyzing overwrites the previous saved analysis (no version history in this story)
- **Assumption (explicit)**: The context menu dynamically checks for a saved file to decide which options to show

---

## Acceptance Criteria

- [ ] Right-click context menu shows "View Saved Analysis" when a saved analysis JSON exists for the selected action item
- [ ] Selecting "View Saved Analysis" loads the result from disk and displays it in the analysis modal with a "Saved on [date/time]" header
- [ ] "Analyze with LLM" (re-analyze) remains available even when a saved analysis exists
- [ ] Re-analyzing replaces the previously saved file with the new result
- [ ] If the saved JSON file is corrupted or unreadable, the user sees an error message and is offered "Analyze with LLM" as a fallback

---

## Non-Functional Requirements

- Loading a saved analysis from disk should complete in under 1 second
- Saved JSON format must be forward-compatible (include a schema version field)
- Should work on Windows (primary platform)

---

## Telemetry / Metrics Expected

- Count of "View Saved Analysis" vs. "Analyze with LLM" (re-analyze) invocations
- Age of viewed saved analyses (how stale are they when users view them?)

---

## Rollout / Rollback Notes

- Feature is additive to SFI-020's context menu
- Rollback: remove the "View Saved Analysis" menu option; saved files remain on disk
