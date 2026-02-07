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

### Post-Implementation Discovery

After implementing the warning mechanism, an audit revealed the problem was **far worse than initially understood**:

| Category | Work Items | Missing Notes |
|----------|------------|---------------|
| Zero notes | 11 work items | 99 notes missing |
| Partial notes | 5 work items | 28 notes missing |
| **Total** | **16 work items** | **127 notes retroactively created** |

This proved that **warning-only is insufficient** - the assistant continued to skip notes despite warnings. The retroactive cleanup took significant effort.

---

## Out of Scope
- Automatic generation of role notes content
- ~~Retroactive enforcement on existing work items~~ **DONE**: 127 notes created retroactively after audit
- Blocking transitions (warning only for now) **⚠️ RECONSIDER**: Warning-only proved insufficient

---

## Assumptions
- **Assumption (explicit)**: Role notes follow naming convention `<workitem-id>-<role>.md`
- **Assumption (explicit)**: Notes are stored in `WorkItems/<workitem-id>/RoleDecisionNotes/`
- **Assumption (INVALIDATED)**: ~~Warning is sufficient~~ - Warning-only did not prevent the problem; 127 notes had to be created retroactively

---

## Acceptance Criteria

### Original (Implemented)
- [x] `gcp_transition` checks if outgoing role's decision notes file exists
- [x] If notes file is missing, return includes a `warning` field: "Missing role notes: <role>"
- [x] ~~Warning is displayed to user but does not block the transition~~ **INSUFFICIENT** - see below
- [x] `gcp_status` includes a "missing_notes" list showing which roles lack decision notes
- [x] Role notes check uses correct naming convention for each role

### Revised (Recommended for GCP-0020)
Based on 127 retroactive notes proving warning-only doesn't work:

- [ ] `gcp_transition` **blocks** if outgoing role's decision notes file is missing
- [ ] Error message: "Cannot transition: Missing role notes for <role>. Create the file first."
- [ ] Add `force_without_notes=True` parameter for explicit bypass (requires prior `gcp_consent`)
- [ ] Transition prompt should remind assistant: "Before transitioning, create role notes file"

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

---

## Post-Implementation Lessons Learned

### Why Warning-Only Failed

1. **AI assistants optimize for task completion** - Warnings are noted but don't change behavior
2. **Accumulated debt is invisible** - Without periodic audits, missing notes pile up unnoticed
3. **Retroactive work is expensive** - Creating 127 notes after the fact is far more work than creating them incrementally

### Recommendations for GCP-0020+

1. **Consider blocking mode** - Force note creation before transition allowed
2. **Add audit tooling** - `gcp_audit` to show missing notes across all work items
3. **Make notes part of transition** - Prompt assistant to create note before allowing transition
4. **Periodic audits** - Schedule regular checks for workflow compliance

### Work Items Remediated

GCP-0001, 0002, 0003, 0004, 0005, 0006, 0007, 0008, 0009, 0010, 0012, 0013, 0014, 0016, 0017, 0018
