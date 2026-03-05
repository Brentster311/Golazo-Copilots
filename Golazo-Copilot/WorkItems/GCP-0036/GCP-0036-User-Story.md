# GCP-0036: Replace Dynamic Version Stamping with Static Last-Updated Comment

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Replace Dynamic Version Stamping with Static Last-Updated Comment
- **As a**: Golazo Copilot maintainer
- **I want**: The version comment in instruction/role files to say `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->` and be static (not dynamically overwritten at deploy time)
- **So that**: The version reflects when the file content was last changed, not the package version at deploy time

---

## Out of Scope
- Changing file content beyond the version comment format
- Adding version tracking to files that don't currently have it
- Version bumping automation

---

## Assumptions
- **Assumption (explicit)**: All files with `<!-- Golazo Copilot Version: X.Y.Z -->` or `<!-- Golazo Version: X.Y.Z -->` will be updated to the new format
- **Assumption (explicit)**: The `_get_default_instructions()` regex replacement in `gcp_bootstrap.py` will be removed
- **Assumption (explicit)**: The version sync warning in `gcp_status` (`_get_deployed_version`) will be updated to match the new comment format

---

## Acceptance Criteria

- [ ] All source role files use `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->` format
- [ ] `bootstrap-instructions.md` uses the new format
- [ ] `_get_default_instructions()` no longer performs dynamic regex version replacement
- [ ] `_get_deployed_version()` in `gcp_status.py` reads the new comment format
- [ ] All existing tests pass with the updated format
- [ ] Version sync warning still works (compares `Last Updated` version vs running package version)

---

## Non-Functional Requirements
- None

---

## Telemetry / Metrics Expected
- None
