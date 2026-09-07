# GCP-0078: Correct README Product Contract

**Status**: IMPLEMENTED

**User Story**
- **Title:** Correct README product contract
- **As a:** Golazo Copilot user
- **I want:** The README to describe the public tools, workflow roles, installation environment, bypass behavior, and Git boundaries accurately
- **So that:** I can install and operate Golazo Copilot without relying on overstated or incomplete behavior
- **Out of scope:** Changing runtime workflow behavior, adding work-item cancellation, implementing Git operations, or resolving the internal Planner initialization inconsistency
- **Assumptions:** **Assumption (explicit):** Documentation should reflect the current v6.0.3 public MCP contract; product inconsistencies remain documented limitations unless separately implemented.
- **Acceptance Criteria:**
  - The README removes the unusable role-note bypass recipe while preserving the valid output-gate bypass instructions.
  - Complete-profile role counts and transition targets match the registered profile, including Planner, while noting that new work items initialize at Project Owner Assistant.
  - The README documents `golazo_role_context`, configured-interpreter installation, proposal-only Git behavior, and the absence of automatic Git/work-item cancellation operations.
  - Duplicate persistence claims are consolidated, and finalization is clearly distinguished from creating the next work item.
  - Focused README contract tests and the full Golazo Copilot test suite pass.
- **Non-functional requirements:** Keep changes documentation-focused, use concise language, preserve existing public APIs, and publish with a PEP 440 patch version and matching changelog entry.
- **Telemetry / metrics expected:** None.
- **Rollout / rollback notes:** Publish as v6.0.4; revert the release commit to roll back.

## Closure

Delivered an accurate v6.0.4 README contract with source-backed regression tests.

- **PASS:** Unsupported role-note bypass wording was removed while valid output-gate bypass guidance remains.
- **PASS:** Complete-profile documentation now includes Planner, 11-role progress, and Project Owner Assistant initialization behavior.
- **PASS:** `golazo_role_context`, configured-interpreter installation, proposal-only Git behavior, and unsupported automation boundaries are documented.
- **PASS:** Persistence claims are consolidated and work-item finalization is distinguished from creation.
- **PASS:** Six focused tests, 557 full-suite tests, coverage validation, Ruff, capability validation, and wheel build passed.

Future work candidates: align Express QA design inputs, resolve the public `skip_role` consent mismatch, separate timing tests from coverage guidance, and align Builder branch push instructions. These candidates have not been created as work items.

Final status: **IMPLEMENTED**.

