# GCP-0052 Refactor Expert Notes

## Modularity Audit

| File | Lines | Functions/Classes | Assessment |
|------|-------|-------------------|------------|
| `tests/test_subagent_integration.py` | 532 | 29 (7 classes, 20 test methods, 2 helpers) | **Over 300-line threshold** — see below |
| `WorkItems/Golazo-Subagent-Handoff-Protocol.md` | 115 | N/A (markdown) | Well under 200-line NFR |

### test_subagent_integration.py (532 lines)

**Decision: Keep as single file.**

Rationale:
- All 20 tests are integration tests for the same feature (subagent handoff flow)
- 7 test classes provide clear logical grouping (workflow walk, missing outputs, backward transitions, protocol validation, zero-bridge, suffix mapping)
- Only 2 shared helper functions (`_wi_dir`, `_create_outputs_for_role`) — minimal coupling
- The `REQUIRED_OUTPUTS` constant (60 lines) accounts for significant line count but provides value as a single reference
- Splitting by test class would create 7 small files with shared constants and fixture — more complexity, not less
- Other test files in the repo follow the same pattern (e.g., `test_gcp_transition.py` at 586 lines)

### No Refactoring Required

- Code is clean and follows existing test patterns
- No duplication detected between tests (each test has unique setup)
- Naming is clear and consistent with the test suite convention
- No code smells or unnecessary complexity

## Test Verification
391 tests passing, 0 behavior changes.
