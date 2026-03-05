# GCP-0060 — Domain Expert Decision Notes

## Domain Assessment
- Domain expertise required: **Yes**.
- Reason: This work item is internal tooling, but it carries explicit workflow-auditability and policy-verification outcomes, deterministic error contracts, and append-only persistence integrity requirements.
- Trigger categories hit:
  - **Application/Solution domain**: governance/audit traceability expectations
  - **Integration/Architecture domain**: MCP tool contract and state persistence contract behavior
  - **Engineering domain**: deterministic validation and cross-platform state round-trip integrity

## Domain Experts Consulted (Assumed)
1. **Workflow Governance / Auditability Expert**
   - Focus: evidentiary quality of intent records and compliance-readiness of persisted state.
2. **API Contract & State Persistence Expert**
   - Focus: deterministic parameter validation, schema compatibility, and append-only invariants in `state.json`.

## Specific Guidance
1. **Audit evidence quality**
   - Persist proposal timestamps in normalized UTC ISO-8601 format (`...Z`) to avoid cross-environment interpretation drift.
   - Ensure each proposal entry is immutable after append from the `golazo_git_propose` path (no in-place updates for this work item scope).
2. **Deterministic validation contract**
   - Keep action-specific validation failures stable and machine-assertable (same condition -> same error class/message shape).
   - Use explicit parameter-required semantics for `message` (commit) and `branch` (push/branch) without fallback inference.
3. **Backward compatibility and persistence integrity**
   - Apply `git_actions: []` default on load and preserve round-trip compatibility for legacy work items.
   - Treat any persistence failure as a hard failure for the proposal call; avoid ambiguous partial-success responses.
4. **Operational observability alignment**
   - Emit/action-tag outcomes that map directly to the KPIs already defined in story/design (`action`, `validation_rule`, `persist_success|failure`).

## Risks / Constraints Identified
- **Bypass risk**: downstream git operations may occur without a prior proposal; compliance ratio must be observable to detect drift.
- **Serialization drift risk**: timestamp/status shape inconsistency can weaken audit replay quality across environments.
- **Filesystem failure risk**: failed writes can create audit gaps unless failure responses are explicit and non-ambiguous.
- **Legacy compatibility risk**: missing default application for `git_actions` can break older work-item state loads.

## Suggested Design Modifications (Within Scope)
1. In design/data-contract text, explicitly lock timestamp normalization to UTC ISO-8601 with trailing `Z`.
2. In error-contract text, explicitly define deterministic parameter-required failure shape as stable across releases.
3. In persistence semantics text, explicitly state that proposal history is append-only and proposal records are not mutated by this work item.

## Escalation and Conflict Check
- No fundamental design flaw requiring return to Program Manager.
- No mandatory new user story required for current scope.
- No blocking conflict with current design; suggestions above are clarifying refinements to improve audit reliability.

## Handoff Notes
- **Architect**: enforce append-only + deterministic error-contract boundaries in interface/state design.
- **Developer**: implement normalized timestamps and strict validation/persistence failure behavior.
- **QA**: assert deterministic errors, UTC timestamp normalization, append-only history, and legacy-state round-trip compatibility.
