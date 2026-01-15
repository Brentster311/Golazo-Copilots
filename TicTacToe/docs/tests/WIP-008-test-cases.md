# Test Cases: WIP-008 - AI Fork Detection and Blocking

**Work Item**: WIP-008  
**Author**: Tester  
**Date**: 2026-01-14

---

## Test Strategy

Test the new `_find_fork_block()` method and verify AI behavior against fork strategies.

---

## Test Cases

### Unit Tests for `_find_fork_block()`

#### TC-401: Detect Diagonal Fork Setup (Corner-Center-Corner)

**Description**: AI detects fork when X has opposite corners (0,0) and (2,2).

**Setup**:
```
X | . | .
---------
. | O | .
---------
. | . | X
```

**Expected**: `_find_fork_block("X")` returns a corner that blocks the fork: (0,2) or (2,0).

---

#### TC-402: Detect Anti-Diagonal Fork Setup

**Description**: AI detects fork when X has corners (0,2) and (2,0).

**Setup**:
```
. | . | X
---------
. | O | .
---------
X | . | .
```

**Expected**: `_find_fork_block("X")` returns (0,0) or (2,2).

---

#### TC-403: No Fork When Single Corner

**Description**: No fork exists with only one corner occupied.

**Setup**:
```
X | . | .
---------
. | O | .
---------
. | . | .
```

**Expected**: `_find_fork_block("X")` returns `None`.

---

#### TC-404: Detect Edge-Corner Fork

**Description**: AI detects fork from edge + corner combination.

**Setup**:
```
X | . | .
---------
. | O | .
---------
. | X | .
```

**Expected**: `_find_fork_block("X")` returns (2,0) to block the fork.

---

#### TC-405: No Fork When Lines Blocked

**Description**: No fork if potential lines are blocked.

**Setup**:
```
X | O | .
---------
. | O | .
---------
. | . | X
```

**Expected**: `_find_fork_block("X")` returns `None` (diagonal blocked by O at center).

---

### Integration Tests for AI Behavior

#### TC-406: AI Blocks Diagonal Fork in Game

**Description**: Full game simulation where AI blocks the classic corner fork.

**Moves**:
1. X plays (0,0)
2. AI plays (1,1) - center
3. X plays (2,2)
4. AI should NOT play (0,2) or (2,1) - must block fork

**Expected**: AI plays (0,1), (1,0), (1,2), or (2,1) to force X to respond defensively instead of taking any corner.

---

#### TC-407: AI Wins or Draws Against Fork Strategy

**Description**: AI should never lose when fork strategy is attempted.

**Scenario**: Play multiple games with X using corner-fork strategy.

**Expected**: AI achieves draw or win in all cases.

---

#### TC-408: Fork Block Priority Below Immediate Win

**Description**: AI still takes winning move over blocking fork.

**Setup**:
```
O | O | .
---------
X | . | .
---------
X | . | .
```

**Expected**: AI plays (0,2) to win, not a fork block move.

---

#### TC-409: Fork Block Priority Below Immediate Block

**Description**: AI still blocks opponent's winning move over fork.

**Setup**:
```
X | X | .
---------
. | O | .
---------
. | . | X
```

**Expected**: AI plays (0,2) to block X's win.

---

### Regression Tests

#### TC-410: Existing AI Tests Pass

**Description**: All existing TC-201 through TC-219 tests must pass.

**Expected**: No regressions.

---

## Acceptance Criteria Mapping

| Acceptance Criteria | Test Cases |
|---------------------|------------|
| AI detects fork setup | TC-401, TC-402, TC-404 |
| AI blocks fork | TC-406 |
| AI doesn't lose to fork strategy | TC-407 |
| Existing tests pass | TC-410 |
| New tests cover fork detection | TC-401 through TC-409 |
