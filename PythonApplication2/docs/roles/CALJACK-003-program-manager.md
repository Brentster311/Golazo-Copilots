# Role Decision Document: Program Manager

**Work Item**: CALJACK-003 - Trick-Taking Gameplay and Card Drawing  
**Role**: Program Manager  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] User Story exists at `docs/workitems/CALJACK-003-user-story.md`

---

## Decisions Made

### 1. Trick Model Design
- New `Trick` dataclass to track lead/follow cards and determine winner
- Separate from game state for clarity

### 2. Game State Updates
- Add `current_trick` field to track in-progress trick
- Add `can_play_card()` for validation
- Add `play_card()`, `resolve_trick()`, `draw_cards()` methods

### 3. UI Interaction
- Click card to play (single action)
- Invalid plays show visual feedback (card highlight/shake)
- Play area in center shows current trick

### 4. Timing
- Brief delay (1 second) to show completed trick before clearing

---

## Alternatives Considered

| Decision | Selected | Rejected | Rationale |
|----------|----------|----------|-----------|
| Card selection | Click to play | Drag/drop | Simpler to implement |
| Invalid feedback | Visual highlight | Error popup | Less disruptive |

---

## Tradeoffs Accepted

1. **Single click to play**: May cause accidental plays, but faster gameplay
2. **Visual-only feedback**: No sound effects, keeps implementation simple

---

## Known Limitations or Risks

1. **Follow-suit logic complexity**: Many edge cases to test
2. **Overlapping card clicks**: Need to check rightmost card first
3. **Hot-seat visibility**: Both players can see opponent's hand during their turn

---

## Next Role

Ready for **Reviewer** to critique the User Story and Design Doc.
