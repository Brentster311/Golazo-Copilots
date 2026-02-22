# GCP-0046 Test Cases

## Test Suite: Domain Expert Transitions

### TC-1: Forward transition PM → domain-expert succeeds
- **Setup:** Work item at `program-manager`
- **Action:** `validate_transition("program-manager", "domain-expert")`
- **Expected:** `(True, None)`

### TC-2: Forward transition domain-expert → quality-assurance succeeds
- **Setup:** Work item at `domain-expert`
- **Action:** `validate_transition("domain-expert", "quality-assurance")`
- **Expected:** `(True, None)`

### TC-3: Backward transition domain-expert → program-manager succeeds
- **Setup:** Work item at `domain-expert`
- **Action:** `validate_transition("domain-expert", "program-manager")`
- **Expected:** `(True, None)`

### TC-4: Backward transition quality-assurance → domain-expert succeeds
- **Setup:** Work item at `quality-assurance`
- **Action:** `validate_transition("quality-assurance", "domain-expert")`
- **Expected:** `(True, None)`

### TC-5: Skip prevention — PM cannot skip domain-expert to reach QA
- **Setup:** Work item at `program-manager`
- **Action:** `validate_transition("program-manager", "quality-assurance")`
- **Expected:** `(False, "Cannot transition from 'program-manager' to 'quality-assurance'. Allowed: domain-expert, project-owner-assistant")`

### TC-6: domain-expert cannot skip QA to reach architect
- **Setup:** Work item at `domain-expert`
- **Action:** `validate_transition("domain-expert", "architect")`
- **Expected:** `(False, "Cannot transition from 'domain-expert' to 'architect'. Allowed: quality-assurance, program-manager")`

### TC-7: Phase mapping for domain-expert
- **Action:** `get_phase_for_role("domain-expert")`
- **Expected:** `"definition"`

### TC-8: ROLE_ORDER contains domain-expert at correct position
- **Action:** Check `ROLE_ORDER.index("domain-expert")`
- **Expected:** `2` (after `program-manager` at 1, before `quality-assurance` at 3)

### TC-9: domain-expert is in VALID_ROLES
- **Action:** Check `"domain-expert" in VALID_ROLES`
- **Expected:** `True`

### TC-10: Self-transition domain-expert → domain-expert succeeds
- **Action:** `validate_transition("domain-expert", "domain-expert")`
- **Expected:** `(True, None)`

### TC-11: is_backward_transition correctly identifies domain-expert → PM as backward
- **Action:** `is_backward_transition("domain-expert", "program-manager")`
- **Expected:** `True`

### TC-12: is_backward_transition correctly identifies PM → domain-expert as NOT backward
- **Action:** `is_backward_transition("program-manager", "domain-expert")`
- **Expected:** `False`

## Test Suite: Role File Existence

### TC-13: domain-expert.md exists in source defaults
- **Action:** Check file exists at `golazo-copilot/src/golazo_copilot/roles/defaults/domain-expert.md`
- **Expected:** File exists and contains `# Role: Domain Expert`

### TC-14: domain-expert.md exists in .github/roles/
- **Action:** Check file exists at `.github/roles/domain-expert.md`
- **Expected:** File exists and contains `# Role: Domain Expert`

### TC-15: domain-expert.md exists in golazo-copilot/.github/roles/
- **Action:** Check file exists at `golazo-copilot/.github/roles/domain-expert.md`
- **Expected:** File exists and contains `# Role: Domain Expert`

## Test Suite: Existing Test Regression

### TC-16: All existing transition tests still pass
- **Action:** Run `pytest golazo-copilot/tests/`
- **Expected:** All tests pass (some may need index updates for the new role)

### TC-17: ROLE_ORDER has exactly 10 entries
- **Action:** `len(ROLE_ORDER)`
- **Expected:** `10`
