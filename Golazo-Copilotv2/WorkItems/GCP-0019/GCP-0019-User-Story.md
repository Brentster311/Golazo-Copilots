# GCP-0019: Enforce Role Decision Notes on Transition

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Enforce Role Decision Notes Creation on Transition
- **As a**: Project Owner using Golazo workflow
- **I want**: `gcp_transition` to warn (or block) when the outgoing role has not produced its required decision notes
- **So that**: Every role produces its required artifacts as mandated by the workflow

---

## Problem Statement

The Golazo workflow requires "Every role produces a document" but the MCP tools do not enforce this. In GCP-0014, 8 of 9 role decision notes were missing because the assistant optimized for speed over compliance.

---

## Out of Scope
- Automatic generation of role notes content
- Retroactive enforcement on existing work items
- Blocking transitions (warning only for now)

---

## Assumptions
- **Assumption (explicit)**: Role notes follow naming convention `<workitem-id>-<role>.md`
- **Assumption (explicit)**: Notes are stored in `WorkItems/<workitem-id>/RoleDecisionNotes/`
- **Assumption (explicit)**: Warning is sufficient - blocking may be too restrictive

---

## Acceptance Criteria

- [ ] `gcp_transition` checks if outgoing role's decision notes file exists
- [ ] If notes file is missing, return includes a `warning` field: "Missing role notes: <role>"
- [ ] Warning is displayed to user but does not block the transition
- [ ] `gcp_status` includes a "missing_notes" list showing which roles lack decision notes
- [ ] Role notes check uses correct naming convention for each role

---

## Non-Functional Requirements
- File existence check should be fast (<10ms)
- Should work with both default and custom WorkItems directories

---

## Telemetry / Metrics Expected
- Count of transitions with missing notes warnings

---

## Rollout / Rollback Notes
- Non-breaking change (warning only)
- Rollback: remove warning logic
