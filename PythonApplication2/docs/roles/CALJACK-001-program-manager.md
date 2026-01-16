# Role Decision Document: Program Manager

**Work Item**: CALJACK-001 - Main Menu and Game Window Foundation  
**Role**: Program Manager  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] User Story exists at `docs/workitems/CALJACK-001-user-story.md`

---

## Decisions Made

### 1. Architecture Pattern: State Machine
Selected state machine pattern for screen management because:
- Clean separation of concerns (each screen is a state)
- Easy to add new screens (Game Over, Settings, etc.)
- Testable in isolation
- Common pattern for game development

### 2. Project Structure
Organized code into logical modules:
- `main.py` - Entry point with game loop
- `game/constants.py` - Centralized configuration
- `game/states/` - Screen implementations
- `game/ui/` - Reusable UI components

This structure supports:
- Future AI integration (game logic separate from UI)
- Future save/load (game state encapsulated)
- Testability (small, focused modules)

### 3. Placeholder States
Created placeholder states for Game and Help screens:
- Allows clean transitions now
- Downstream stories (CALJACK-002, CALJACK-006) fill in implementations
- Prevents integration surprises

### 4. Visual Design Defaults
Made explicit assumptions for unspecified visuals:
- Background: Dark green (#2E7D32) - card table feel
- Buttons: Simple rectangles, no hover effects
- Font: Pygame default (cross-platform safe)

---

## Alternatives Considered

### Scene Management
| Option | Evaluation |
|--------|------------|
| No pattern (if/else) | Rejected - unmaintainable |
| **State machine** | Selected - clean, extensible |
| Third-party scene library | Rejected - unnecessary dependency |

### Code Organization
| Option | Evaluation |
|--------|------------|
| Single file | Rejected - will become unmaintainable |
| **Modular structure** | Selected - supports future stories |
| Over-engineered (too many layers) | Rejected - overkill for card game |

---

## Tradeoffs Accepted

1. **More upfront structure**: State machine adds initial code, but pays off in CALJACK-002+
2. **No hover effects**: Simpler MVP, can enhance later if needed
3. **Fixed window size**: No responsive design; simplifies layout calculations

---

## Known Limitations or Risks

1. **Pygame learning curve**: Team may need ramp-up time
2. **No automated visual testing**: Pygame UI testing is manual
3. **Placeholder states are empty**: Will show blank screens until downstream stories complete

---

## Validation

- [x] User Story exists at `docs/workitems/CALJACK-001-user-story.md`
- [x] Design Doc created at `docs/design/CALJACK-001-design-doc.md`
- [x] All functional requirements traced to acceptance criteria
- [x] Business case articulated
- [x] Test strategy outlined

---

## Next Role

Ready for **Reviewer** to critique the User Story and Design Doc.
