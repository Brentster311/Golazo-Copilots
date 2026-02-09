# GCP-0031: Developer Notes

## Summary
Implemented complete removal of DoR/DoD checklist system per design doc.

## TDD Approach
1. **Red Phase**: Added 3 new tests:
   - `test_state_has_no_dor_field` — verifies new state has no dor field
   - `test_state_has_no_dod_field` — verifies new state has no dod field
   - `test_old_state_with_dor_dod_loads` — verifies backward compat via `extra="ignore"`
2. **Also renamed** `skip_dor` → `skip_outputs` in `test_output_integration.py` (red: consent action rejected)
3. **Green Phase**: Implemented all 10 steps from design doc

## Changes Made

| File | Change |
|------|--------|
| `core/checklists.py` | **Deleted** — entire module removed |
| `core/types.py` | Removed `ChecklistItem` class, `dor`/`dod` fields, migration validator. Added `model_config = ConfigDict(extra="ignore")` |
| `core/state.py` | Removed `dor` and `dod` initialization from `create_initial_state()` |
| `core/transitions.py` | Removed `check_dor_gate()`, `DOR_GATE_ROLE`, `TYPE_CHECKING`+`ChecklistItem` import |
| `tools/gcp_consent.py` | Renamed `skip_dor` → `skip_outputs`, removed `skip_dod` |
| `tools/gcp_transition.py` | Removed DoR gate block (L101-120), removed `check_dor_gate`/`DOR_GATE_ROLE` imports, renamed `skip_dor` → `skip_outputs` in output validation |
| `tools/gcp_status.py` | Removed checklists import, DoR/DoD computation, simplified `_generate_next_steps(state, required_outputs)` |
| `server.py` | Removed DoR/DoD count/rendering, updated consent enum, updated gcp_status description |
| `test_gcp_create_workitem.py` | Replaced dor/dod tests with no-dor/no-dod tests, added backward compat test |
| `test_gcp_transition.py` | Deleted `TestDoRGate` class, removed `mark_all_dor_complete` helper, fixed phase/backward tests |
| `test_gcp_status.py` | Deleted `TestStatusDoRDoD` class, renamed `skip_dor` → `skip_outputs` |
| `test_gcp_consent.py` | Renamed all `skip_dor` → `skip_outputs`, rewrote force tests to use output validation |
| `test_gcp012_backward.py` | Removed `mark_all_dor_complete` helper and all calls |
| `test_output_integration.py` | Renamed `skip_dor` → `skip_outputs` in consent test |
| `__init__.py` | Version bump 2.100.9 → 2.100.10 |
| `bootstrap-instructions.md` | Version header 2.100.8 → 2.100.10 |

## Design Decisions
- Used `extra="ignore"` in Pydantic `model_config` for backward compat (old state files with dor/dod load silently)
- Simplified `_generate_next_steps` to only take `(state, required_outputs)` — no more DoR/DoD logic
- Rewrote consent force tests to use output validation (the replacement gate) instead of dead DoR gate

## Test Results
- 120 passed, 6 skipped, 0 failures
- Net test change: 126 → 120 (removed 9 DoR/DoD tests, added 3 new tests)
