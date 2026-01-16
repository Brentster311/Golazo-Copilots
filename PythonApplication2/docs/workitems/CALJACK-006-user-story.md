# User Story: CALJACK-006

**Status**: BACKLOG

---

## User Story

**Title**: Help Screen with Rules and Attribution

**As a**: Player

**I want**: To view the game rules and see credit to the source

**So that**: I can learn how to play and know where the rules came from

---

## Out of Scope

- Gameplay features (covered in CALJACK-001 through CALJACK-005)
- Tutorial mode (future iteration)

---

## Assumptions

- **Assumption (explicit)**: Help screen is scrollable if content exceeds viewport
- **Assumption (explicit)**: Hyperlink opens in system default browser

---

## Rules Content (to display)

### Rank of Cards
A (high), K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2.

### Deal
Deal 6 cards to each player. Remaining cards form face-up stock. Top card determines trump.

### The Play
- Non-dealer leads first
- Must follow suit or trump if able; else play any card
- Higher same-suit or trump wins trick
- Winner draws top stock card; loser draws next
- When stock empty, play out remaining hands

### Scoring (per hand)
- High (Ace of trumps): 1 point
- Low (2 of trumps): 1 point
- Jack (Jack of trumps): 1 point
- Game (most counting points): 1 point

### Counting Cards
10=10, A=4, K=3, Q=2, J=1

### Winning
First to 10 points. Tiebreaker order: High, Low, Jack, Game.

---

## Acceptance Criteria (bulleted, testable)

- [ ] Help screen accessible from main menu
- [ ] Help screen displays complete rules (as above)
- [ ] Help screen credits "Bicycle Cards" as source
- [ ] Help screen includes clickable link to https://bicyclecards.com/how-to-play/california-jack/
- [ ] "Back" button returns to main menu

---

## Non-functional Requirements

- Text is readable (appropriate font size)
- Link opens in default browser

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Depends on CALJACK-001 for menu navigation
