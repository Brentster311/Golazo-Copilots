# Role Decision Document: Project Owner Assistant

**Work Item**: CALJACK-001 through CALJACK-006 (California Jack Card Game)  
**Role**: Project Owner Assistant  
**Date**: 2025-01-XX

---

## Decomposition Rationale

The original request was **too large** because it contained multiple user-observable outcomes:
1. Main menu / window launch
2. Card dealing and game setup
3. Trick-taking gameplay
4. Scoring system
5. Win condition / game over
6. Help screen

Per role instructions: *"A request is too large if it contains more than one user-observable outcome"* and *"Acceptance Criteria must be 3–7 items maximum."*

The original monolithic story had **26+ acceptance criteria**, far exceeding the 7-item limit.

---

## Decisions Made

### 1. Decomposition into 6 Vertical Slices

| ID | Title | Outcome | AC Count |
|----|-------|---------|----------|
| CALJACK-001 | Main Menu and Game Window Foundation | Launch game, see menu | 5 |
| CALJACK-002 | Card Dealing and Initial Game Setup | Start game with dealt cards | 6 |
| CALJACK-003 | Trick-Taking Gameplay and Card Drawing | Play tricks, draw cards | 6 |
| CALJACK-004 | Hand Scoring (High, Low, Jack, Game) | Earn points after hand | 6 |
| CALJACK-005 | Win Condition and Game Over | Game ends, winner declared | 6 |
| CALJACK-006 | Help Screen with Rules and Attribution | View rules and credit | 5 |

### 2. Dependency Chain
```
CALJACK-001 (foundation)
    ??? CALJACK-002 (deal/setup)
    ?       ??? CALJACK-003 (gameplay)
    ?               ??? CALJACK-004 (scoring)
    ?                       ??? CALJACK-005 (win condition)
    ??? CALJACK-006 (help screen)
```

### 3. Each Story is Independently Testable
- CALJACK-001: Can test menu renders and buttons respond
- CALJACK-002: Can test cards dealt correctly with mock/stub gameplay
- CALJACK-003: Can test trick resolution logic independently
- CALJACK-004: Can test scoring calculation with known hands
- CALJACK-005: Can test win detection with preset scores
- CALJACK-006: Can test help screen renders with content

---

## Alternatives Considered

### Decomposition Strategy
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Single large story | Simple tracking | 26+ ACs, untestable in isolation | Rejected |
| **Vertical slices by feature** | Each independently testable, 3-7 ACs | More stories to track | **Selected** |
| Horizontal slices (UI/logic/data) | Clean separation | Can't demo partial features | Rejected |

### Slice Granularity
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| 3 stories (setup/play/end) | Fewer items | Still 10+ ACs each | Rejected |
| **6 stories** | Right-sized ACs (5-6 each) | More dependencies | **Selected** |
| 10+ micro-stories | Very small scope | Over-fragmented | Rejected |

---

## Tradeoffs Accepted

1. **Sequential dependencies**: Stories must be implemented in order (001?002?003?004?005). Accepted because this matches natural game flow.

2. **Help screen independent**: CALJACK-006 can be done in parallel with gameplay stories after CALJACK-001.

3. **Hot-seat visibility**: Players can see each other's cards during turn transitions. Accepted for simplicity.

---

## Known Limitations or Risks

1. **Dependency chain**: A bug in CALJACK-002 blocks CALJACK-003+
2. **Integration risk**: Stories tested independently may have integration issues
3. **Card rendering**: No image assets; programmatic rendering may be time-consuming

---

## Required Outputs Checklist

- [x] Decomposition rationale provided
- [x] `docs/workitems/CALJACK-001-user-story.md`
- [x] `docs/workitems/CALJACK-002-user-story.md`
- [x] `docs/workitems/CALJACK-003-user-story.md`
- [x] `docs/workitems/CALJACK-004-user-story.md`
- [x] `docs/workitems/CALJACK-005-user-story.md`
- [x] `docs/workitems/CALJACK-006-user-story.md`
- [x] `docs/roles/CALJACK-001-project-owner-assistant.md` (this file)

---

## Next Role

Ready for **Program Manager** to create Design Review documents for each story, starting with CALJACK-001.
