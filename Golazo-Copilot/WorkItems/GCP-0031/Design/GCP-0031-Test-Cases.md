# GCP-0031 Test Cases

## TC1: State schema (AC 1, 6)

### TC1.1: New work item has no dor/dod fields
- **Action**: Create work item, load state.json
- **Expected**: No "dor" or "dod" keys in state
- **Failure**: "New state still contains dor/dod"

### TC1.2: Old state file with dor/dod loads without error
- **Action**: Load a state.json that contains dor/dod fields
- **Expected**: Load succeeds, dor/dod fields silently ignored
- **Failure**: "Loading old state with dor/dod raises error"

## TC2: Status output (AC 2)

### TC2.1: Status has no DoR/DoD lines
- **Action**: Call gcp_status
- **Expected**: No "DoR:" or "DoD:" in formatted output
- **Failure**: "Status still shows DoR/DoD"

### TC2.2: Status still shows required outputs
- **Action**: Call gcp_status with role that has required outputs
- **Expected**: Required outputs section present
- **Failure**: "Required outputs lost during cleanup"

## TC3: Transition gate (AC 3, 4)

### TC3.1: Developer transition works without DoR gate
- **Action**: Transition to developer role (all prior roles have outputs)
- **Expected**: Transition succeeds based on output validation only
- **Failure**: "Developer transition still blocked by DoR gate"

### TC3.2: check_dor_gate is gone
- **Action**: grep source for check_dor_gate
- **Expected**: Zero matches
- **Failure**: "check_dor_gate still exists"

## TC4: Dead code (AC 5)

### TC4.1: checklists.py is deleted
- **Action**: Check file exists
- **Expected**: File does not exist
- **Failure**: "checklists.py still exists"

### TC4.2: No checklists imports in source
- **Action**: grep source for "from.*checklists import"
- **Expected**: Zero matches
- **Failure**: "checklists still imported"

## TC5: Consent actions (FR6)

### TC5.1: skip_outputs action works
- **Action**: Call gcp_consent with action="skip_outputs"
- **Expected**: Consent recorded successfully
- **Failure**: "skip_outputs action not recognized"

### TC5.2: skip_dor action rejected
- **Action**: Call gcp_consent with action="skip_dor"
- **Expected**: Action rejected as invalid
- **Failure**: "skip_dor action still accepted"

### TC5.3: skip_dod action rejected
- **Action**: Call gcp_consent with action="skip_dod"
- **Expected**: Action rejected as invalid
- **Failure**: "skip_dod action still accepted"

## TC6: Regression (AC 7)

### TC6.1: Full test suite passes
- **Action**: pytest tests/ -v
- **Expected**: All tests pass (count may differ due to removed DoR/DoD tests)
- **Failure**: "Test failures after cleanup"
