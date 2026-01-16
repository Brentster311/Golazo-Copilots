# Role Decision Document: Tester

**Work Item**: CALJACK-002 - Card Dealing and Initial Game Setup  
**Role**: Tester  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] User Story exists at `docs/workitems/CALJACK-002-user-story.md`
- [x] Review Notes exist at `docs/design/CALJACK-002-review-notes.md` (includes Reviewer + Architect)

---

## TDD Verification ?

### Test Execution
```bash
cd PythonApplication2/PythonApplication2
python -m pytest tests/test_card.py tests/test_deck.py tests/test_game_state_model.py --tb=no -q
```

### Result: **58 FAILED** ?

All tests fail with `ModuleNotFoundError: No module named 'game.models'` because production code does not exist yet.

This confirms TDD is working correctly:
- Tests exist before production code
- Tests fail initially
- Developer will make tests pass

---

## Test Files Created

| File | Tests | Purpose |
|------|-------|---------|
| `tests/test_card.py` | 20 | Card model (suit, rank, value, points) |
| `tests/test_deck.py` | 21 | Deck model (shuffle, deal, draw) |
| `tests/test_game_state_model.py` | 17 | GameState model (new_game, hands, trump) |

**Total: 58 automated tests**

---

## Test Coverage Mapping

| Acceptance Criteria | Tests |
|---------------------|-------|
| AC #1: Shuffled 52-card deck | test_deck_has_52_cards, test_deck_has_unique_cards, test_shuffle_changes_order |
| AC #2: Each player gets 6 cards | test_new_game_deals_6_cards_to_player1, test_new_game_deals_6_cards_to_player2 |
| AC #3: 40 cards in stock (top visible) | test_new_game_stock_has_40_cards, test_stock_top_card_visible |
| AC #4: Trump suit from top card | test_trump_suit_matches_top_card |
| AC #5: Both hands displayed | Manual visual test |
| AC #6: Player 1 leads first | test_player1_leads_first |

---

## Decisions Made

### 1. Model Naming
Used `CaliforniaJackGame` instead of `GameState` for the model class to avoid confusion with the UI state class `GameState` in `game/states/game_state.py`.

### 2. Seed for Testing
Added tests for deterministic shuffling with seed parameter to enable reproducible tests.

### 3. Card.game_points() Method
Included tests for the scoring system (10=10, A=4, K=3, Q=2, J=1) which will be used in CALJACK-004 but is part of the Card model.

---

## Manual Tests (Deferred)

| Test | Reason |
|------|--------|
| Card visual rendering | Requires pygame display |
| Hand display layout | Requires visual inspection |
| Turn indicator visibility | Requires visual inspection |

---

## Known Limitations

1. **Visual tests not automated**: Cannot automate visual verification
2. **Model naming**: Chose `CaliforniaJackGame` to avoid `GameState` collision

---

## Next Role

Ready for **Developer** to implement production code and make all 58 tests pass.
