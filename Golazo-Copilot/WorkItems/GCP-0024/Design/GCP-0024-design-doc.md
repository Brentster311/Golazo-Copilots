# GCP-0024: Design Document

## Overview

This design documents the evidence requirements enhancement and role order update for Golazo Copilot v2.16.0.

## Design Decisions

### 1. Remove N/A Evidence Option

**Problem:** The `refactorComplete` DoD item allowed "N/A: reason" as valid evidence, providing an escape hatch that could be abused to skip the Refactor Expert role's responsibilities.

**Solution:** Remove N/A support entirely. All roles must produce concrete artifacts.

**Implementation:**
- Delete `NA_ALLOWED_ITEMS = {"refactorComplete"}` constant
- Delete `validate_na_evidence()` function
- Add `refactorComplete` to `FILE_EVIDENCE_ITEMS`

### 2. Add retroComplete DoD Item

**Problem:** The Retrospective role had no corresponding DoD item, meaning its work wasn't tracked or validated.

**Solution:** Add `retroComplete` DoD item requiring a Retro Plan artifact.

**Implementation:**
- Add to `VALID_DOD_ITEMS` set in checklists.py
- Add to default `dod` dict in WorkItemState (types.py)
- Add to `FILE_EVIDENCE_ITEMS` in evidence.py
- Add evidence hint for the new item

### 3. Update Role Order

**Problem:** The previous order had Builder before Documenter:
```
Developer → Refactor Expert → Builder → Documenter → Retrospective
```

This didn't match natural workflow - documentation should be updated before final build verification.

**Solution:** Swap Documenter and Builder:
```
Developer → Refactor Expert → Documenter → Builder → Retrospective
```

**Implementation:**
- Update `TRANSITIONS` dict
- Update `PHASE_MAP` (Builder now in completion phase)
- Update `ROLE_ORDER` list

## File Changes

| File | Changes |
|------|---------|
| evidence.py | Remove NA_ALLOWED_ITEMS, delete validate_na_evidence(), add refactorComplete/retroComplete to FILE_EVIDENCE_ITEMS, update hints |
| transitions.py | Swap Documenter/builder in TRANSITIONS, PHASE_MAP, ROLE_ORDER |
| checklists.py | Add "retroComplete" to VALID_DOD_ITEMS |
| types.py | Add "retroComplete": ChecklistItem() to dod default |

## Backward Compatibility

- Existing work items with 7 DoD items will work fine - new item starts unchecked
- Role transitions using old order will be rejected - must follow new order
- N/A evidence for refactorComplete will now fail validation

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Existing workflows break | MCP server version check; clear error messages |
| Refactor Expert forced to create file when none needed | Refactoring Plan can document "No changes needed" with justification |
| Retrospective skipped | retroComplete DoD item enforces completion |
