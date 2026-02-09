# GCP-0027 Test Cases

## TC1: Mark tools and dead code are absent (AC 1, 2, 3)

### TC1.1: No gcp_mark references in source
- **Action**: `grep -r "gcp_mark" golazo-copilot/src/`
- **Expected**: Zero matches
- **Failure message**: "Found gcp_mark reference in production source"

### TC1.2: No gcp_mark.py file exists
- **Action**: Check `golazo-copilot/src/golazo_copilot/tools/gcp_mark.py`
- **Expected**: File does not exist
- **Failure message**: "gcp_mark.py still exists"

### TC1.3: No evidence.py file exists
- **Action**: Check `golazo-copilot/src/golazo_copilot/core/evidence.py`
- **Expected**: File does not exist
- **Failure message**: "evidence.py still exists — dead code not cleaned up"

### TC1.4: No test_evidence.py file exists
- **Action**: Check `golazo-copilot/tests/test_evidence.py`
- **Expected**: File does not exist
- **Failure message**: "test_evidence.py still exists"

### TC1.5: Server exports only 5 tools
- **Action**: Check `tools/__init__.py` exports
- **Expected**: Exactly `gcp_create_workitem`, `gcp_transition`, `gcp_status`, `gcp_bootstrap`, `gcp_consent`
- **Failure message**: "Unexpected tool export found"

## TC2: Bootstrap instructions are clean (AC 4)

### TC2.1: No gcp_mark references in bootstrap-instructions.md
- **Action**: `grep "gcp_mark" bootstrap-instructions.md`
- **Expected**: Zero matches
- **Failure message**: "bootstrap-instructions.md still references removed tools"

### TC2.2: No evidence parameter references
- **Action**: `grep "evidence=" bootstrap-instructions.md`
- **Expected**: Zero matches
- **Failure message**: "bootstrap-instructions.md still references evidence= parameter"

### TC2.3: Bootstrap version header matches package
- **Action**: Compare version in bootstrap-instructions.md header with pyproject.toml version
- **Expected**: Versions match
- **Failure message**: "bootstrap-instructions.md version header is stale"

## TC3: Output validation works end-to-end (AC 5)

### TC3.1: gcp_transition still validates required outputs
- **Precondition**: Work item in project-owner-assistant role, user story exists, role notes exist
- **Action**: Call `gcp_transition(role="program-manager")`
- **Expected**: Transition succeeds — output_validator checks required outputs and they exist
- **Failure message**: "Transition failed when required outputs exist"

### TC3.2: gcp_transition blocks when outputs missing
- **Precondition**: Work item in project-owner-assistant role, role notes file missing
- **Action**: Call `gcp_transition(role="program-manager")`
- **Expected**: Transition blocked with message listing missing file
- **Failure message**: "Transition allowed despite missing required outputs"

### TC3.3: gcp_status shows required outputs validation
- **Precondition**: Work item in project-owner-assistant role with some outputs missing
- **Action**: Call `gcp_status()`
- **Expected**: Response includes required outputs section with valid/missing indicators
- **Failure message**: "gcp_status does not show required outputs validation"

### TC3.4: gcp_status next steps include remediation for missing outputs
- **Precondition**: Work item in project-owner-assistant role, role notes file missing
- **Action**: Call `gcp_status()`
- **Expected**: Next Steps include "Create file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md" or similar remediation text
- **Failure message**: "gcp_status next steps do not include remediation for missing outputs"

### TC3.5: gcp_status next steps exclude remediation when all outputs exist
- **Precondition**: Work item with all required outputs present
- **Action**: Call `gcp_status()`
- **Expected**: Next Steps do NOT include "Create file:" remediation lines
- **Failure message**: "gcp_status shows remediation when no outputs are missing"

## TC4: All tests pass (AC 6)

### TC4.1: Full test suite passes
- **Action**: `python -m pytest tests/ -v`
- **Expected**: 121+ tests pass, 0 failures (skips allowed)
- **Failure message**: "Test suite has failures after cleanup"

### TC4.2: No import errors
- **Action**: `python -c "from golazo_copilot.tools import *; from golazo_copilot.core import *"`
- **Expected**: No ImportError
- **Failure message**: "Import error after removing modules"

## TC5: Version bumped (AC 7)

### TC5.1: Version in pyproject.toml is incremented
- **Action**: Check `pyproject.toml` version
- **Expected**: Version > 2.100.8
- **Failure message**: "Version not bumped"
