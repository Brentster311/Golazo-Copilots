# Role Decision Document: Retrospective

**Work Item**: RETRO-001  
**Role**: Retrospective  
**Date**: 2025-01-XX  
**Trigger**: Critical data loss - codebase deleted without backup

---

## Incident Summary

Copilot deleted the entire California Jack codebase (`PythonApplication2\PythonApplication2\`) while attempting to clean up a nested folder structure. The code was never committed to git, making it unrecoverable.

---

## Root Cause Analysis

| Factor | Failure |
|--------|---------|
| **No backup** | Deleted folder without creating backup first |
| **No verification** | Did not verify which folder contained working code |
| **No git commit** | Code was never committed, so not recoverable |
| **Wrong assumption** | Assumed nested folder was duplicate, not primary |

---

## Process Changes Implemented

### 1. Builder Role: Git Commit Required

**File**: `.github/roles/builder.md`

Added:
- Git commit is now a **required output** of Builder role
- Commit message format: `<workitem-id>: <description>`
- Must document commit hash in builder notes
- Cannot declare "done" without committing

### 2. DoD Checklist: Git Commit Added

**File**: `.github/copilot-instructions.md`

Added to DoD Checklist:
- `[ ] Changes committed to git`

---

## Lessons Learned

1. **Always commit code** before any major operation
2. **Never delete** without backup or git safety net
3. **Verify before delete** - run the code from the folder first
4. **Ask user confirmation** for destructive operations

---

## Recovery Plan

The codebase must be recreated from:
1. Conversation history (file contents shared during session)
2. Open files in IDE (some may still be in memory/cache)
3. Documentation artifacts (still exist in `docs/`)

---

## Process Improvement Summary

| Change | File | Status |
|--------|------|--------|
| Git commit required in Builder | `.github/roles/builder.md` | ? Applied |
| Git commit in DoD checklist | `.github/copilot-instructions.md` | ? Applied |
