# Design Doc: CALJACK-003

## Summary

Implement trick-taking gameplay and card drawing for California Jack. This includes playing cards from hand, validating legal plays, determining trick winners, drawing replacement cards from stock, and managing turn order.

---

## Problem Statement

CALJACK-002 provides dealt cards and game setup, but players cannot interact with their cards. This story enables:
1. Clicking cards to play them
2. Following suit/trump rules
3. Determining trick winners
4. Drawing from stock after each trick
5. Continuing until all 52 cards are played

---

## Business Case

### Why Now
- CALJACK-002 is complete; this is the core gameplay
- Without trick-taking, the game is just a card display

### Impact
- Players can actually play California Jack
- Enables scoring (CALJACK-004) and win detection (CALJACK-005)

### KPIs
- All 52 cards played correctly
- Trick winner determined correctly per rules
- Stock drawing works correctly

---

## Stakeholders

| Role | Interest |
|------|----------|
| Project Owner | Playable California Jack game |
| Players | Interactive gameplay experience |

---

## Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-001 | Click card to play it | AC #1 |
| FR-002 | Validate legal plays (follow suit/trump rules) | AC #2 |
| FR-003 | Show visual feedback for invalid plays | AC #2 |
| FR-004 | Determine trick winner correctly | AC #3 |
| FR-005 | Winner draws top card from stock | AC #4 |
| FR-006 | Loser draws next card from stock | AC #4 |
| FR-007 | Winner leads next trick | AC #5 |
| FR-008 | Continue until all cards played | AC #6 |

---

## Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-001 | Turn transitions < 100ms | User Story |
| NFR-002 | Game state supports future save/load | User Story |

---

## California Jack Rules Reference

### Following Suit
1. **Lead player**: May play any card
2. **Second player**: 
   - MUST follow suit if able
   - If cannot follow suit, MUST trump if able
   - If cannot follow suit OR trump, may play any card

### Determining Winner
- Higher card of **lead suit** wins, UNLESS
- A **trump** card is played, then highest trump wins

### Drawing from Stock
- **Trick winner** draws the top card (face-up)
- **Trick loser** draws the next card (now face-up)
- When stock is exhausted, play remaining 6 tricks without drawing

---

## Proposed Approach (High Level)

### Phase 1: Trick Model

```python
@dataclass
class Trick:
    lead_card: Optional[Card] = None
    follow_card: Optional[Card] = None
    lead_player: int = 1
    
    def is_complete(self) -> bool
    def winner(self, trump_suit: str) -> int
```

### Phase 2: Game State Updates

Update `CaliforniaJackGame` model:

```python
@dataclass
class CaliforniaJackGame:
    # Existing fields...
    current_trick: Optional[Trick] = None
    tricks_won: List[int] = field(default_factory=list)  # For scoring later
    
    def can_play_card(self, player: int, card: Card) -> bool
    def play_card(self, player: int, card: Card) -> None
    def resolve_trick(self) -> int  # Returns winner
    def draw_cards(self, winner: int) -> None
    def is_game_over(self) -> bool
```

### Phase 3: UI Updates

Update `GameState` UI class:

```python
class GameState(BaseState):
    def _get_clicked_card(self, pos) -> Optional[Card]
    def _highlight_invalid_card(self, card: Card) -> None
    def _draw_current_trick(self, screen) -> None
    def _draw_played_cards(self, screen) -> None
```

### UI Layout for Trick Play

```
??????????????????????????????????????????????????????
?                 Player 2 Hand                       ?
?    [?][?][?][?][?][?]                              ?
??????????????????????????????????????????????????????
?                                                     ?
?  Stock [38]     ???????????????     Trump: ?       ?
?  [Top Card]     ? Play Area   ?                    ?
?                 ? [P1] [P2]   ?                    ?
?                 ???????????????                    ?
??????????????????????????????????????????????????????
?                 Player 1 Hand                       ?
?    [A?][K?][Q?][J?][10?][9?]  ? Click to play    ?
??????????????????????????????????????????????????????
```

---

## Alternatives Considered

### Card Selection
| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| **Click to play** | Intuitive, simple | Single action | **Selected** |
| Drag and drop | More tactile | Complex, harder to implement | Rejected |
| Click to select, then confirm | Less error-prone | Two clicks, slower | Rejected |

### Invalid Play Feedback
| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| **Card shake/highlight** | Visual, quick | No explanation | **Selected** |
| Error message popup | Explains why | Interrupts flow | Rejected |
| Disable invalid cards | Prevents errors | May confuse about rules | Deferred to future |

---

## Risks, Mitigations, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Follow-suit logic bugs | Medium | High | Extensive unit tests |
| Click detection on overlapping cards | Low | Medium | Check from right to left (top card first) |
| Turn order confusion | Low | Medium | Clear turn indicator |

### Open Questions

| Question | Status |
|----------|--------|
| What happens if player clicks wrong card? | **Assumption**: Show error, allow retry |
| Show played cards briefly before clearing? | **Assumption**: Yes, 1 second delay |

---

## Dependencies

### Upstream
- CALJACK-002 (complete) - provides Card, Deck, CaliforniaJackGame

### Downstream
- CALJACK-004 (scoring) - uses tricks_won data
- CALJACK-005 (win condition) - uses is_game_over()

### External
- None

---

## Migration / Rollout / Rollback Plan

### Rollout
1. Add Trick model with tests
2. Update CaliforniaJackGame with trick logic
3. Add UI card click handling
4. Add play area display
5. Add invalid play feedback
6. Test complete game flow

### Rollback
- Revert to CALJACK-002 state if issues found
- Game will show cards but not allow play

---

## Observability Plan

- Console logging for card plays (DEBUG level)
- Log trick winners
- Log draw operations

---

## Test Strategy Summary

| Test Type | Scope | Approach |
|-----------|-------|----------|
| Unit | Trick winner determination | pytest - all suit/trump combinations |
| Unit | Follow suit validation | pytest - can/cannot follow scenarios |
| Unit | Card drawing | pytest - winner/loser draw order |
| Integration | Full trick cycle | pytest |
| Visual | Card click, play area, feedback | Manual + Project Owner verification |

Key test scenarios:
1. Lead player can play any card
2. Follow player must follow suit if able
3. Follow player must trump if cannot follow suit
4. Higher same-suit card wins
5. Trump beats non-trump
6. Higher trump beats lower trump
7. Winner draws first, loser draws second
8. Game ends when all cards played
