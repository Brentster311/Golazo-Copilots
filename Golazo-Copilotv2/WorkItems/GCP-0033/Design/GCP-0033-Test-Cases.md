# GCP-0033 Test Cases

## TC1: Role progress computation

### TC1.1: Fresh work item shows 0 completed, PO in-progress
- **Action**: Create work item, get status
- **Expected**: `roles_completed` = 0, current role in-progress, rest pending
- **Failure**: "Fresh work item has wrong progress counts"

### TC1.2: After transitions shows correct completed count
- **Action**: Create work item, transition through 3 roles, get status
- **Expected**: `roles_completed` matches exited roles count
- **Failure**: "Progress count doesn't match transitions"

### TC1.3: Role progress list has correct statuses
- **Action**: Create work item, transition to PM, get status
- **Expected**: PO = completed, PM = in-progress, rest = pending
- **Failure**: "Individual role statuses incorrect"

## TC2: Server rendering

### TC2.1: Summary line rendered in output
- **Action**: Get formatted status
- **Expected**: Contains "Role Progress:" with "X/9" format
- **Failure**: "Role progress not rendered in status"
