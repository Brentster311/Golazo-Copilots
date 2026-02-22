# GCP-0046: Developer Decision Notes

## Implementation Summary

Added the **domain-expert** role to the Golazo Copilot workflow, positioned between program-manager and quality-assurance in the definition phase.

## TDD Approach

### Red Phase — 16 New Tests Written First
Created `golazo-copilot/tests/test_domain_expert.py` with 16 tests across 4 classes:

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestDomainExpertTransitions` | 6 | Forward/backward transitions, adjacency, skip rejection |
| `TestDomainExpertMetadata` | 5 | Phase mapping, VALID_ROLES, ROLE_ORDER position/count |
| `TestDomainExpertBackwardDetection` | 2 | Backward detection for DE→PM and QA→DE |
| `TestDomainExpertRoleFiles` | 3 | Role file existence in 3 locations |

Initial run: 11 failed, 5 passed (red phase confirmed).

### Green Phase — Production Code
1. **`golazo-copilot/src/golazo_copilot/core/transitions.py`** — Single source of truth:
   - Added `"domain-expert"` to `TRANSITIONS` with forward→quality-assurance, backward→program-manager
   - Updated program-manager forward to point to domain-expert (was quality-assurance)
   - Updated quality-assurance backward to point to domain-expert (was program-manager)
   - Added to `PHASE_MAP` as "definition"
   - Inserted at index 2 in `ROLE_ORDER`

2. **`golazo-copilot/src/golazo_copilot/roles/defaults/domain-expert.md`** — New role file with:
   - 4-step identification process (extract claims → categorize → evaluate triggers → decide)
   - 4 trigger categories (Engineering & AI, Azure Platform, Application & Solution, Integration & Architecture)
   - Consultation rules (mandatory, optional, skip criteria)
   - Required outputs: decision notes + optional consultation log

3. **Deployed copies** of domain-expert.md to:
   - `.github/roles/domain-expert.md`
   - `golazo-copilot/.github/roles/domain-expert.md`

4. **Updated role lists** (9→10 roles) in:
   - `.github/copilot-instructions.md`
   - `golazo-copilot/.github/copilot-instructions.md`
   - `golazo-copilot/src/golazo_copilot/bootstrap-instructions.md`

### Regression Fix Phase
Adding domain-expert broke 10 existing tests (PM→QA no longer a valid direct forward transition). Fixed across 3 files:
- `test_gcp012_backward.py` — ALL_ROLES, 3 test transition sequences, 1 role_history count
- `test_gcp_status.py` — ALL_ROLES, roles_total 9→10, role count assertion 9→10
- `test_gcp_transition.py` — ALL_ROLES, advance_to_role helper, 5 test methods updated

## Final Test Results
**252 passed, 6 skipped, 0 failed** (was 236 passed before GCP-0046).

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single insertion point in transitions.py | All role ordering derives from TRANSITIONS + ROLE_ORDER; no scattered role lists in production code |
| Role file in defaults/ not just .github/ | Editable install tests validate source paths; deployed copies serve workspace usage |
| Renamed `test_valid_transition_program_manager_to_qa` → `test_valid_transition_program_manager_to_domain_expert` | Accurately describes the new valid forward transition |
| No changes to persistence.py or server.py | domain-expert is data-driven via transitions.py; no new tool logic needed |

## Files Changed
- `golazo-copilot/src/golazo_copilot/core/transitions.py` (modified)
- `golazo-copilot/src/golazo_copilot/roles/defaults/domain-expert.md` (created)
- `.github/roles/domain-expert.md` (created)
- `golazo-copilot/.github/roles/domain-expert.md` (created)
- `.github/copilot-instructions.md` (modified)
- `golazo-copilot/.github/copilot-instructions.md` (modified)
- `golazo-copilot/src/golazo_copilot/bootstrap-instructions.md` (modified)
- `golazo-copilot/tests/test_domain_expert.py` (created)
- `golazo-copilot/tests/test_gcp012_backward.py` (modified)
- `golazo-copilot/tests/test_gcp_status.py` (modified)
- `golazo-copilot/tests/test_gcp_transition.py` (modified)
