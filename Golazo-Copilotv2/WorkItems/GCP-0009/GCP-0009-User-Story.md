# GCP-0009: Create Role Decision Notes Tool

## Status: ?? SKIPPED

**Reason:** Role decision notes are already being created by Copilot following the role instructions. A dedicated MCP tool is not needed.

---

## Original User Story

**As a** developer using Golazo Copilot,  
**I want to** automatically create role decision notes files,  
**So that** each role's decisions are properly documented and persisted.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_create_role_notes` Creates File
- [ ] Calling `gcp_create_role_notes({ role: "program-manager", content: "..." })`:
  - Creates `WorkItems/<id>/RoleDecisionNotes/<id>-program-manager.md`
  - Creates `RoleDecisionNotes` folder if not exists
  - Updates `updatedAt` timestamp in state
- [ ] Returns success with file path

### AC2: Content Structure
- [ ] If no content provided, generates template:
  ```markdown
  # <id>: <role> Decision Notes

  ## Role Entry
  - **Work Item**: <id>
  - **Prior Role**: <previous-role>
  - **Entry Condition Met**: <reason>

  ---

  ## Decisions Made

  ### D1: <decision-title>
  **Decision**: <what was decided>
  **Rationale**: <why>

  ---

  ## Output Artifacts Created
  - [ ] <list artifacts>

  ---

  ## Transition Recommendation
  **Ready for**: <next-role>
  ```

### AC3: Role Validation
- [ ] Only valid role names accepted
- [ ] Error if invalid role: "Unknown role 'xyz'. Valid: project-owner, program-manager, ..."

### AC4: Idempotency
- [ ] If file exists, option to:
  - Append (default): Add new section with timestamp
  - Replace: Overwrite with new content
- [ ] Parameter: `mode: "append" | "replace"`

### AC5: Integration with Transition
- [ ] `gcp_transition` can optionally require role notes exist before transitioning
- [ ] Warning if transitioning without role notes: "No role notes created for current role"

### AC6: Automatic Metadata
- [ ] Includes metadata in file:
  - Created timestamp
  - Work item ID
  - Current role
  - Phase

---

## Technical Notes

### MCP Tool Definition
```python
{
    name: "gcp_create_role_notes",
    description: "Create or update role decision notes for the current role",
    inputSchema: {
        type: "object",
        properties: {
            work_item_id: {
                type: "string",
                description: "Work item identifier"
            },
            role: {
                type: "string",
                enum: ["project-owner", "program-manager", "quality-assurance",
                       "architect", "developer", "refactor-expert", "builder", "documentor"],
                description: "Role to create notes for (defaults to current role)"
            },
            content: {
                type: "string",
                description: "Markdown content for the notes (optional - uses template if not provided)"
            },
            mode: {
                type: "string",
                enum: ["append", "replace"],
                default: "append",
                description: "How to handle existing file"
            }
        },
        required: ["work_item_id"]
    }
}
```

### File Path
```
WorkItems/<work_item_id>/RoleDecisionNotes/<work_item_id>-<role>.md
```

### Response Schema
```python
{
    "success": bool,
    "file_path": str,
    "created": bool,  # True if new file, False if appended
    "role": str,
    "message": str
}
```

---

## Dependencies

- **GCP-0001**: State persistence
- **GCP-0002**: Role information

---

## Out of Scope

- Custom templates per role (future)
- Git commit of notes (handled by Builder role)

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
