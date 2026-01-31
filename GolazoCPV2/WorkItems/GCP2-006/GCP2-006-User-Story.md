# GCP2-006: Multi-Session and Multi-Work-Item Support

**Status**: BACKLOG  
**Priority**: Medium  
**Size**: M  
**Created**: 2026-01-27

---

## User Story

- **Title**: Multi-Session and Multi-Work-Item Support
- **As a**: Developer using Golazo Copilot V2
- **I want**: To work on multiple work items and resume workflows across sessions
- **So that**: I can context-switch between tasks without losing progress

- **Out of scope**:
  - Real-time collaboration (Google Docs style)
  - Role assignment to specific team members
  - Integration with project management tools (Jira, Azure DevOps)
  - Conflict resolution for concurrent edits

- **Assumptions**:
  - **Assumption (explicit)**: Single user per workspace (no multi-user locking)
  - **Assumption (explicit)**: Active work item tracked in workspace-level config
  - **Assumption (explicit)**: CLI commands for switching implemented in GCP2-001c

- **Acceptance Criteria**:
  - [ ] State persists across IDE/Copilot session restart
  - [ ] `golazo list` shows all work items with status
  - [ ] `golazo switch <id>` changes active work item with confirmation
  - [ ] `golazo park [note]` pauses current work item with optional note
  - [ ] Session recovery offers to resume last work item on startup
  - [ ] Clear indication of active work item in status output
  - [ ] Confirmation prompt prevents accidental work on wrong item

- **Non-functional requirements**:
  - Switching work items < 500ms
  - List command handles 100+ work items gracefully

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Enhances GCP2-001c CLI; backward compatible

---

## Background

Golazo V1 limitations:
- Each Copilot conversation is stateless (closes = state lost)
- Working on WI-001, asked about WI-002? Context confusion
- No way to park a work item and return later

---

## Proposed Commands

| Command | Description |
|---------|-------------|
| `golazo list` | Show all work items with status |
| `golazo switch <id>` | Change active work item |
| `golazo park [note]` | Pause current work item |
| `golazo resume <id>` | Resume a parked work item |

---

## Dependencies

- GCP2-003 (State persistence)
- GCP2-001c (CLI implementation)
