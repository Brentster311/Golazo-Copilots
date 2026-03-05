# GCP-0006: Multi-Session Support

**Status**: IMPLEMENTED

## User Story

**As a** developer working on multiple features,  
**I want to** switch between work items without losing progress,  
**So that** I can context-switch efficiently while maintaining separate workflow states.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_switch` Changes Active Work Item
- [ ] Calling `gcp_switch({ workItemId: "feature-b" })`:
  - Loads state from `WorkItems/feature-b/state.json`
  - Sets as active work item for current session
  - Returns status of switched-to work item
- [ ] Previous work item state preserved (not modified)

### AC2: MCP Tool `gcp_list` Shows All Work Items
- [ ] Calling `gcp_list()` returns:
  ```json
  {
    "active": "feature-a",
    "workItems": [
      {
        "id": "feature-a",
        "profile": "complete",
        "currentRole": "developer",
        "phase": "development",
        "dorComplete": true,
        "dodComplete": false,
        "updatedAt": "2026-01-31T14:30:00Z",
        "isActive": true
      },
      {
        "id": "feature-b",
        "profile": "express",
        "currentRole": "architect",
        "phase": "definition",
        "dorComplete": false,
        "dodComplete": false,
        "updatedAt": "2026-01-30T09:15:00Z",
        "isActive": false
      }
    ]
  }
  ```

### AC3: Switch Preserves Context
- [ ] When switching back to a work item:
  - Resumes at exact role and state
  - Role instructions for current role loaded
  - No progress lost

### AC4: Auto-Discovery of Work Items
- [ ] `gcp_list()` scans `WorkItems/*/state.json` to find all work items
- [ ] Works without maintaining separate index file

### AC5: Work Item Not Found Handling
- [ ] `gcp_switch({ workItemId: "nonexistent" })` returns error:
  - "Work item 'nonexistent' not found. Available: feature-a, feature-b"

### AC6: Session State Indicator
- [ ] Status includes active session info:
  ```json
  {
    "session": {
      "activeWorkItem": "feature-a",
      "switchedAt": "2026-01-31T14:00:00Z",
      "otherWorkItems": 2
    }
  }
  ```

### AC7: Recent Work Items Sorting
- [ ] `gcp_list()` returns work items sorted by `updatedAt` (most recent first)
- [ ] Optional filter: `gcp_list({ filter: "active" })` shows only in-progress items

### AC8: Work Item Completion
- [ ] When all DoD items complete and Documenter role finished:
  - Work item can be marked complete: `gcp_complete()`
  - Completed items shown separately in list
  - State preserved but flagged as `completed: true`

---

## Technical Notes

### MCP Tool Definitions
```typescript
// gcp_switch
{
  name: "gcp_switch",
  description: "Switch to a different work item, preserving current state",
  inputSchema: {
    type: "object",
    properties: {
      workItemId: {
        type: "string",
        description: "ID of work item to switch to"
      }
    },
    required: ["workItemId"]
  }
}

// gcp_list
{
  name: "gcp_list",
  description: "List all work items with their current status",
  inputSchema: {
    type: "object",
    properties: {
      filter: {
        type: "string",
        enum: ["all", "active", "completed"],
        default: "all",
        description: "Filter work items by status"
      },
      sort: {
        type: "string",
        enum: ["recent", "name", "phase"],
        default: "recent",
        description: "Sort order for results"
      }
    }
  }
}

// gcp_complete
{
  name: "gcp_complete",
  description: "Mark current work item as completed",
  inputSchema: {
    type: "object",
    properties: {
      summary: {
        type: "string",
        description: "Brief summary of what was accomplished"
      }
    }
  }
}
```

### Session Management
```typescript
interface SessionState {
  activeWorkItemId: string | null;
  switchedAt: string;
}

// Session state stored in memory (per MCP server instance)
// Not persisted - each IDE session starts fresh
// First gcp_status or gcp_init sets active work item
```

### Work Item Discovery
```typescript
async function discoverWorkItems(workItemsDir: string): Promise<WorkItemSummary[]> {
  const dirs = await fs.readdir(workItemsDir);
  const workItems: WorkItemSummary[] = [];
  
  for (const dir of dirs) {
    const statePath = path.join(workItemsDir, dir, "state.json");
    if (await fs.exists(statePath)) {
      const state = await loadState(statePath);
      workItems.push(summarizeWorkItem(dir, state));
    }
  }
  
  return workItems.sort((a, b) => 
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
}
```

---

## Dependencies

- **GCP-0001**: Work items must be initialized with state.json
- **GCP-0004**: Uses status display for switched work item

---

## Out of Scope

- Work item archival/deletion (Future)
- Work item templates (Future)
- Cross-repo work items (Future)

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
