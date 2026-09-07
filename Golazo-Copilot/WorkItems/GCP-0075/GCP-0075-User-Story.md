# GCP-0075 User Story

**Status**: IMPLEMENTED

**User Story**
- Title: Reconcile Builder and Documenter release-order instructions
- As a: Golazo Copilot workflow contributor
- I want: Builder and Documenter instructions to define one executable versioning and changelog sequence
- So that: I can complete release documentation without circular prerequisites or violating the enforced role order
- Out of scope: Reordering unrelated workflow roles; changing semantic-versioning policy; automating package publication; changing product runtime behavior.
- Assumptions:
  - **Assumption (explicit):** The interface is the existing Markdown role guidance returned by Golazo MCP tools.
  - **Assumption (explicit):** The guidance applies cross-platform and persists in packaged default role files plus bootstrap-generated copies.
  - **Assumption (explicit):** `pyproject.toml` remains the canonical Python version source and README changelog entries remain newest-first.
- Acceptance Criteria (bulleted, testable):
  - Builder and Documenter role instructions specify one non-circular owner and sequence for version selection, `pyproject.toml` update, and changelog maintenance.
  - The documented sequence is compatible with the workflow's enforced role order and does not require a future role's artifact as an entry condition.
  - Canonical packaged instructions, bootstrap-generated role files, and README workflow guidance remain consistent.
  - Policy tests fail when circular or contradictory version/changelog instructions are reintroduced.
- Non-functional requirements: Keep guidance concise and unambiguous; preserve semantic-versioning and PEP 440 requirements; avoid changing runtime APIs or workflow state schemas.
- Telemetry / metrics expected: No external telemetry. Tests provide deterministic policy validation.
- Rollout / rollback notes: Deliver as an instruction and policy-test update. Rollback restores prior text only; no state or data migration is required.

## Closure

Delivered a forward-only release process in which Documenter reviews implementation documentation and Builder owns version selection, the canonical `pyproject.toml` update, PEP 440 monotonicity validation, README changelog maintenance, build, commit, and push.

### Acceptance Criteria

- PASS: Packaged Builder and Documenter instructions define one non-circular Builder-owned release sequence.
- PASS: Complete orders Documenter before Builder, while Express includes Builder without Documenter and remains executable.
- PASS: Packaged defaults, forced-bootstrap output, and README guidance are checked for consistency.
- PASS: Policy tests reject backward transitions, future-role prerequisites, and contradictory ownership wording.

### Future Work

No follow-up work item is required. The retrospective recommendation to check mandatory ownership against all profiles is captured as a process practice.

Final status: **IMPLEMENTED**.