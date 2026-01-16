# Role Decision Document: Project Owner Assistant

**Work Items**: CALJACK-008, CALJACK-009, CALJACK-010  
**Role**: Project Owner Assistant  
**Date**: 2025-01-XX

---

## Work Items Created

### CALJACK-008: Confirm Exit During Game
- **Scope**: Show "End the game?" confirmation when clicking Back during active game
- **Dependencies**: CALJACK-003 (game state)
- **AC Count**: 6 items ?

### CALJACK-009: Always Highlight Invalid Cards
- **Scope**: Continuously highlight invalid cards instead of only on click
- **Dependencies**: CALJACK-003 (can_play_card validation)
- **AC Count**: 6 items ?

### CALJACK-010: Settings Menu with Language Selection
- **Scope**: Add Settings menu with English/Chinese/Russian language options
- **Dependencies**: None (independent)
- **AC Count**: 7 items ?
- **Note**: Includes translation table for all UI strings

---

## Decisions Made

1. **CALJACK-008**: Dialog-based confirmation (not toast/notification)
2. **CALJACK-009**: Gray/dim invalid cards (clearer than subtle border)
3. **CALJACK-010**: Three languages based on user request; included full translation table

---

## Dependency Analysis

| Work Item | Dependencies | Can Start |
|-----------|--------------|-----------|
| CALJACK-008 | CALJACK-003 ? | Yes |
| CALJACK-009 | CALJACK-003 ? | Yes |
| CALJACK-010 | None | Yes |

All three can be worked on now.

---

## Backlog Summary

| ID | Title | Status | Dependencies |
|----|-------|--------|--------------|
| CALJACK-004 | Scoring System | BACKLOG | CALJACK-003 ? |
| CALJACK-005 | Win Condition | BACKLOG | CALJACK-004 |
| CALJACK-006 | Help Screen | BACKLOG | None |
| CALJACK-007 | Display Last Won Trick | BACKLOG | CALJACK-003 ? |
| CALJACK-008 | Confirm Exit During Game | BACKLOG | CALJACK-003 ? |
| CALJACK-009 | Always Highlight Invalid Cards | BACKLOG | CALJACK-003 ? |
| CALJACK-010 | Settings with Language Selection | BACKLOG | None |
