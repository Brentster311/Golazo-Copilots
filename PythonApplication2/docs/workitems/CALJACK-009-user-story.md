# User Story: CALJACK-009

**Status**: BACKLOG

---

## User Story

**Title**: Always Highlight Invalid Cards

**As a**: Player

**I want**: To always see which cards I cannot legally play

**So that**: I can quickly identify my valid options without trial and error

---

## Out of Scope

- Tooltip explaining why card is invalid
- Different highlight colors for different reasons

---

## Assumptions

- **Assumption (explicit)**: Invalid cards are grayed out or have red tint
- **Assumption (explicit)**: Valid cards remain normal appearance
- **Assumption (explicit)**: Only applies to current player's visible hand
- **Assumption (explicit)**: When leading (no trick in progress), all cards are valid

---

## Acceptance Criteria (bulleted, testable)

- [ ] When it's player's turn, invalid cards are visually marked
- [ ] Invalid cards have dimmed/grayed appearance or red border
- [ ] Valid cards have normal appearance
- [ ] Highlighting updates immediately when trick state changes
- [ ] When leading a trick, all cards appear valid (no highlighting)
- [ ] Clicking invalid card still shows brief error feedback

---

## Non-functional Requirements

- Visual distinction should be clear but not distracting
- Must work with all card colors (red and black suits)

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Depends on CALJACK-003 for can_play_card validation
- Replaces temporary red highlight on invalid click
