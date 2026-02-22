# GCP-0046 — Architect Decision Notes

## Work Item
GCP-0046: Add Domain Expert Role to the Definition Phase

## Architecture Review

### Alignment
- Change touches only `transitions.py` (data constants) and adds a new role file — no structural changes to the MCP server, tool modules, or output validator
- The `VALID_ROLES` set is derived from `TRANSITIONS.keys()`, so adding the new key automatically registers the role everywhere

### Capability Impact
- 1 directly affected capability (`transitions`)
- 3 transitively affected capabilities (`tool-transition`, `tool-status`, `mcp-server`) — none require code changes
- Full impact documented in `GCP-0046-Capability-Impact.md`

### Decisions
1. **No API changes needed** — the `role` parameter already accepts any string in VALID_ROLES
2. **No output validator changes** — the validator reads `## Required Outputs` from whatever role file is active; a new role file "just works"
3. **Bootstrap impact** — `gcp_bootstrap` copies role files from `roles/defaults/` to `.github/roles/`; the new file will be automatically included in future bootstraps

### Risks Accepted
- Existing work items in `program-manager` state will be routed to `domain-expert` on next forward transition — this is correct and desired
