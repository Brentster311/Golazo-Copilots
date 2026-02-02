# GCP-0001: Initialize Work Item

## User Story

**As a** developer using GitHub Copilot with Golazo Copilot installed,  
**I want to** initialize a new work item by saying "Start [work-item-id]",  
**So that** I can begin a tracked workflow session with persistent state.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_init` Creates Work Item
- [ ] Calling `gcp_init({ workItemId: "feature-x", profile: "complete" })` creates:
  - `WorkItems/feature-x/state.json` with initial state
- [ ] Initial state includes:
  - `schemaVersion: "1.0"`
  - `workItemId: "feature-x"`
  - `profile: "complete"`
  - `currentPhase: "definition"`
  - `currentRole: "project-owner"`
  - `createdAt: <ISO timestamp>`
  - `updatedAt: <ISO timestamp>`
  - `dor: { userStory: false, designDoc: false, reviewComments: false, testCases: false }`
  - `dod: { branchCreated: false, testsWrittenFirst: false, testsPass: false, buildPasses: false, docsUpdated: false, refactorComplete: false, committed: false }`
  - `roleHistory: [{ role: "project-owner", enteredAt: <timestamp>, exitedAt: null }]`
  - `deviations: []`

### AC2: MCP Returns Current Role Instructions
- [ ] After `gcp_init`, the MCP response includes:
  - Success confirmation
  - Current role: "project-owner"
  - Role instructions (markdown content for project-owner role)
- [ ] Role instructions served from:
  1. Local `.github/roles/project-owner.md` if exists
  2. Otherwise, default from `golazo-copilot` package

### AC3: Default Role Files Included in Package
- [ ] Package includes default role instruction files:
  - `roles/project-owner.md`
  - `roles/program-manager.md`
  - `roles/quality-assurance.md`
  - `roles/architect.md`
  - `roles/developer.md`
  - `roles/refactor-expert.md`
  - `roles/builder.md`
  - `roles/documentor.md`
- [ ] Each role file contains:
  - Role purpose/responsibilities
  - Key outputs expected
  - Transition guidance (when to move to next role)

### AC4: MCP Resource `state://current` Available
- [ ] After initialization, `state://current` resource returns current state JSON
- [ ] If no work item initialized, returns error: "No active work item. Use gcp_init first."

### AC5: Idempotency & Error Handling
- [ ] If `WorkItems/feature-x/` already exists:
  - Return error: "Work item 'feature-x' already exists. Use gcp_switch to resume."
- [ ] If `workItemId` contains invalid characters (spaces, `/`, `\`, etc.):
  - Return error: "Invalid work item ID. Use alphanumeric, hyphens, underscores only."

### AC6: Minimal Bootstrap Instructions Work
- [ ] A repo with only this in `.github/copilot-instructions.md` can use Golazo Copilot:
```markdown
# Golazo Copilot

This repository uses Golazo Copilot for workflow management.

## Setup
Ensure the `golazo-copilot` MCP server is installed and running.

## Usage
- Call `gcp_status` at the start of each response to check workflow state
- Follow the role instructions provided by the MCP server
- Use `gcp_init`, `gcp_transition`, and other tools for workflow operations

## Troubleshooting
If MCP tools are not available:
1. Check that Python 3.10+ is installed
2. Run: `pip install golazo-copilot`
3. Restart your IDE
4. Verify MCP server is configured in your IDE settings
```

---

## Technical Notes

### Package Structure (Python/pip)
```
golazo_copilot/
??? pyproject.toml
??? src/
?   ??? golazo_copilot/
?       ??? __init__.py
?       ??? server.py         # MCP server entry point
?       ??? core/
?       ?   ??? __init__.py
?       ?   ??? types.py      # Pydantic models
?       ?   ??? state.py      # State creation/validation
?       ?   ??? persistence.py # JSON file read/write
?       ??? tools/
?       ?   ??? __init__.py
?       ?   ??? gcp_init.py   # gcp_init tool
?       ??? roles/
?           ??? __init__.py
?           ??? loader.py     # Role instruction loading
?           ??? defaults/
?               ??? project-owner.md
?               ??? program-manager.md
?               ??? quality-assurance.md
?               ??? architect.md
?               ??? developer.md
?               ??? refactor-expert.md
?               ??? builder.md
?               ??? documentor.md
??? tests/
    ??? __init__.py
    ??? test_gcp_init.py
```

### MCP Tool Definition
```python
@server.tool()
async def gcp_init(work_item_id: str, profile: str = "complete") -> dict:
    """Initialize a new Golazo Copilot work item with persistent state tracking.
    
    Args:
        work_item_id: Unique identifier (alphanumeric, hyphens, underscores)
        profile: Workflow profile - "complete", "express", or "spike"
    
    Returns:
        dict with success status, current role, and role instructions
    """
```

### State Schema (v1.0)
```python
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class RoleHistoryEntry(BaseModel):
    role: str
    entered_at: datetime
    exited_at: datetime | None = None

class Deviation(BaseModel):
    action: str
    reason: str
    role: str
    timestamp: datetime

class WorkItemState(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    work_item_id: str
    profile: Literal["complete", "express", "spike"]
    current_phase: Literal["definition", "development", "completion"]
    current_role: str
    created_at: datetime
    updated_at: datetime
    dor: dict[str, bool]
    dod: dict[str, bool]
    role_history: list[RoleHistoryEntry]
    deviations: list[Deviation]
```

---

## Out of Scope (Future Work Items)

- `gcp_transition` - Role transitions (GCP-0002)
- `gcp_mark_dor` / `gcp_mark_dod` - Checklist updates (GCP-0003)
- `gcp_status` - Full status with DoR/DoD display (GCP-0004)
- `gcp_consent` - Deviation recording (GCP-0005)
- `gcp_switch` - Multi-session support (GCP-0006)
- CLI commands (`gcp init`, etc.) (GCP-0007)
- Workflow profiles logic (GCP-0008)

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
