# GCP-0048 User Story

**Status**: IMPLEMENTED

## User Story

- **Title:** Self-Contained Role Instructions for Subagent Isolation
- **As a:** Golazo Copilot developer
- **I want:** Each role markdown file refactored to be a fully self-contained subagent brief — no implicit cross-role context, explicit artifact paths, embedded success criteria, and a machine-readable metadata header
- **So that:** Any role file can be handed to an isolated subagent (with no prior conversation history) and that subagent can perform the role's work correctly without needing context carried over from previous roles

- **Out of scope:**
  - Changes to MCP tool Python code (server.py, tool handlers)
  - Changes to transitions.py or state machine logic
  - Adding or removing roles from ROLE_ORDER
  - Changes to copilot-instructions.md / bootstrap-instructions.md (that's GCP-0050)

- **Assumptions:**
  - **Assumption (explicit):** "Self-contained" means each role file includes: (a) a YAML front-matter block listing input artifacts it expects to find, output artifacts it must produce, and the MCP tools it should call; (b) explicit `WorkItems/<id>/` path patterns for every artifact reference; (c) no phrases like "from the previous role" — replaced with exact file references
  - **Assumption (explicit):** The existing role file markdown structure (Purpose, First action, Entry conditions, Responsibilities, Forbidden actions, Required Outputs, Decision rules, Escalation rules, Success criteria) is preserved — this work adds to it, not replaces it
  - **Assumption (explicit):** TechBestPractices.md is not a role and does not get a front-matter block, but each role that references it gets an explicit path reference instead of assuming it's in context
  - **Assumption (explicit):** All changes apply to the source defaults copy (`roles/defaults/`). The 2 deployed copies (`.github/roles/` and `golazo-copilot/.github/roles/`) are updated to match via bootstrap

- **Acceptance Criteria (bulleted, testable):**
  - [ ] AC1: Every role file in `roles/defaults/` has a YAML front-matter block with `inputs:` (list of artifact file patterns the role reads), `outputs:` (list of artifact file patterns the role must produce), and `tools:` (list of MCP tool names the role should call)
  - [ ] AC2: No role file contains implicit cross-role references (grep for "previous role", "from the last", "earlier phase", "already created" returns zero matches in role files)
  - [ ] AC3: Every artifact reference in role files uses the explicit `WorkItems/{id}/` path pattern — no bare filenames without paths
  - [ ] AC4: `output_validator.py` can still parse `## Required Outputs` from the updated files without modification (backward compatible)
  - [ ] AC5: A new test `test_role_self_contained.py` validates AC1–AC3 programmatically across all role files
  - [ ] AC6: Each role file's front-matter `outputs:` list is consistent with its `## Required Outputs` section (test validates no drift)

- **Non-functional requirements:**
  - Role files must remain human-readable — the front-matter is additive, not a replacement for prose
  - Existing tests continue to pass without modification

- **Telemetry / metrics expected:** None (role files are static markdown)

- **Rollout / rollback notes:**
  - Rollout: Bump version, rebuild package. Bootstrap new workspaces to get updated roles. Existing workspaces need re-bootstrap.
  - Rollback: Revert role file changes, rebuild with previous version.

## Dependencies

- **Prerequisite for:** GCP-0049 (Role Context Bundler), GCP-0050 (Subagent Orchestration Spine)
- **Depends on:** GCP-0047 (role improvements must be complete first — this builds on the improved role structure)

## Closure

### Summary of delivery
- Backfilled during closure reconciliation for an already implemented work item.

### Final status confirmation
- Work item `GCP-0048` is IMPLEMENTED and workflow artifacts are complete.
