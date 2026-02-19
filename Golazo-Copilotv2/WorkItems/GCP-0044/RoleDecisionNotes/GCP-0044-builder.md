# GCP-0044 — Builder Decision Notes

## Git Operations
- Branch: `GCP-0044` created from `GCP-0043`
- Commit: `c32de37` — "GCP-0044: Make workspace_path required on all MCP tools"
- Push: `origin/GCP-0044` — success

## Build Verification
- `python -m pytest tests/` — 136 passed (excluding pre-existing failures)
- No build errors or warnings

## Capability Registry
- `gcp_capabilities(action="validate")` — all 12 capabilities valid, all key_files exist
- No new capabilities introduced
- Only `mcp-server` capability affected (schema contract narrowed), no new contracts or key_files
