# GCP-0032 Design Document: Bootstrap Version Sync Check

## Summary

Add a version sync check to `gcp_status` that warns when the deployed `.github/copilot-instructions.md` version doesn't match the running package version.

## Problem Statement

After upgrading the Golazo Copilot package, workspace files (`.github/copilot-instructions.md`) retain the old version. Users get stale instructions without knowing they're outdated. This was observed in GCP-0027 where bootstrap was at 2.17.0 while the package was at 2.100.8.

## Business Case

### Why Now
- Directly requested in GCP-0027 retrospective (AI-2)
- Users have no way to know their workspace instructions are stale

### Impact
- Users get a clear warning when instructions are outdated
- Reduces confusion from stale instructions

### KPIs
- Version mismatch detected and warned in status output

## Functional Requirements

### FR1: Parse deployed version from instructions file
- Read `.github/copilot-instructions.md` relative to workspace root
- Extract version from `<!-- Golazo Copilot Version: X.Y.Z -->` comment
- Return None if file missing or no version found

### FR2: Compare with package version
- Compare extracted version string with `__version__`
- Simple string equality (no semver)

### FR3: Include warning in status output
- Add `version_warning` field to `gcp_status` return dict
- `server.py` renders warning between version line and work item details
- Warning text: `"[WARN] Workspace instructions are stale (v{deployed} != v{current}). Run gcp_bootstrap to update."`

## Proposed Approach

### Step 1: Add `_get_deployed_version()` helper in `gcp_status.py`
- Reads `.github/copilot-instructions.md` from workspace root  
- Uses regex to extract version from HTML comment
- Returns version string or None

### Step 2: Call helper in `gcp_status()` and include in return dict
- Add `version_warning` key (string or None)

### Step 3: Render warning in `server.py`
- If `version_warning` is not None, insert warning line after the `(vX.Y.Z)` header

### Step 4: Add tests
- Test version match (no warning)
- Test version mismatch (warning present)
- Test missing file (no warning)
- Test file without version comment (no warning)

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| File read errors | Catch exceptions, return None (no warning) |
| Different workspace root | Use `work_items_dir.parent` as workspace root (existing pattern) |

## Test Strategy

| Test | Coverage |
|------|----------|
| Match scenario | No warning in return |
| Mismatch scenario | Warning with both versions |
| Missing file | No warning |
| No version comment | No warning |
