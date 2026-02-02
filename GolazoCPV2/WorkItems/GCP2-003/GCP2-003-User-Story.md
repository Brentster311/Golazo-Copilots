# GCP2-003: Structured State Management

**Status**: BACKLOG  
**Priority**: High  
**Size**: S  
**Created**: 2026-01-27

---

## User Story

- **Title**: Structured State Management
- **As a**: Developer using Golazo Copilot V2
- **I want**: Workflow state stored in machine-readable JSON format
- **So that**: State can be queried, persisted across sessions, and integrated with IDE extensions

- **Out of scope**:
  - GitHub Actions integration
  - Team collaboration features (covered in GCP2-006)
  - Database persistence (files only for MVP)

- **Assumptions**:
  - **Assumption (explicit)**: JSON chosen over YAML for easier programmatic access
  - **Assumption (explicit)**: State file located at `WorkItems/<id>/state.json`
  - **Assumption (explicit)**: Single active work item per session (multi-session in GCP2-006)

- **Acceptance Criteria**:
  - [ ] State file created as JSON at `WorkItems/<id>/state.json`
  - [ ] State includes: workItemId, profile, currentRole, currentPhase, timestamps
  - [ ] State includes DoR status object with boolean flags
  - [ ] State includes DoD status object with boolean flags
  - [ ] State includes roleHistory array with entry/exit timestamps
  - [ ] State persists across Copilot/IDE sessions
  - [ ] State file is human-readable (pretty-printed JSON)

- **Non-functional requirements**:
  - State file read/write must complete in < 100ms
  - State file must be valid JSON (parseable by standard libraries)
  - State schema must be versioned for future migrations

- **Telemetry / metrics expected**:
  - None for MVP (local file only)

- **Rollout / rollback notes**:
  - New file format; no migration from V1 required (V1 has no state files)

---

## Background

Golazo V1 tracks state via:
- Markdown status headers in Copilot responses
- Existence of artifact files in directories
- Human interpretation of checklist items

This makes it impossible to:
- Programmatically query "what's the current role?"
- Resume a workflow after closing IDE
- Track multiple work items simultaneously

---

## State Schema

```json
{
  "schemaVersion": "1.0",
  "workItemId": "GCP2-003",
  "profile": "complete",
  "currentPhase": "development",
  "currentRole": "developer",
  "createdAt": "2026-01-27T10:00:00Z",
  "updatedAt": "2026-01-27T14:30:00Z",
  "dor": {
    "userStory": true,
    "designDoc": true,
    "reviewComments": true,
    "testCases": true
  },
  "dod": {
    "branchCreated": true,
    "testsWrittenFirst": true,
    "testsPass": false,
    "buildPasses": false,
    "docsUpdated": false,
    "refactorComplete": false,
    "committed": false
  },
  "roleHistory": [
    {"role": "project-owner", "enteredAt": "2026-01-27T10:00:00Z", "exitedAt": "2026-01-27T10:30:00Z"},
    {"role": "developer", "enteredAt": "2026-01-27T14:00:00Z", "exitedAt": null}
  ],
  "deviations": []
}
```

---

## Dependencies

- None (foundational; GCP2-001a depends on this)
