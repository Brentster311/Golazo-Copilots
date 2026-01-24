# GCP-008 - Review Comments

## Reviewer Notes

### Reviewed Documents
- GCP-008-User-Story.md
- GCP-008-Design-Doc.md

### Clarity and Completeness

? **Clear scope**: Two extractions (PowerShell, Update) with explicit line ranges
? **Clear deliverables**: New files, updated spine, version bump
? **Clear success criteria**: Line count reduction, file existence, behavior unchanged

### Feasibility and Sequencing

? **Feasible**: Pure content extraction with no logic changes
? **Sequencing correct**: Create guides ? Update spine ? Update meta files

### Risk Coverage

? **Rollback plan**: Single commit revert
? **Upgrade path**: Design addresses updating download list

### Concerns Identified

#### Concern 1: Guide file download order in upgrade (Minor)
**Issue**: The upgrade process creates `.github/guides/` directory implicitly via `Invoke-WebRequest -OutFile`. If the directory doesn't exist, the download will fail.

**Recommendation**: Add explicit directory creation step to upgrade process:
```powershell
New-Item -ItemType Directory -Path ".github/guides" -Force
```

**Impact**: Non-functional clarification to upgrade script. No new User Story needed.

#### Concern 2: Backup process doesn't include guides (Minor)
**Issue**: Current backup script only backs up spine and roles:
```powershell
Copy-Item ".github/copilot-instructions.md" "$backupDir/"
Copy-Item ".github/roles/*.md" "$backupDir/" -Force
```

**Recommendation**: Add guide backup:
```powershell
Copy-Item ".github/guides/*.md" "$backupDir/" -Force -ErrorAction SilentlyContinue
```

**Impact**: Non-functional clarification. No new User Story needed (guides may not exist in older versions, hence `-ErrorAction SilentlyContinue`).

### Edge Cases

1. **Fresh install (no guides directory)**: Handled by `New-Item -Force` in upgrade
2. **Partial upgrade failure**: Existing backup/restore logic handles this
3. **User on 1.0.x upgrading**: Will get guides created for first time

### Naming Clarity

? `powershell-terminal.md` - Clear purpose
? `golazo-update.md` - Clear purpose
? `.github/guides/` - Clear category

### Folder Structure

? Follows existing `.github/` convention
? Parallel to `.github/roles/` pattern

---

## Summary

**Recommendation**: ? Proceed with implementation

**Required adjustments** (non-functional clarifications):
1. Add `New-Item -ItemType Directory -Path ".github/guides" -Force` to upgrade process
2. Add guide backup line with `-ErrorAction SilentlyContinue`

No new User Stories required.
