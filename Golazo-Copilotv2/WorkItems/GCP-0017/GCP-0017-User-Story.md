# GCP-0017: Separation of Concerns in Role Instructions

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Move Role-Specific Instructions from Bootstrap to Role Files
- **As a**: Golazo Copilot maintainer
- **I want**: Role-specific instructions in `bootstrap-instructions.md` to be moved to individual role files
- **So that**: Each role file is self-contained and the bootstrap file only contains cross-cutting workflow mechanics

---

## Out of Scope
- Changing the actual behavior of roles
- Adding new roles or modifying role sequence
- Changes to the MCP server code

---

## Assumptions
- **Assumption (explicit)**: Role files are located at `.github/roles/<role>.md` or packaged defaults
- **Assumption (explicit)**: Bootstrap should only contain: how to call MCP tools, file naming conventions, and general workflow guidance

---

## Acceptance Criteria

- [ ] `bootstrap-instructions.md` contains only workflow mechanics (MCP tool calls, file paths, gate enforcement)
- [ ] Role-specific output requirements (e.g., "Project Owner: User Story + notes") are moved to respective role files
- [ ] Each role file specifies its own required outputs
- [ ] `gcp_bootstrap` generates updated files with proper separation
- [ ] No duplication of instructions between bootstrap and role files

---

## Non-Functional Requirements
- Maintainability: Single source of truth for each role's responsibilities
- Clarity: Developers can read one role file to understand all requirements for that role

---

## Telemetry / Metrics Expected
- None

---

## Rollout / Rollback Notes
- Documentation-only change to packaged role files
- Existing workspaces with local role overrides unaffected
