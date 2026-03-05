# GCP-0039: Role Instructions — Reference Capability Registry

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Role Instructions — Reference Capability Registry
- **As a**: GCP user with a `capabilities.yaml` in my project
- **I want**: the QA, Architect, Developer, Refactor Expert, and Retrospective role instructions to mention calling `gcp_capabilities(action="impact", files=[...])` when reviewing or changing files
- **So that**: the LLM assistant automatically checks which capabilities are affected by file changes, preventing downstream misses
- **Out of scope**:
  - Modifying the `gcp_capabilities` tool itself (GCP-0038, done)
  - Adding the tool to `gcp_status` output (GCP-0042)
  - Bootstrap scaffolding (GCP-0040)
  - Spine mention (GCP-0041)
- **Assumptions**:
  - **Assumption (explicit)**: Interface is MCP tool — inherited from GCP
  - **Assumption (explicit)**: Target platform is cross-platform Python — inherited from GCP
  - **Assumption (explicit)**: Users are technical developers using GCP — inherited
  - **Assumption (explicit)**: Changes are to `.md` role files only (no production code changes)
- **Acceptance Criteria**:
  - AC1: QA role (`quality-assurance.md`) instructs the assistant to run `gcp_capabilities(action="impact")` on files touched by the design, and flag any affected capabilities not covered by test cases
  - AC2: Architect role (`architect.md`) instructs the assistant to run impact analysis on files in the design doc and verify contract compatibility
  - AC3: Developer role (`developer.md`) instructs the assistant to run impact analysis before committing, ensuring no downstream capabilities are broken
  - AC4: Refactor Expert role (`refactor-expert.md`) instructs the assistant to run impact analysis on refactored files to verify no transitive dependents are affected
  - AC5: Retrospective role (`retrospective.md`) instructs the assistant to check if a capabilities.yaml exists and, if so, whether it was consulted during the work item — flagging missed opportunities
  - AC6: All role instructions include a conditional: "If `capabilities.yaml` exists in the project root, then..." (no-op if registry doesn't exist)
- **Non-functional requirements**: Role file changes only; no code changes; tests for role content may be added
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: Bootstrap (`gcp_bootstrap --force`) propagates updated roles to workspaces

## Closure

### Summary of delivery
- Backfilled during closure reconciliation for an already implemented work item.

### Final status confirmation
- Work item `GCP-0039` is IMPLEMENTED and workflow artifacts are complete.
