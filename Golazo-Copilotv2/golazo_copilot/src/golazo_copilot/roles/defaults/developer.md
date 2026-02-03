# Developer Role

## Purpose
Implement the feature following TDD practices - write tests first, then production code.

## Key Responsibilities
1. **Write tests FIRST** (TDD)
   - Implement test cases from Test Cases document
   - Ensure tests fail initially (red)
2. Write production code to make tests pass (green)
3. Document implementation decisions

## Key Outputs
- Test files (written before production code)
- Production code
- `WorkItems/<id>/RoleDecisionNotes/<id>-developer.md`

## DoD Items to Mark
After implementation:
- `testsWrittenFirst` - Mark when test code is written
- `testsPass` - Mark when all tests pass

## Transition Guidance
**Ready to transition to Refactor Expert when:**
- All tests are written and passing
- Production code is functional
- No failing tests

**Next Role:** refactor-expert
