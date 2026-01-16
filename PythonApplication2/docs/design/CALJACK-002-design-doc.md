# Design Doc: CALJACK-002

## Summary

Implement card dealing and initial game setup for California Jack. This includes creating a 52-card deck, shuffling, dealing 6 cards to each player, displaying the stock pile with visible top card, showing trump suit, and indicating which player leads first.

---

## Problem Statement

CALJACK-001 provided the menu and navigation foundation, but clicking "New Game" shows a placeholder screen. Players need to see:
1. Their dealt cards
2. The stock pile with top card visible
3. The trump suit indicator
4. Who plays first

Without this, no actual gameplay can occur.

---

## Business Case

### Why Now
- CALJACK-001 is complete; this is next in the dependency chain
- Enables visual verification that card logic works before adding trick-taking

### Impact
- Players can see a real game setup (not placeholder)
- Card and deck classes become available for CALJACK-003 (trick-taking)
- Foundation for all card-related features

### KPIs
- 52 cards created correctly
- 6 cards dealt to each player
- 40 cards in stock
- Trump suit matches top card of stock

---

## Stakeholders

| Role | Interest |
|------|----------|
| Project Owner | Playable California Jack game |
| Players | See dealt cards, understand game state |
| Developer (future) | Card/Deck classes for AI integration |

---

## Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-001 | Create shuffled 52-card deck | AC #1 |
| FR-002 | Deal 6 cards to each player | AC #2 |
| FR-003 | Remaining 40 cards form stock pile | AC #3 |
| FR-004 | Top card of stock visible | AC #3 |
| FR-005 | Display trump suit based on top card | AC #4 |
| FR-006 | Display both players' hands | AC #5 |
| FR-007 | Show turn indicator (Player 1 leads) | AC #6 |

---

## Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-001 | Cards visually distinguishable by suit and rank | User Story |
| NFR-002 | Game state encapsulated for future AI | User Story |
| NFR-003 | Card rendering performant (60 FPS maintained) | Implicit |

---

## Proposed Approach (High Level)

### New Classes

```
game/
??? models/
?   ??? __init__.py
?   ??? card.py          # Card class (suit, rank)
?   ??? deck.py          # Deck class (52 cards, shuffle, deal)
?   ??? game_state.py    # GameState class (players, stock, trump)
??? ui/
    ??? card_renderer.py # Draw cards programmatically
```

### Card Model

```python
class Card:
    suit: str      # 'hearts', 'diamonds', 'clubs', 'spades'
    rank: str      # '2'-'10', 'J', 'Q', 'K', 'A'
    
    def value(self) -> int:  # For "Game" scoring: 10=10, A=4, K=3, Q=2, J=1
    def __lt__(self, other): # For trick comparison
```

### Deck Model

```python
class Deck:
    cards: List[Card]
    
    def shuffle(self) -> None
    def deal(self, count: int) -> List[Card]
    def top_card(self) -> Optional[Card]
    def draw(self) -> Optional[Card]
```

### GameState Model

```python
class GameState:
    player1_hand: List[Card]
    player2_hand: List[Card]
    stock: Deck
    trump_suit: str
    current_player: int  # 1 or 2
    
    @classmethod
    def new_game(cls) -> 'GameState'
```

### Card Renderer

```python
class CardRenderer:
    def draw_card(self, screen, card, x, y, face_up=True) -> None
    def draw_card_back(self, screen, x, y) -> None
```

### GameState Integration

Replace `GameState` placeholder with actual implementation:
- Initialize `GameState.new_game()` when entering game state
- Render player hands, stock, trump indicator

---

## Card Rendering Design

### Card Dimensions
- Width: 70px
- Height: 100px
- Rounded corners: 5px radius

### Card Face
```
???????????
? A       ?  <- Rank (top-left)
?   ?     ?  <- Suit symbol (center)
?       A ?  <- Rank (bottom-right, inverted)
???????????
```

### Colors
- Background: White
- Hearts/Diamonds: Red (#D32F2F)
- Clubs/Spades: Black (#212121)
- Card back: Dark blue pattern

### Layout
```
??????????????????????????????????????????????????
?                 Player 2 Hand                   ?
?    [?][?][?][?][?][?]  (face-down or face-up)  ?
??????????????????????????????????????????????????
?                                                 ?
?  Stock [40]     Trump: ?                       ?
?  [Top Card]                                     ?
?                                                 ?
??????????????????????????????????????????????????
?                 Player 1 Hand                   ?
?    [A?][K?][Q?][J?][10?][9?]  (face-up)       ?
?              ? Current Player                   ?
??????????????????????????????????????????????????
```

---

## Alternatives Considered

### Card Representation
| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Image sprites | Professional look | Requires assets, licensing | Rejected |
| **Programmatic drawing** | No assets, customizable | More code | **Selected** |
| Unicode symbols only | Very simple | Limited styling | Rejected |

### Deck Storage
| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| **List with shuffle** | Simple, standard | Random order | **Selected** |
| Pre-defined order | Deterministic | Not realistic | Rejected |

### Hand Visibility
| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Both face-up | Easier testing | Spoils game for hot-seat | Rejected |
| **Current player face-up** | Realistic | Need turn transition | **Selected** |
| Both face-down until turn | Most realistic | Complex UI | Deferred |

---

## Risks, Mitigations, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Card rendering performance | Low | Medium | Use pygame Surface caching |
| Card overlap in hand | Low | Low | Calculate spacing based on hand size |
| Suit symbols not rendering | Low | Low | Use ASCII fallback (H, D, C, S) |

### Open Questions

| Question | Status |
|----------|--------|
| Show opponent's hand face-up or face-down? | **Assumption**: Face-down for realism (hot-seat) |
| Card spacing in hand? | **Assumption**: Overlap if >6 cards, fixed spacing otherwise |

---

## Dependencies

### Upstream
- CALJACK-001 (complete) - provides GameState placeholder, state machine

### Downstream
- CALJACK-003 (trick-taking) - uses Card, Deck, GameState
- CALJACK-004 (scoring) - uses Card.value()

### External
- None (pygame already installed)

---

## Migration / Rollout / Rollback Plan

### Rollout
1. Create Card and Deck models with tests
2. Create GameState model with tests
3. Create CardRenderer UI component
4. Replace GameState placeholder with real implementation
5. Test complete game setup flow

### Rollback
- Revert to CALJACK-001 placeholder if issues found
- Card models are isolated, easy to revert

---

## Observability Plan

- Console logging for deal operations (DEBUG level)
- Log trump suit selection
- Log hand sizes after deal

---

## Test Strategy Summary

| Test Type | Scope | Approach |
|-----------|-------|----------|
| Unit | Card creation/comparison | pytest |
| Unit | Deck shuffle/deal | pytest |
| Unit | GameState initialization | pytest |
| Integration | Full game setup flow | pytest + manual |
| Visual | Card rendering | Manual inspection |

Key test scenarios:
1. Deck has exactly 52 unique cards
2. Shuffle produces different orders
3. Deal removes cards from deck
4. Each player gets 6 cards
5. Stock has 40 cards after deal
6. Trump matches top card suit
7. Player 1 leads first
