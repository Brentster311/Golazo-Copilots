# User Story: CALJACK-008

**Status**: BACKLOG

---

## User Story

**Title**: Confirm Exit During Game

**As a**: Player

**I want**: To be warned when I try to leave a game in progress

**So that**: I don't accidentally lose my game progress

---

## Out of Scope

- Save/load game functionality
- Auto-save on exit

---

## Assumptions

- **Assumption (explicit)**: Confirmation dialog appears as modal overlay
- **Assumption (explicit)**: Two buttons: "Yes, Exit" and "Cancel"
- **Assumption (explicit)**: Pressing Cancel returns to game in same state

---

## Acceptance Criteria (bulleted, testable)

- [ ] Clicking "Back" button during active game shows confirmation dialog
- [ ] Dialog displays "End the game?" message
- [ ] "Yes, Exit" button returns to main menu
- [ ] "Cancel" button closes dialog and resumes game
- [ ] Game state is preserved while dialog is shown
- [ ] If game is already over, no confirmation needed (direct exit)

---

## Non-functional Requirements

- Dialog should appear centered on screen
- Dialog should dim/overlay the game background

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Depends on CALJACK-003 for game state
