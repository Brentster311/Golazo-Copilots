# GCP-0037: Per-File Stale Version Reporting

**Status**: BACKLOG

---

## User Story

- **Title**: Per-File Stale Version Reporting
- **As a**: Golazo Copilot user
- **I want**: `gcp_status` to compare each deployed `.github/` file's version comment against its source counterpart and list any outdated files
- **So that**: I know exactly which files are stale, not just that "the workspace is stale"
- **Out of scope**:
  - Auto-updating stale files (bootstrap already handles that)
  - Changing the version comment format (done in GCP-0036)
  - Capability Index process improvement (separate work item if pursued)
- **Assumptions**:
  - Each source file's `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->` comment is the source of truth for that file
  - Deployed files live in `.github/copilot-instructions.md` and `.github/roles/*.md`
  - Source files are in the installed package (`golazo_copilot/bootstrap-instructions.md` and `golazo_copilot/roles/defaults/*.md`)
  - TechBestPractices.md has no version comment — it should be excluded from stale checking (or flagged separately)
- **Acceptance Criteria**:
  - AC1: `gcp_status` compares each deployed `.github/roles/*.md` file's version comment against its package source version comment
  - AC2: `gcp_status` compares `.github/copilot-instructions.md` version comment against `bootstrap-instructions.md` source version comment
  - AC3: If any deployed file has a version comment that differs from its source, `version_warning` includes a list of the specific stale file names
  - AC4: If all deployed files match their sources (or files are missing), the existing behavior is preserved (no warning or "file not found" — that's bootstrap's job)
  - AC5: Files without version comments (e.g., TechBestPractices.md) are excluded from stale comparison
  - AC6: The old single-version comparison (`copilot-instructions.md` vs `__version__`) is removed
- **Non-functional requirements**: No additional file I/O beyond what's already in the `.github/` directory
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: This changes the version_warning format in gcp_status output. Consumers that parse the warning string may need updating.
