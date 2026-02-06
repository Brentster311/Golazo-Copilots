# GCP-0010: Bootstrap Command for Copilot Instructions

**Status**: IMPLEMENTED

## User Story

**As a** developer setting up Golazo Copilot in a new repository,  
**I want to** run a bootstrap command that creates the necessary configuration files,  
**So that** I can quickly start using the Golazo workflow without manual setup.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_bootstrap` Creates Instructions File
- [ ] Calling `gcp_bootstrap()`:
  - Creates `.github/copilot-instructions.md` with default content
  - Creates `.github/` directory if not exists
- [ ] Returns success with file path

### AC2: Default Instructions Content
- [ ] Created file includes:
  - Golazo workflow overview
  - Required tool calls (gcp_status before every response)
  - Marking progress instructions (correct parameter names)
  - Role transition instructions
  - File naming conventions
  - DoR/DoD gate documentation

### AC3: Does Not Overwrite Existing
- [ ] If `.github/copilot-instructions.md` already exists:
  - Returns warning: "Instructions file already exists"
  - Does NOT overwrite
- [ ] Optional `force=True` parameter to overwrite

### AC4: Creates WorkItems Directory
- [ ] Also creates `WorkItems/` directory if not exists
- [ ] Creates `.gitkeep` in WorkItems for git tracking

### AC5: Optional Role Files
- [ ] Parameter `include_roles=True` (default False):
  - Copies default role files to `.github/roles/`
  - Allows local customization

### AC6: Workspace Detection
- [ ] Detects workspace root (looks for `.git`, `pyproject.toml`, `package.json`)
- [ ] Creates files relative to workspace root
- [ ] Error if no workspace detected

---

## Technical Notes

### MCP Tool Definition
```python
{
    name: "gcp_bootstrap",
    description: "Bootstrap Golazo Copilot in a workspace - creates copilot instructions and directories",
    inputSchema: {
        type: "object",
        properties: {
            force: {
                type: "boolean",
                default: False,
                description: "Overwrite existing files if they exist"
            },
            include_roles: {
                type: "boolean",
                default: False,
                description: "Also copy default role files to .github/roles/"
            },
            workspace_path: {
                type: "string",
                description: "Workspace root path (auto-detected if not provided)"
            }
        },
        required: []
    }
}
```

### Default Instructions Template
Uses content from `golazo_copilot/bootstrap-instructions.md`

### File Structure Created
```
<workspace>/
??? .github/
?   ??? copilot-instructions.md    # Created by bootstrap
?   ??? roles/                      # Optional, if include_roles=True
?       ??? project-owner-assistant.md
?       ??? program-manager.md
?       ??? ...
??? WorkItems/
    ??? .gitkeep
```

### Response Schema
```python
{
    "success": bool,
    "files_created": list[str],
    "files_skipped": list[str],  # Already existed
    "message": str
}
```

---

## Dependencies

- None - standalone initialization tool

---

## Out of Scope

- Custom template selection (future)
- Interactive setup wizard (future)
- Auto-detecting existing workflow state

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
