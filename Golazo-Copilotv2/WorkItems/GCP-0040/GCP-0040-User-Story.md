# GCP-0040: Bootstrap — Scaffold capabilities.yaml Template

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Bootstrap — Scaffold capabilities.yaml Template
- **As a**: GCP user bootstrapping a new project
- **I want**: `gcp_bootstrap` to create a starter `capabilities.yaml` template in the project root (if one doesn't already exist)
- **So that**: I have a ready-made structure to fill in rather than writing the YAML schema from scratch
- **Out of scope**:
  - Auto-populating the registry from code analysis
  - Role instruction changes (GCP-0039)
  - Spine mention (GCP-0041)
  - Status hints (GCP-0042)
- **Assumptions**:
  - **Assumption (explicit)**: Interface is MCP tool (`gcp_bootstrap`) — inherited from GCP
  - **Assumption (explicit)**: Target platform is cross-platform Python — inherited
  - **Assumption (explicit)**: Users are technical developers — inherited
  - **Assumption (explicit)**: File persistence (YAML on disk) — inherited from GCP-0038
- **Acceptance Criteria**:
  - AC1: Running `gcp_bootstrap` creates a `capabilities.yaml` in the workspace root with a commented example showing the schema (capabilities, name, description, key_files, contracts, depends_on)
  - AC2: If `capabilities.yaml` already exists, it is NOT overwritten (skipped, reported in files_skipped)
  - AC3: Running `gcp_bootstrap(force=True)` overwrites an existing `capabilities.yaml`
  - AC4: The template includes at least one fully commented example capability
  - AC5: The created file passes `gcp_capabilities(action="validate")` without errors
- **Non-functional requirements**: Template should be self-documenting with YAML comments
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: New bootstrap output; next version bump deploys it

## Closure

### Summary of delivery
- Backfilled during closure reconciliation for an already implemented work item.

### Final status confirmation
- Work item `GCP-0040` is IMPLEMENTED and workflow artifacts are complete.
