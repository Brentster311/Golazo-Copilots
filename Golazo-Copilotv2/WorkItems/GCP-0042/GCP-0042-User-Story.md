# GCP-0042: gcp_status — Surface Capability Registry Presence and Impact Hints

**Status**: IMPLEMENTED

---

## User Story

- **Title**: gcp_status — Surface Capability Registry Hints
- **As a**: GCP user calling `gcp_status`
- **I want**: the status output to indicate whether a `capabilities.yaml` exists in the project and, if so, show a hint to run impact analysis
- **So that**: I'm reminded the capability registry is available without having to remember to call it separately
- **Out of scope**:
  - Running impact analysis automatically (just a hint)
  - Role instruction changes (GCP-0039)
  - Bootstrap scaffolding (GCP-0040)
  - Spine mention (GCP-0041)
- **Assumptions**:
  - **Assumption (explicit)**: Interface is MCP tool (`gcp_status`) — inherited
  - **Assumption (explicit)**: Target platform is cross-platform Python — inherited
  - **Assumption (explicit)**: Users are technical developers — inherited
  - **Assumption (explicit)**: Status output is markdown text — inherited
- **Acceptance Criteria**:
  - AC1: When `capabilities.yaml` exists in the workspace root, `gcp_status` output includes a line like: "Capability Registry: found (N capabilities). Use `gcp_capabilities(action='impact')` to check affected features."
  - AC2: When `capabilities.yaml` does NOT exist, no registry line appears (silent absence, no warning)
  - AC3: The hint appears in the status output after the role progress section
  - AC4: The capability count (N) is accurate — parsed from the YAML
  - AC5: Malformed `capabilities.yaml` shows a warning instead of crashing status
- **Non-functional requirements**: Must not slow down `gcp_status` noticeably (YAML parse is fast)
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: Requires code change to `gcp_status.py` and `server.py` formatter

## Closure

### Summary of delivery
- Backfilled during closure reconciliation for an already implemented work item.

### Final status confirmation
- Work item `GCP-0042` is IMPLEMENTED and workflow artifacts are complete.
