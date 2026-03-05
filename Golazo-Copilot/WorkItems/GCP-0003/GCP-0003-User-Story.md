# GCP-0003: DoR/DoD Checklist Management

**Status**: IMPLEMENTED

## User Story

**As a** developer using Golazo Copilot,  
**I want to** mark Definition of Ready and Definition of Done items as complete,  
**So that** I can track progress and unlock workflow gates.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_mark_dor` Updates DoR Items
- [ ] Calling `gcp_mark_dor({ item: "userStory", complete: true })`:
  - Sets `dor.userStory = true` in state
  - Updates `updatedAt` timestamp
  - Saves state to `state.json`
- [ ] Returns current DoR status showing all items

### AC2: MCP Tool `gcp_mark_dod` Updates DoD Items
- [ ] Calling `gcp_mark_dod({ item: "testsPass", complete: true })`:
  - Sets `dod.testsPass = true` in state
  - Updates `updatedAt` timestamp
  - Saves state to `state.json`
- [ ] Returns current DoD status showing all items

### AC3: Bulk Update Support
- [ ] Can mark multiple items at once:
  ```typescript
  gcp_mark_dor({ items: { userStory: true, designDoc: true } })
  ```
- [ ] Partial updates allowed (only specified items changed)

### AC4: Item Validation
- [ ] Invalid item names return error:
  - `"Unknown DoR item: 'userStories'. Valid items: userStory, designDoc, reviewComments, testCases"`
- [ ] Type validation on `complete` (must be boolean)

### AC5: MCP Resource `dor://checklist` Available
- [ ] Returns current DoR status:
  ```json
  {
    "complete": false,
    "items": {
      "userStory": { "complete": true, "markedAt": "2026-01-31T10:30:00Z" },
      "designDoc": { "complete": true, "markedAt": "2026-01-31T11:00:00Z" },
      "reviewComments": { "complete": false, "markedAt": null },
      "testCases": { "complete": false, "markedAt": null }
    },
    "missing": ["reviewComments", "testCases"]
  }
  ```

### AC6: MCP Resource `dod://checklist` Available
- [ ] Returns current DoD status with same structure as DoR

### AC7: Unmarking Items (Rework)
- [ ] Setting `complete: false` unmarks an item:
  - `gcp_mark_dor({ item: "userStory", complete: false })`
  - Clears `markedAt` timestamp
- [ ] Warning returned: "Unmarking userStory. This may affect workflow gates."

### AC8: Gate Status Calculation
- [ ] `is_dor_complete()` returns true only when ALL DoR items are true
- [ ] `is_dod_complete()` returns true only when ALL DoD items are true
- [ ] Gate status included in responses

---

## Technical Notes

### MCP Tool Definitions
```typescript
// gcp_mark_dor
{
  name: "gcp_mark_dor",
  description: "Mark Definition of Ready items as complete or incomplete",
  inputSchema: {
    type: "object",
    properties: {
      item: {
        type: "string",
        enum: ["userStory", "designDoc", "reviewComments", "testCases"],
        description: "Single DoR item to mark"
      },
      items: {
        type: "object",
        description: "Multiple DoR items to mark (alternative to single item)",
        additionalProperties: { type: "boolean" }
      },
      complete: {
        type: "boolean",
        default: true,
        description: "Whether item is complete (used with single item)"
      }
    }
  }
}

// gcp_mark_dod
{
  name: "gcp_mark_dod",
  description: "Mark Definition of Done items as complete or incomplete",
  inputSchema: {
    type: "object",
    properties: {
      item: {
        type: "string",
        enum: ["branchCreated", "testsWrittenFirst", "testsPass", 
               "buildPasses", "docsUpdated", "refactorComplete", "committed"],
        description: "Single DoD item to mark"
      },
      items: {
        type: "object",
        description: "Multiple DoD items to mark",
        additionalProperties: { type: "boolean" }
      },
      complete: {
        type: "boolean",
        default: true,
        description: "Whether item is complete"
      }
    }
  }
}
```

### Enhanced State Schema
```typescript
interface ChecklistItem {
  complete: boolean;
  markedAt: string | null;  // ISO timestamp when marked complete
  markedBy?: string;        // Future: user/role that marked it
}

interface DoRState {
  userStory: ChecklistItem;
  designDoc: ChecklistItem;
  reviewComments: ChecklistItem;
  testCases: ChecklistItem;
}
```

### Response Schema
```typescript
interface ChecklistResponse {
  success: boolean;
  checklist: "dor" | "dod";
  complete: boolean;  // All items done?
  items: Record<string, { complete: boolean; markedAt: string | null }>;
  missing: string[];  // Items still incomplete
  warning?: string;   // If unmarking
}
```

---

## Dependencies

- **GCP-0001**: Requires initialized work item with state.json
- **GCP-0002**: Checklist status affects transition gates

---

## Out of Scope

- Custom DoR/DoD items via gcp.yaml (GCP-0008)
- Automatic DoR detection (e.g., file exists = marked) (Future)

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
