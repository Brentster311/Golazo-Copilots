# GCP2-003: Structured State Management - Design Document

**Work Item**: GCP2-003  
**Version**: 1.0  
**Created**: 2026-01-27  
**Author**: Program Manager

---

## Summary

Implement a JSON-based state persistence layer for Golazo V2 that stores workflow state (current role, phase, DoR/DoD status, role history, and deviations) in files within the `WorkItems/` directory. This enables the agent to maintain state across sessions and provides a foundation for IDE extensions and multi-session support.

---

## Problem Statement

Golazo V1 has no persistent state. Workflow progress exists only in:
- Copilot's conversation context (lost when session ends)
- Markdown status headers (requires parsing, easily corrupted)
- Human memory (unreliable)

This causes:
- **Lost progress**: Closing IDE/Copilot loses workflow position
- **No programmatic access**: Cannot query "what role am I in?" via code
- **No integration**: IDE extensions cannot read workflow status
- **No audit trail**: Deviations not recorded persistently

---

## Business Case

### Why Now?
State persistence is foundational to all other GCP2 work items:
- GCP2-001a (State Machine) needs state to persist
- GCP2-005 (IDE Extensions) needs state to display
- GCP2-006 (Multi-Session) needs state to switch between work items

**Blocking**: This must be completed first.

### Impact
| Metric | Before | After |
|--------|--------|-------|
| Session continuity | None | Full |
| State query time | N/A (impossible) | < 100ms |
| IDE integration | None | Enabled |

### KPIs
- State file created for 100% of active work items
- State read/write < 100ms
- Zero data loss on normal session close

---

## Stakeholders

| Role | Interest |
|------|----------|
| **Developers** | Resume workflows after closing IDE |
| **GCP2-001a** | Consume state for state machine |
| **GCP2-005** | Read state for UI display |
| **GCP2-006** | Manage multiple work item states |

---

## Requirements

### Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | State stored as JSON at `WorkItems/<id>/state.json` | AC-1 |
| FR-2 | State includes: workItemId, profile, currentRole, currentPhase | AC-2 |
| FR-3 | State includes: createdAt, updatedAt timestamps | AC-2 |
| FR-4 | State includes: dor object with boolean flags | AC-3 |
| FR-5 | State includes: dod object with boolean flags | AC-4 |
| FR-6 | State includes: roleHistory array with entry/exit timestamps | AC-5 |
| FR-7 | State includes: deviations array for audit trail | Schema |
| FR-8 | State includes: schemaVersion for future migrations | NFR |
| FR-9 | State file is pretty-printed (human-readable) | AC-7 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Read/write latency | < 100ms |
| NFR-2 | File format | Valid JSON |
| NFR-3 | Schema versioning | Include schemaVersion field |
| NFR-4 | No external dependencies | Python standard library only |

---

## Proposed Approach

### High-Level Design

```
???????????????????????????????????????????
?           GolazoState Class             ?
???????????????????????????????????????????
? + load(work_item_id) ? State            ?
? + save(state) ? None                    ?
? + create(work_item_id, profile) ? State ?
? + exists(work_item_id) ? bool           ?
???????????????????????????????????????????
                    ?
                    ?
         WorkItems/<id>/state.json
```

### Implementation Phases

| Phase | Deliverable | Description |
|-------|-------------|-------------|
| 1 | State dataclass | Python dataclass representing state schema |
| 2 | Load/save functions | Read/write JSON with pretty-printing |
| 3 | Create function | Initialize new state with defaults |
| 4 | Validation | Ensure state file is valid on load |

### File Location

```
WorkItems/
??? GCP2-003/
?   ??? GCP2-003-User-Story.md
?   ??? state.json                 ? NEW
?   ??? Design/
?   ?   ??? GCP2-003-Design-Doc.md
?   ??? RoleDecisionNotes/
?       ??? ...
```

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| **YAML format** | Human-readable, supports comments | Requires PyYAML dependency | Rejected |
| **SQLite database** | Query support, ACID | Overkill for single-user, adds complexity | Rejected |
| **Single global state file** | Simpler | Harder to manage per-work-item | Rejected |
| **JSON (chosen)** | No dependencies, native Python support, tooling | No comments | **Selected** |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| State file corruption | Low | High | Validate JSON on load; log errors |
| Schema changes break old files | Medium | Medium | schemaVersion field enables migration |
| Concurrent access conflicts | Low | Low | Single-user assumption; defer to GCP2-006 |
| File permissions issues | Low | Medium | Clear error messages with path |

### Open Questions

1. ~~JSON vs YAML?~~ ? Decided: JSON
2. Should state.json be gitignored? ? **Recommend: No** (allows sharing workflow state)

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Python 3.10+ | Runtime | Available |
| json module | Library | Standard library |
| dataclasses | Library | Standard library |
| pathlib | Library | Standard library |

**Downstream dependents**:
- GCP2-001a (State Machine) - consumes state
- GCP2-005 (IDE Extensions) - reads state
- GCP2-006 (Multi-Session) - manages multiple states

---

## Migration / Rollout / Rollback Plan

### Migration
- N/A: V1 has no state files. This is greenfield.

### Rollout
1. Implement state module
2. Integrate into GCP2-001a (State Machine)
3. State files created automatically when work items are started

### Rollback
- Delete state.json files
- No other changes required (additive feature)

---

## Observability Plan

### Logging
- Log state file creation: `INFO: Created state file at WorkItems/GCP2-003/state.json`
- Log state load: `DEBUG: Loaded state for GCP2-003 (role: developer)`
- Log errors: `ERROR: Failed to parse state.json: {error}`

### Monitoring
- None for MVP (local tool)

### Alerting
- None for MVP

---

## Test Strategy Summary

| Test Type | Coverage |
|-----------|----------|
| Unit tests | State dataclass, load/save functions, validation |
| Integration tests | End-to-end: create ? modify ? reload |
| Edge cases | Missing file, corrupted JSON, missing fields |

**Key test scenarios**:
1. Create new state ? verify file created with correct schema
2. Load existing state ? verify all fields populated
3. Save modified state ? verify changes persisted
4. Load corrupted file ? verify graceful error handling
5. Load old schema version ? verify migration or clear error

---

## Appendix: State Schema

```json
{
  "schemaVersion": "1.0",
  "workItemId": "GCP2-003",
  "profile": "complete",
  "currentPhase": "design",
  "currentRole": "program-manager",
  "createdAt": "2026-01-27T10:00:00Z",
  "updatedAt": "2026-01-27T14:30:00Z",
  "dor": {
    "userStory": true,
    "designDoc": false,
    "reviewComments": false,
    "testCases": false
  },
  "dod": {
    "branchCreated": false,
    "testsWrittenFirst": false,
    "testsPass": false,
    "buildPasses": false,
    "docsUpdated": false,
    "refactorComplete": false,
    "committed": false
  },
  "roleHistory": [
    {
      "role": "project-owner",
      "enteredAt": "2026-01-27T10:00:00Z",
      "exitedAt": "2026-01-27T10:30:00Z"
    },
    {
      "role": "program-manager",
      "enteredAt": "2026-01-27T10:30:00Z",
      "exitedAt": null
    }
  ],
  "deviations": []
}
```
