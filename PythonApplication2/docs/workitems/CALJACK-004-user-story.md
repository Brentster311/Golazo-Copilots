# User Story: CALJACK-004

**Status**: BACKLOG

---

## User Story

**Title**: Hand Scoring (High, Low, Jack, Game)

**As a**: Player

**I want**: To receive points at the end of each hand based on captured cards

**So that**: My progress toward winning is tracked correctly

---

## Out of Scope

- Win condition / game over (see CALJACK-005)
- Help screen (see CALJACK-006)

---

## Assumptions

- **Assumption (explicit)**: Tie in "Game" points results in no point awarded for Game
- **Assumption (explicit)**: Score display visible during gameplay

---

## Game Rules Reference

One point each for capturing:
- **High**: Ace of trumps
- **Low**: Deuce (2) of trumps
- **Jack**: Jack of trumps
- **Game**: Most counting card points (10=10, A=4, K=3, Q=2, J=1)

---

## Acceptance Criteria (bulleted, testable)

- [ ] At end of hand, High (Ace of trumps) awards 1 point to capturer
- [ ] At end of hand, Low (2 of trumps) awards 1 point to capturer
- [ ] At end of hand, Jack (Jack of trumps) awards 1 point to capturer
- [ ] At end of hand, Game (most counting points) awards 1 point; tie = no point
- [ ] Both players' scores displayed and updated after each hand
- [ ] Hand summary shows which points were awarded to whom

---

## Non-functional Requirements

- Score calculation completes within 100ms

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Depends on CALJACK-003 for trick-taking
