# GCP-0050 User Story

**Status**: IMPLEMENTED

## User Story

- **Title:** Subagent Orchestration Spine
- **As a:** Golazo Copilot user
- **I want:** The bootstrap-instructions.md (spine) rewritten so that Copilot operates as an orchestrator that delegates each role's work to a focused subagent, rather than performing all role work in a single bloated context
- **So that:** Each role gets a clean context window with only its instructions and relevant artifacts, subagent outputs are higher quality due to reduced context pollution, and the orchestrator maintains a clear separation between workflow control (its job) and creative work (subagent jobs)

- **Out of scope:**
  - Changes to MCP tool Python code (no new tools ΓÇö uses existing gcp_status, gcp_transition, and GCP-0049's gcp_role_context)
  - Changes to role file content (that's GCP-0048)
  - Changes to state machine logic or transitions
  - Multi-work-item parallel orchestration (future work)

- **Assumptions:**
  - **Assumption (explicit):** The orchestrator pattern works as: (1) call `gcp_status` to get current role, (2) call `gcp_role_context` to get the subagent's context bundle, (3) spawn a subagent with the bundle as its prompt, (4) collect the subagent's output, (5) call `gcp_transition` to advance, (6) repeat. The orchestrator never writes code, design docs, or test cases itself ΓÇö it only manages the workflow.
  - **Assumption (explicit):** The subagent spawning mechanism is Copilot's built-in `runSubagent` capability (available in VS Code Copilot Chat). The spine instructs Copilot to use it, but cannot enforce it programmatically ΓÇö the instruction is behavioral guidance.
  - **Assumption (explicit):** The spine includes a fallback mode: if subagent spawning fails or is unavailable (e.g., older Copilot version), the orchestrator falls back to performing the role work inline (current V2 behavior). This is documented in the spine as a graceful degradation.
  - **Assumption (explicit):** The orchestrator displays a brief status summary between subagent invocations so the user has visibility into progress (which role just completed, what it produced, what's next).
  - **Assumption (explicit):** The user can override the subagent pattern at any time by saying "do this inline" or "don't use subagents" ΓÇö the spine includes a user-override escape hatch.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] AC1: `bootstrap-instructions.md` describes the orchestrator pattern: call `gcp_status` ΓåÆ call `gcp_role_context` ΓåÆ spawn subagent ΓåÆ collect output ΓåÆ call `gcp_transition` ΓåÆ repeat
  - [ ] AC2: The spine defines the orchestrator's responsibilities (workflow sequencing, gate enforcement, user communication) separately from the subagent's responsibilities (creative work per role instructions)
  - [ ] AC3: The spine includes a fallback mode section that describes inline execution when subagents are unavailable, with the trigger condition clearly stated
  - [ ] AC4: The spine includes a subagent prompt template showing how to compose the `runSubagent` call with the context bundle from `gcp_role_context`
  - [ ] AC5: The spine includes a "between-roles summary" instruction telling the orchestrator to display: completed role, artifacts produced, next role, and any warnings from gcp_transition
  - [ ] AC6: The spine includes a user-override mechanism (e.g., "work inline" / "no subagents") that switches to single-agent mode for the remainder of the session
  - [ ] AC7: The updated spine is Γëñ 150 lines (current is ~50 lines; the orchestrator pattern adds complexity but must remain concise enough for Copilot to follow reliably)

- **Non-functional requirements:**
  - The spine must be clear enough that Copilot follows the orchestrator pattern without additional prompting at least 80% of the time
  - Subagent prompts must include explicit "return your output, do not ask questions" instructions to prevent subagents from trying to interact with the user directly

- **Telemetry / metrics expected:** None (markdown file)

- **Rollout / rollback notes:**
  - Rollout: Bump version, rebuild package, re-bootstrap workspaces. Users with existing `.github/copilot-instructions.md` need to re-run `gcp_bootstrap` (with `force=true` for the instructions file).
  - Rollback: Revert to previous bootstrap-instructions.md, rebuild. Existing workspaces keep the old spine until re-bootstrapped.

## Dependencies

- **Depends on:** GCP-0048 (self-contained role files), GCP-0049 (gcp_role_context tool)
- **Prerequisite for:** GCP-0052 (integration testing validates the full orchestrator flow)

## Closure

### Summary of delivery
- Backfilled during closure reconciliation for an already implemented work item.

### Final status confirmation
- Work item `GCP-0050` is IMPLEMENTED and workflow artifacts are complete.
