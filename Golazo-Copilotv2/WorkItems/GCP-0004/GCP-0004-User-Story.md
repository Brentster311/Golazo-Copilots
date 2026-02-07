# GCP-0004: Workflow Status Display

**Status**: IMPLEMENTED

## User Story

**As a** developer using Golazo Copilot,  
**I want to** see my current workflow status at any time,  
**So that** I know where I am in the process and what's needed next.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_status` Returns Full Status
- [ ] Calling `gcp_status()` returns comprehensive workflow state:
  ```json
  {
    "workItemId": "feature-x",
    "profile": "complete",
    "currentPhase": "definition",
    "currentRole": "quality-assurance",
    "dor": {
      "complete": false,
      "items": { "userStory": true, "designDoc": true, "reviewComments": false, "testCases": false },
      "missing": ["reviewComments", "testCases"]
    },
    "dod": {
      "complete": false,
      "items": { "branchCreated": false, "testsWrittenFirst": false, ... },
      "missing": ["branchCreated", "testsWrittenFirst", ...]
    },
    "roleInstructions": "## Quality Assurance Role\n\n...",
    "nextSteps": ["Complete reviewComments", "Complete testCases", "Then transition to architect"]
  }
  ```

### AC2: Status Header Format for Copilot
- [ ] Response includes formatted status header for Copilot to display:
  ```markdown
  **Golazo Status**
  - Work Item: feature-x
  - Current Role: quality-assurance
  - Phase: definition
  - DoR: 2/4 complete (missing: reviewComments, testCases)
  - DoD: 0/7 complete
  ```

### AC3: Role Instructions Included
- [ ] Status always includes current role's instruction markdown
- [ ] Loaded from local override or package default

### AC4: Next Steps Suggestions
- [ ] Intelligent next steps based on current state:
  - In definition phase: "Complete [missing DoR items]"
  - DoR complete: "Ready to transition to developer"
  - In development: "Complete implementation, then mark testsPass"
  - DoD complete: "Ready to complete work item"

### AC5: No Active Work Item Handling
- [ ] If no work item initialized:
  ```json
  {
    "active": false,
    "message": "No active work item. Use gcp_init to start a new work item.",
    "availableWorkItems": ["feature-a", "feature-b"]  // if any exist
  }
  ```

### AC6: MCP Resource `state://current` Synced
- [ ] `state://current` resource returns same data as `gcp_status()`
- [ ] Can be used by Copilot for context without explicit tool call

### AC7: Elapsed Time Tracking
- [ ] Status includes time information:
  ```json
  {
    "timing": {
      "createdAt": "2026-01-31T10:00:00Z",
      "updatedAt": "2026-01-31T14:30:00Z",
      "elapsed": "4h 30m",
      "currentRoleTime": "1h 15m"
    }
  }
  ```

---

## Technical Notes

### MCP Tool Definition
```typescript
{
  name: "gcp_status",
  description: "Get current Golazo Copilot workflow status, role instructions, and next steps",
  inputSchema: {
    type: "object",
    properties: {
      format: {
        type: "string",
        enum: ["full", "brief", "header"],
        default: "full",
        description: "Level of detail in response"
      }
    }
  }
}
```

### Response Formats

**Full** (default): Complete state with instructions and suggestions
**Brief**: Status without role instructions
**Header**: Just the markdown status header for display

### Status Calculation Logic
```typescript
function calculateNextSteps(state: WorkItemState): string[] {
  const steps: string[] = [];
  
  if (state.currentPhase === "definition") {
    const missingDor = getMissingDoR(state);
    if (missingDor.length > 0) {
      steps.push(`Complete DoR items: ${missingDor.join(", ")}`);
    }
    if (missingDor.length === 0 && state.currentRole !== "developer") {
      steps.push(`Ready to transition to ${getNextRole(state.currentRole)}`);
    }
  }
  
  if (state.currentPhase === "development") {
    // Development-specific suggestions
  }
  
  return steps;
}
```

---

## Dependencies

- **GCP-0001**: Requires initialized work item
- **GCP-0002**: Uses transition info for next steps
- **GCP-0003**: Uses DoR/DoD status

---

## Out of Scope

- Historical status (past states) (Future)
- Team/multi-user status (Future)

---

## Definition of Ready Checklist

- [ ] User Story document exists (this file)
- [ ] Design Doc exists
- [ ] Review Comments from QA and Architect exist
- [ ] Test Cases document exists

## Definition of Done Checklist

- [ ] Feature branch created
- [ ] Test code written before production code
- [ ] All automated tests pass
- [ ] Build passes
- [ ] Docs updated
- [ ] Refactor pass complete
- [ ] Changes committed
