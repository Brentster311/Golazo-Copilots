# GCP-0061 — Domain Expert Decision Notes

## Domain Assessment
- Domain expertise required: **Yes**.
- Reason: This refactor is internal tooling, but it has high contract-preservation risk across MCP registration/dispatch behavior, deterministic validation/error semantics, and operational latency expectations.
- Trigger categories hit:
  - **Integration/Architecture domain**: API/service contract stability during routing/handler decomposition
  - **Engineering domain**: modular extraction with behavior parity and deterministic failure semantics
  - **Application/Solution domain**: maintainability/onboarding outcomes and extension-point clarity for maintainers

## Domain Experts Consulted (Assumed)
1. **MCP API Contract & Compatibility Expert**
   - Focus: preservation of tool names, required parameters, and success/error shape invariants.
2. **Python Modular Architecture & Refactor Safety Expert**
   - Focus: extraction sequencing, boundary cohesion, and low-blast-radius modularization.
3. **Performance/Operability Expert**
   - Focus: dispatch-path latency guardrails, observability categories, and rollback triggers.

## Specific Guidance (Risk-Prioritized)
1. **Contract parity is a release gate, not a best effort**
   - Preserve exact registered tool names and required-parameter semantics during registration-map extraction.
   - Keep deterministic validation/error intent stable for missing/invalid parameters (same condition -> same category and message intent).
2. **Make `server.py` orchestration-only with explicit boundaries**
   - Keep bootstrap/wiring in `server.py`; move route selection, handler execution, and response shaping into dedicated modules.
   - Avoid cross-layer utility leaks (e.g., handlers formatting raw responses directly) to prevent drift.
3. **Enforce stable dispatch-table composition**
   - Centralize registration source-of-truth in one module and assert parity against current registered tool set.
   - Treat missing/renamed registration entries as blocking defects.
4. **Preserve operational determinism while extracting**
   - Keep error normalization centralized so failure categories remain consistent across handlers.
   - Use staged extraction (formatters -> handlers -> registration -> thin server orchestration) to isolate regressions.
5. **No measurable latency regression expectation must be testable**
   - Add a lightweight timing smoke check or bounded operation-count proxy on representative calls.
   - Roll back if latency increases materially or dispatch failure profile changes.

## Risks / Constraints Identified
- **Behavior drift risk**: subtle changes in validation order or error shaping during module extraction.
- **Registration mismatch risk**: renamed/missing tool entries after wiring moves.
- **Indirection overhead risk**: additional call layers increase dispatch latency.
- **Reviewability risk**: oversized refactor slice reduces confidence and rollback precision.

## Suggested Design Modifications (Within Scope)
1. In design text, explicitly require a registration parity check that asserts exact tool-name set and required-parameter invariants.
2. In test strategy text, explicitly call out deterministic error-category parity checks for invalid/missing parameter paths.
3. In observability text, standardize dispatch outcome categories (e.g., `success`, `validation_error`, `handler_error`, `tool_not_found`) for pre/post comparison.
4. In rollout text, define a measurable rollback trigger for latency/regression profile deltas, not only explicit contract breakage.

## Escalation and Conflict Check
- No fundamental design flaw requiring return to Program Manager.
- No mandatory new user story required for current scope.
- No blocking conflict with the current design; recommendations above tighten parity and operability guardrails.

## Assumptions Documented
- Existing MCP tool names, required parameter semantics, and success/error contract shapes are strict compatibility constraints.
- Domain consultation is documented from repository artifacts without external SMEs; listed experts are role-based consultation assumptions.
- Existing server/workflow regression suites remain the primary parity evidence, with targeted additions only where parity assertions are currently implicit.

## Handoff Notes
- **Architect**: enforce strict module-boundary contracts and centralized error/registration ownership.
- **Developer**: execute staged extraction with parity assertions at each slice boundary.
- **QA**: verify contract parity, deterministic validation/error behavior, registration completeness, and latency smoke guardrails.
- **Documenter**: publish concise extension-point notes for where to register tools and where to implement handlers/formatters.
