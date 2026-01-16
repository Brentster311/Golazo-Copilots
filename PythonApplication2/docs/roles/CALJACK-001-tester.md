# Role Decision Document: Tester

**Work Item**: CALJACK-001 - Main Menu and Game Window Foundation  
**Role**: Tester  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] User Story exists at `docs/workitems/CALJACK-001-user-story.md`
- [x] Review Notes exist at `docs/design/CALJACK-001-review-notes.md` (includes Reviewer + Architect notes)

---

## Decisions Made

### 1. Test Coverage
Created 13 test cases covering:
- All 5 acceptance criteria
- Both non-functional requirements
- Edge cases (right-click, keyboard, click outside bounds)
- Error case (invalid state name)

### 2. Test Approach: Hybrid
- **Automated (pytest)**: Unit tests for logic (state transitions, button detection, constants)
- **Manual**: Visual/integration tests requiring display

### 3. Manual Test Justification
Some tests cannot be automated due to:
- Visual verification requirements (is text "readable"?)
- Display dependency for pygame window creation
- System-level interactions (window close)

**Follow-up plan**: Investigate pygame headless mode for CI.

---

## Alternatives Considered

### Test Framework
| Option | Evaluation |
|--------|------------|
| **pytest** | Selected - standard, good mocking support |
| unittest | Rejected - more verbose |
| pygame testing utilities | Rejected - limited, not standard |

### Coverage Strategy
| Option | Evaluation |
|--------|------------|
| Only happy paths | Rejected - insufficient coverage |
| **Happy + edge + error** | Selected - comprehensive |
| Full mutation testing | Rejected - overkill for MVP |

---

## Tradeoffs Accepted

1. **Manual visual tests**: Cannot automate "is button readable" verification
2. **Mocked pygame events**: Unit tests use mocks, may miss pygame-specific edge cases
3. **No screenshot comparison**: Would add complexity for MVP

---

## Known Limitations or Risks

1. **Display-dependent tests**: CI may need pygame headless setup
2. **Mock accuracy**: Mocked pygame events may not perfectly match real events
3. **Manual test subjectivity**: "Readable" is subjective

---

## Test Case to Acceptance Criteria Mapping

| AC | Description | Test Cases |
|----|-------------|------------|
| AC #1 | Window 1024x768 | TC-001, TC-002 |
| AC #2 | New Game button | TC-003 |
| AC #3 | Help button | TC-004 |
| AC #4 | New Game transition | TC-005, TC-006, TC-008 |
| AC #5 | Help transition | TC-007 |
| NFR-001 | Close button | TC-009 |
| NFR-002 | 100ms response | TC-010 |

Edge cases: TC-011, TC-012  
Error cases: TC-013

---

## Validation

- [x] Every acceptance criterion has at least one test
- [x] Edge cases identified and covered
- [x] Error cases identified and covered
- [x] Test code provided where automatable
- [x] Manual test steps documented
- [x] Test Cases created at `docs/tests/CALJACK-001-test-cases.md`

---

## Next Role

Ready for **Developer** to implement production code and tests.
