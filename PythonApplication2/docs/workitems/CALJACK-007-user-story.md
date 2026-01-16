# User Story: CALJACK-007

**Status**: BACKLOG

---

## User Story

**Title**: Display Last Won Trick

**As a**: Player

**I want**: To see the last completed trick displayed on screen

**So that**: I can remember what cards were played and track the game progress

---

## Out of Scope

- Trick history beyond the last trick
- Clickable trick display
- Animation of trick movement

---

## Assumptions

- **Assumption (explicit)**: Last trick shown in corner based on winner (Player 1 = bottom-right, Player 2 = top-right)
- **Assumption (explicit)**: Trick display is smaller than regular cards (scaled down)
- **Assumption (explicit)**: Label shows who won the trick

---

## Acceptance Criteria (bulleted, testable)

- [ ] After a trick is resolved, the two cards are displayed in a corner
- [ ] Player 1's won tricks appear in bottom-right corner
- [ ] Player 2's won tricks appear in top-right corner
- [ ] Display includes label showing "P1 Won" or "P2 Won"
- [ ] Only the most recent trick is shown (replaces previous)

---

## Non-functional Requirements

- Trick display should not overlap with hand cards or stock
- Cards should be recognizable (not too small)

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Depends on CALJACK-003 for trick resolution
