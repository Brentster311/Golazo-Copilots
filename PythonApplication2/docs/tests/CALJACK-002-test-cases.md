# Test Cases: CALJACK-002

**Work Item**: CALJACK-002 - Card Dealing and Initial Game Setup  
**Tester**: Golazo Tester Role  
**Date**: 2025-01-XX

---

## Test Coverage Summary

| Acceptance Criteria | Test File | Test Functions |
|---------------------|-----------|----------------|
| AC #1: Shuffled 52-card deck | test_deck.py | test_deck_has_52_cards, test_deck_has_unique_cards, test_shuffle_changes_order |
| AC #2: Each player gets 6 cards | test_game_state.py | test_new_game_deals_6_cards_each |
| AC #3: 40 cards in stock (top visible) | test_game_state.py | test_new_game_stock_has_40_cards, test_stock_top_card_visible |
| AC #4: Trump suit from top card | test_game_state.py | test_trump_suit_matches_top_card |
| AC #5: Both hands displayed | test_card_renderer.py | (manual - visual) |
| AC #6: Player 1 leads first | test_game_state.py | test_player1_leads_first |

---

## Automated Test Files Created

1. `PythonApplication2/tests/test_card.py` - Card model tests
2. `PythonApplication2/tests/test_deck.py` - Deck model tests
3. `PythonApplication2/tests/test_game_state_model.py` - GameState model tests

---

## Manual Tests (Visual)

| Test ID | Description | AC |
|---------|-------------|----|
| MT-001 | Cards visually distinguishable by suit/rank | AC #5 |
| MT-002 | Player hands displayed correctly | AC #5 |
| MT-003 | Stock pile shows top card | AC #3 |
| MT-004 | Turn indicator visible | AC #6 |

---

## Test Execution Commands

```bash
cd PythonApplication2/PythonApplication2
python -m pytest tests/test_card.py tests/test_deck.py tests/test_game_state_model.py -v
```

Expected: **ALL TESTS FAIL** (production code not yet written)
