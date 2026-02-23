# GCP-0054 Architect Decision Notes — Rename MCP Tools from `gcp_` to `golazo_`

## Architectural Decisions

### AD-1: Use `git mv` for file renames to preserve history
File renames (e.g., `gcp_status.py` → `golazo_status.py`) should use `git mv` so Git tracks the rename and `git log --follow` works.

### AD-2: Use bulk PowerShell replacement for content changes
After file renames, use PowerShell `(Get-Content ... -Raw) -replace` or equivalent bulk sed to update all `gcp_` → `golazo_` references in file contents. Single pass, atomic.

### AD-3: Rename files first, then update all imports/references
Order: (1) `git mv` files, (2) bulk-replace content references, (3) run tests. This avoids broken imports during the rename window.

### AD-4: `capabilities.yaml` needs tool name references updated
Both root `capabilities.yaml` and `golazo-copilot/capabilities.yaml` reference `gcp_*` tool names — these must be renamed to `golazo_*`.

### AD-5: No changes to TRANSITIONS, ROLE_ORDER, PHASE_MAP, or state model
The rename is limited to MCP tool entry points. Internal role/phase/state machinery is unaffected.

## Additional Notes

- **`gcp_init` alias in `gcp_create_workitem.py`**: This alias also needs renaming to `golazo_init` (or removed if deemed unnecessary). Design doc should confirm.
- **Security:** No concerns — pure string rename, no new attack surface.
- **Rollback:** Simple `git revert` of the rename commit.
