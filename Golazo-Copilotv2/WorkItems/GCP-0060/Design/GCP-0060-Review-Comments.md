# GCP-0060 Review Comments

## QA Outcome
- **Decision**: Design is implementable with clarifications; no blocking defect requiring return to Program Manager.
- **Scope guard**: Keep this work item proposal-only; no git execution behavior is introduced.

## Strengths
- Functional requirements map cleanly to user story acceptance criteria.
- Backward compatibility is explicitly addressed through default initialization of `git_actions`.
- Risks and mitigations identify the highest governance concerns (bypass, persistence failure, serialization drift).

## Actionable Review Comments

### Critical (must be explicit in implementation/tests)
1. **Deterministic validation contract must be machine-assertable**
  - Current design states deterministic behavior but does not define error payload shape.
  - Recommendation: lock a stable error contract for missing required parameters.
  - Minimum expected semantics:
    - `commit` without `message` -> parameter-required error identifying `message`
    - `push`/`branch` without `branch` -> parameter-required error identifying `branch`
  - Why: prevents regression in validation semantics and enables exact assertions.

2. **Timestamp normalization must be pinned to UTC ISO-8601 with trailing `Z`**
  - Current wording mentions timestamp but not strict format requirement.
  - Recommendation: require UTC ISO-8601 `...Z` in proposal record contract.
  - Why: avoids cross-platform parsing drift and preserves audit comparability.

3. **Append-only integrity should explicitly prohibit in-place mutation**
  - Current design says append-only history but does not state immutability semantics for existing entries.
  - Recommendation: clarify that this work item only appends; it does not edit/remove prior proposal entries.
  - Why: protects audit lineage and prevents ambiguous history rewriting.

### Important (high-value operability clarifications)
4. **Missing-work-item guidance should be explicit and consistent**
  - Recommendation: ensure not-found response includes clear creation guidance and is deterministic across calls.
  - Why: avoids support ambiguity and aligns with acceptance criteria.

5. **Persistence failure behavior must be hard-fail, never partial-success**
  - Recommendation: explicitly state no success result is returned when state persistence fails.
  - Why: prevents false audit confidence during intermittent filesystem errors.

## Requirement/Testability Coverage Check
- AC: initialize missing `git_actions` safely -> testable and covered.
- AC: `add` persists one proposal record with required fields -> testable and covered.
- AC: `commit` missing `message` deterministic error -> testable and covered.
- AC: `push`/`branch` missing `branch` deterministic error -> testable and covered.
- AC: missing work item guidance + round-trip persistence -> testable and covered.

## Risks to Watch During Implementation
- Bypass risk remains operational (downstream git actions may occur without prior proposal) and should be observed via KPI ratio.
- Cross-platform timestamp/serialization differences can still regress unless format assertions are strict.
- Legacy state paths unrelated to `git_actions` may regress if defaults are not applied uniformly on load/save.

## QA Assumptions
- Design file `GCP-0060-design-doc.md` is treated as the canonical design artifact for this work item despite case variation from role template.
- Deterministic errors are validated by stable semantic fields/messages rather than locale-specific phrasing.

## Architect Notes

### Architectural Alignment and Boundaries
- **Decision**: Keep the feature as a proposal-only MCP path (`golazo_git_propose`) with no git execution side effects in this work item.
- **Boundary contract**: Tool responsibility is limited to validation + append-only state persistence under `git_actions`; downstream execution remains outside scope.
- **Coupling control**: Route changes through existing state/persistence abstractions to avoid duplicating file I/O semantics.

### Contract Hardening (Required)
- **Proposal record contract** (minimum): `action`, `status`, `timestamp` (UTC ISO-8601 with trailing `Z`), plus action payload (`files` | `message` | `branch`).
- **Validation error contract** (deterministic):
  - Missing `message` for `commit` -> stable parameter-required error naming `message`.
  - Missing `branch` for `push|branch` -> stable parameter-required error naming `branch`.
- **Persistence contract**: append-only behavior forbids in-place edits/removals of prior entries in this scope.

### Security and Operability Review
- **Data exposure**: proposal payload must not include secrets/tokens; reject or redact sensitive values in logged telemetry context.
- **Auth boundary**: no new authentication/authorization surface is introduced by this design; it inherits existing MCP trust boundary.
- **Failure isolation**: persistence failure must be hard-fail with no success response to prevent false audit confidence.
- **On-call signals**: emit structured outcome categories for `missing_message`, `missing_branch`, `workitem_not_found`, `persistence_failure`.

### Explicit Questions to Project Owner (Default Behaviors)
1. Should `status` default remain a single creation value for now, or must we reserve an enum contract now for future approval linkage?
2. Should missing optional payload fields serialize as omitted keys (preferred) or explicit `null` values for audit export compatibility?
3. Should timestamp generation be strictly UTC from server clock only, with no client-supplied override accepted?

### Architect Disposition
- **Disposition**: Approved with constraints above; no architectural escalation required.
- **Scope change**: None proposed in this role pass; no new user story created.
