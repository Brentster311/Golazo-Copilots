# GCP-0054 Review Comments — Rename MCP Tools from `gcp_` to `golazo_`

## Overall Assessment

**Approve** — straightforward mechanical rename. Design is clear, approach is sound.

## Key Observations

1. **Primary Risk**: Missed occurrences causing runtime errors. Mitigated by grep verification + full test suite (409 tests).
2. **Atomic Execution**: Correct choice to do all renames in one pass rather than incremental.
3. **Scope Boundaries**: Clear exclusions (historical WorkItems, test filenames) are well-defined.
4. **Breaking Change**: Acknowledged and acceptable — `.github/copilot-instructions.md` updated simultaneously.

## Concerns

- **Stale MCP server process**: After deployment, running MCP server instances will still serve old `gcp_*` names until restarted. Design already notes this risk.
- **Grep verification must exclude**: WorkItems history docs, test filenames (not contents). Pattern needs to be precise.

## Recommendations

- Run post-rename grep with explicit exclusion patterns to avoid false positives from historical WorkItems.
- Verify `tools/__init__.py` exports match renamed files.
- Confirm server tool registration count remains exactly 7.

## Verdict

No design changes needed. Proceed to implementation.
## Architect Notes

### Rename Strategy
- **Order of operations:** Rename files first (`git mv`), then bulk-replace content references. This preserves Git history and avoids a broken intermediate state.
- **Bulk replacement:** Use PowerShell `(Get-Content -Raw) -replace 'gcp_', 'golazo_'` across all affected files for efficiency.

### Key Observations
- **`gcp_init` alias** in `gcp_create_workitem.py` must also be renamed to `golazo_init` (or removed).
- **`capabilities.yaml`** (both root and `golazo-copilot/`) references tool names — needs updating.
- **No changes** to TRANSITIONS, ROLE_ORDER, PHASE_MAP, or state model.

### Security
No concerns — pure mechanical rename, no new entry points or data exposure.

### Capability Impact
Single capability affected: **mcp-server**. See [GCP-0054-Capability-Impact.md](GCP-0054-Capability-Impact.md).