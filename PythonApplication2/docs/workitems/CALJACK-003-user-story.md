# User Story: CALJACK-003

**Status**: IMPLEMENTED

---

## User Story

**Title**: Trick-Taking Gameplay and Card Drawing

**As a**: Player

**I want**: To play cards in tricks following the rules and draw from stock

**So that**: I can experience the core California Jack gameplay loop

---

## Out of Scope

- Scoring points (see CALJACK-004)
- Win detection (see CALJACK-005)
- Help screen (see CALJACK-006)
- Display last won trick (see CALJACK-007)

---

## Assumptions

- **Assumption (explicit)**: Hot-seat multiplayer (players share screen)
- **Assumption (explicit)**: Invalid plays rejected with visual feedback (card highlights or message)

---

## Game Rules Reference

- Second player must follow suit or trump if able; else play any card
- Card led loses to higher card of same suit or to a trump, wins otherwise
- Winner draws top stock card; loser draws next card
- When stock exhausted, play remaining 6 cards from hands

---

## Acceptance Criteria (bulleted, testable)

- [x] Current player can click a card to play it
- [x] Invalid card plays are rejected with visual feedback
- [x] Trick winner determined correctly (higher same-suit or trump wins)
- [x] Winner of trick draws top card from stock; loser draws next
- [x] Winner of trick leads next trick
- [x] Game continues until all 52 cards have been played (stock empty + hands empty)

---

## Non-functional Requirements

- Turn transitions respond within 100ms ?
- Game state allows future save/load feature ?

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Depends on CALJACK-002 for deal/setup
