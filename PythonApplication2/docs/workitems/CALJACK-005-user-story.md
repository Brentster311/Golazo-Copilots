# User Story: CALJACK-005

**Status**: BACKLOG

---

## User Story

**Title**: Win Condition and Game Over

**As a**: Player

**I want**: The game to end when a player reaches 10 points with a winner announced

**So that**: I know who won and can start a new game

---

## Out of Scope

- Help screen (see CALJACK-006)
- AI opponent (future iteration)

---

## Assumptions

- **Assumption (explicit)**: Tiebreaker order is High, Low, Jack, Game
- **Assumption (explicit)**: Game over screen offers "Play Again" and "Main Menu" options

---

## Game Rules Reference

- First player to 10 points wins
- If both reach 10 in same hand, points count in order: High, Low, Jack, Game

---

## Acceptance Criteria (bulleted, testable)

- [ ] Game ends immediately when a player reaches 10+ points
- [ ] If both players reach 10 in same hand, winner determined by point order (High, Low, Jack, Game)
- [ ] Game over screen displays winner announcement
- [ ] Game over screen shows final scores
- [ ] "Play Again" button starts a new game (scores reset)
- [ ] "Main Menu" button returns to main menu

---

## Non-functional Requirements

- Game over detection occurs immediately after scoring

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Depends on CALJACK-004 for scoring
