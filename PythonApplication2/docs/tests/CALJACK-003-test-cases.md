# Test Cases: CALJACK-003

**Work Item**: CALJACK-003 - Trick-Taking Gameplay and Card Drawing  
**Tester**: Golazo Tester Role  
**Date**: 2025-01-XX

---

## Test Coverage Summary

| Acceptance Criteria | Test File | Test Functions |
|---------------------|-----------|----------------|
| AC #1: Click card to play | Manual | Visual verification |
| AC #2: Invalid plays rejected | test_trick.py | test_must_follow_suit_*, test_must_trump_* |
| AC #3: Trick winner determined | test_trick.py | test_winner_* |
| AC #4: Winner/loser draw cards | test_trick.py | test_draw_cards_* |
| AC #5: Winner leads next | test_trick.py | test_winner_leads_next |
| AC #6: Game ends when all played | test_trick.py | test_game_over_* |

---

## Automated Test Files Created

1. `PythonApplication2/tests/test_trick.py` - Trick model and game logic tests

---

## Manual Tests (Visual - Requires Project Owner)

| Test ID | Description | AC |
|---------|-------------|----|
| MT-001 | Click card in hand to play it | AC #1 |
| MT-002 | Invalid play shows visual feedback | AC #2 |
| MT-003 | Played cards appear in play area | AC #1 |
| MT-004 | Turn indicator updates correctly | AC #5 |

---

## Test Execution Commands

```bash
cd PythonApplication2/PythonApplication2
python -m pytest tests/test_trick.py -v
```

Expected: **ALL TESTS FAIL** (production code not yet written)
