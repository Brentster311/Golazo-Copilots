# GCP-0052 User Story

**Status**: BACKLOG

## User Story

- **Title:** Subagent Handoff Protocol & Integration Testing
- **As a:** Golazo Copilot developer
- **I want:** A documented handoff protocol defining how artifacts and context flow between sequential role subagents, plus end-to-end integration tests that validate the full orchestrator → subagent → artifacts → next-subagent flow
- **So that:** The subagent architecture is verified to work correctly with the deterministic gate enforcement, artifact validation catches gaps between roles, and future contributors understand the contract between orchestrator and subagents

- **Out of scope:**
  - Changes to MCP tool implementations (gcp_transition, gcp_status, etc.)
  - Changes to role file content or spine instructions  
  - Performance optimization (that's GCP-0051)
  - Multi-work-item parallel orchestration

- **Assumptions:**
  - **Assumption (explicit):** The handoff protocol is documented as a new markdown file (`WorkItems/Golazo-Subagent-Handoff-Protocol.md`) that defines: (a) the orchestrator's responsibilities at each transition boundary, (b) the artifact contract between consecutive roles (what role N writes that role N+1 reads), (c) the error recovery strategy when a subagent fails to produce required outputs, (d) the context limits and truncation behavior inherited from gcp_role_context
  - **Assumption (explicit):** Integration tests use mocked subagent execution (simulating file creation) rather than actual LLM calls — the tests validate the orchestration machinery, not the LLM output quality
  - **Assumption (explicit):** The test suite walks a complete 10-role workflow from project-owner-assistant through retrospective (and back to POA closure), verifying at each transition that: (a) gcp_role_context returns the correct input artifacts, (b) gcp_transition validates outputs correctly, (c) state.json is updated correctly
  - **Assumption (explicit):** A "handoff matrix" table is produced that maps every role pair (N → N+1) to the artifacts that bridge them, making dependency gaps visible

- **Acceptance Criteria (bulleted, testable):**
  - [ ] AC1: `Golazo-Subagent-Handoff-Protocol.md` exists in `WorkItems/` and contains: orchestrator responsibilities, subagent contract, artifact handoff matrix (role × artifacts), error recovery strategy
  - [ ] AC2: The handoff matrix covers all 10 role transitions (including retrospective → POA closure) with specific artifact file patterns for each
  - [ ] AC3: New test file `test_subagent_integration.py` walks a full 10-role workflow using mocked file creation, asserting at each step that gcp_role_context returns correct inputs and gcp_transition succeeds after mock outputs are created
  - [ ] AC4: The integration test includes a negative case: a subagent "fails" to create a required output, and the test verifies that gcp_transition blocks the advancement with the correct error message
  - [ ] AC5: The integration test includes a backward-transition case: after reaching developer, a subagent triggers a return to architect, and the test verifies the handoff protocol handles re-entry correctly (architect gets the updated artifacts, not the originals)
  - [ ] AC6: All existing tests continue to pass (no regressions)

- **Non-functional requirements:**
  - The handoff protocol document must be concise (≤ 200 lines) and structured for quick reference, not exhaustive prose
  - Integration tests must complete in < 10 seconds (no real I/O beyond temp directories)

- **Telemetry / metrics expected:** None

- **Rollout / rollback notes:**
  - Rollout: Merge tests and documentation. No runtime impact — this is a verification and documentation work item.
  - Rollback: Remove test file and protocol document.

## Dependencies

- **Depends on:** GCP-0048 (self-contained role files with front-matter), GCP-0049 (gcp_role_context tool), GCP-0050 (orchestration spine)
- **Prerequisite for:** None (capstone work item for the subagent initiative)
