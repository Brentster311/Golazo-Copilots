# Role Decision Document: Program Manager

**Work Item**: CALJACK-002 - Card Dealing and Initial Game Setup  
**Role**: Program Manager  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] User Story exists at `docs/workitems/CALJACK-002-user-story.md`

---

## Decisions Made

### 1. Card Model Design
- Immutable Card class with suit and rank
- Value method for scoring (used in CALJACK-004)
- Comparison methods for trick resolution (CALJACK-003)

### 2. Deck Model Design
- List-based storage with shuffle
- Deal method removes cards from deck
- Top card visible for trump/stock

### 3. GameState Model Design
- Encapsulates all game state (hands, stock, trump, current player)
- Factory method `new_game()` for clean initialization
- Designed for future AI integration

### 4. Card Rendering
- Programmatic drawing (no image assets)
- 70x100px cards with suit symbols
- Red/Black color scheme
- Card back for face-down cards

### 5. Hand Visibility
- Current player's hand: face-up
- Opponent's hand: face-down (realistic for hot-seat)

---

## Alternatives Considered

| Decision | Selected | Rejected | Rationale |
|----------|----------|----------|-----------|
| Card graphics | Programmatic | Image sprites | No asset dependencies |
| Hand visibility | Opponent face-down | Both face-up | Realistic gameplay |
| State management | GameState class | Global variables | Encapsulation for AI |

---

## Tradeoffs Accepted

1. **No card images**: Less polished but simpler
2. **Face-down opponent hand**: More realistic but needs turn transition UI later
3. **Fixed card size**: 70x100px may need adjustment on different screens

---

## Known Limitations or Risks

1. **Card rendering complexity**: Drawing 52 unique cards requires careful implementation
2. **Performance**: Many cards on screen; may need Surface caching
3. **Hot-seat realism**: Opponent hand is hidden but still in memory

---

## Next Role

Ready for **Reviewer** to critique the User Story and Design Doc.
