# GCP-0034: Design Document

## Summary
Add `WorkItems` to `WORKSPACE_MARKERS` in `gcp_bootstrap.py` so workspaces containing a `WorkItems/` directory are recognized as valid.

## Problem Statement
`gcp_bootstrap` rejects workspaces that have a `WorkItems/` directory but no other markers (`.git`, `pyproject.toml`, etc.). This causes bootstrap to fail or deploy to the wrong directory (ancestor with `.git`).

## Proposed Approach
Add `"WorkItems"` to the `WORKSPACE_MARKERS` list in `gcp_bootstrap.py`. The existing `_is_workspace()` function uses `Path.exists()` which works for both files and directories.

## Change
- File: `golazo-copilot/src/golazo_copilot/tools/gcp_bootstrap.py`
- Line 11: Add `"WorkItems"` to `WORKSPACE_MARKERS`

## Test Strategy
- New test: verify `_is_workspace()` returns True when only `WorkItems/` exists
- Existing bootstrap tests continue to pass
