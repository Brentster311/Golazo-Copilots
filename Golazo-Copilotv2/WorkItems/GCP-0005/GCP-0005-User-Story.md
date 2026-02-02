# GCP-0005: Consent and Deviation Recording

## User Story

**As a** developer using Golazo Copilot,  
**I want to** record explicit consent when bypassing workflow gates,  
**So that** deviations are tracked with justification for audit purposes.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_consent` Records Deviation
- [ ] Calling `gcp_consent({ action: "skip_dor", reason: "spike exploration" })`:
  - Appends to `deviations[]` array in state
  - Records: action, reason, current role, timestamp
  - Saves state to `state.json`
- [ ] Returns confirmation with deviation ID

### AC2: Consent Required Before Forced Transition
- [ ] `gcp_transition({ role: "developer", force: true })` fails without prior consent:
  - Error: "Cannot force transition without recorded consent. Call gcp_consent first."
- [ ] After `gcp_consent({ action: "skip_dor" })`, forced transition succeeds

### AC3: Consent Actions Supported
- [ ] Supported deviation actions:
  - `skip_dor` - Bypass Definition of Ready gate
  - `skip_dod` - Bypass Definition of Done gate
  - `skip_role` - Skip a role in the workflow
  - `revert_progress` - Undo completed items
  - `custom` - Custom deviation with description

### AC4: Reason Required
- [ ] Consent without reason fails:
  - Error: "Reason required for deviation. Explain why you're bypassing the gate."
- [ ] Minimum reason length: 10 characters

### AC5: Deviation Audit Trail
- [ ] Each deviation record contains:
  ```json
  {
    "id": "dev-001",
    "action": "skip_dor",
    "reason": "Spike exploration - will create proper artifacts later",
    "role": "architect",
    "timestamp": "2026-01-31T12:55:00Z",
    "context": {
      "missingItems": ["testCases"],
      "targetRole": "developer"
    }
  }
  ```

### AC6: Consent Expiration
- [ ] Consent is single-use:
  - After forced transition, consent is "consumed"
  - Must call `gcp_consent` again for another forced action
- [ ] Consent expires after 5 minutes if not used

### AC7: Deviation Summary in Status
- [ ] `gcp_status()` includes deviation summary:
  ```json
  {
    "deviations": {
      "count": 2,
      "recent": [
        { "action": "skip_dor", "reason": "...", "timestamp": "..." }
      ]
    }
  }
  ```

### AC8: Warning on Multiple Deviations
- [ ] If work item has 3+ deviations, status includes warning:
  - "Warning: Multiple workflow deviations recorded. Consider addressing root causes."

---

## Technical Notes

### MCP Tool Definition
```typescript
{
  name: "gcp_consent",
  description: "Record explicit consent for bypassing a workflow gate with justification",
  inputSchema: {
    type: "object",
    properties: {
      action: {
        type: "string",
        enum: ["skip_dor", "skip_dod", "skip_role", "revert_progress", "custom"],
        description: "Type of workflow deviation"
      },
      reason: {
        type: "string",
        minLength: 10,
        description: "Justification for the deviation (min 10 chars)"
      },
      customAction: {
        type: "string",
        description: "Description if action is 'custom'"
      }
    },
    required: ["action", "reason"]
  }
}
```

### Deviation Schema
```typescript
interface Deviation {
  id: string;                    // Unique ID: "dev-001"
  action: DeviationAction;
  reason: string;
  role: string;                  // Role when deviation recorded
  timestamp: string;             // ISO 8601
  context: {
    missingItems?: string[];     // What was skipped
    targetRole?: string;         // If skip_role
    customAction?: string;       // If action is "custom"
  };
  consumed: boolean;             // Whether deviation was used
  consumedAt?: string;           // When it was used
}

type DeviationAction = "skip_dor" | "skip_dod" | "skip_role" | "revert_progress" | "custom";
```

### Consent Flow
```
User: "Skip the DoR, I'm just exploring"
  |
  +-> Copilot calls gcp_consent({ action: "skip_dor", reason: "exploring spike" })
  |     |
  |     +-> Deviation recorded, consent token issued
  |     +-> Returns: { success: true, consentId: "dev-003", expiresIn: "5m" }
  |
  +-> Copilot calls gcp_transition({ role: "developer", force: true })
  |     |
  |     +-> Checks for valid consent token
  |     +-> Marks consent as consumed
  |     +-> Transition proceeds
  |
  +-> Deviation permanently recorded in audit trail
```

---

## Dependencies

- **GCP-0001**: Requires initialized work item
- **GCP-0002**: Consent enables forced transitions

---

## Out of Scope

- Approval workflows (multi-user consent) (Future)
- Deviation limits/quotas (Future)
- Manager notification on deviations (Future)

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
