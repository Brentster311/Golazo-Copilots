# GCP-0067 Design Doc

## Summary
Clarify and enforce the contract between `golazo_status` and `golazo_update` so users can reliably understand status information and deterministically choose update install target behavior.

## Problem Statement
Users can confuse `golazo_status` (inspection/reporting) with `golazo_update` (state-changing install action), and update target behavior can be unclear when different Python environments are present. This ambiguity risks unintended installations and trust erosion.

## Business Case
- Why now: recent usage exposed confusion between status output and update behavior, including uncertainty about global vs environment-scoped installs.
- Impact: reduces operator errors, improves user confidence, and lowers support/debug time.
- KPIs:
  - 0 ambiguous status/update descriptions in tool metadata and docs.
  - 100% of update executions emit explicit target confirmation.
  - Regression tests cover both success and at least one error path for target selection.

## Stakeholders
- Golazo Copilot users (developers/operators)
- Golazo maintainers
- Release/package maintainers

## Functional Requirements
- `golazo_status` descriptions/output must clearly indicate read-only reporting semantics.
- `golazo_update` descriptions/output must clearly indicate update/install semantics.
- `golazo_update` must support deterministic target selection behavior with safe defaults (for example: active interpreter/environment default plus explicit global/system option).
- Update execution must emit clear confirmation of selected target and effective command path.
- Backward compatibility must be preserved for existing calls that do not pass new target fields.

## Non-Functional Requirements
- Messages are concise, explicit, and actionable.
- No destructive behavior when no update is available.
- Cross-platform compatibility for command construction and invocation.

## Proposed Approach
- Update MCP tool descriptions in server registration/dispatch docs to remove semantic overlap.
- Extend `golazo_update` argument schema to include explicit target selection (enumerated values) and clear defaults.
- Implement/update update execution logic so selected target controls command construction deterministically.
- Improve `golazo_update` result payload text to include target and action summary.
- Add/adjust tests for:
  - status/update descriptive clarity
  - default target behavior
  - explicit target behavior
  - invalid/unsupported target error handling
- Update README tool documentation and changelog entry accordingly.

## Alternatives Considered
- Documentation-only fix without behavior changes: rejected because runtime ambiguity remains.
- Force only one install target: rejected because users need explicit control across environments.

## Risks, Mitigations, Open Questions
- Risk: target semantics differ across CI/dev/local shells.
  - Mitigation: centralize target-to-command resolution and test representative scenarios.
- Risk: backward compatibility breaks for older callers.
  - Mitigation: keep default behavior equivalent to current interpreter-scoped update unless explicit target is requested.
- Open question: naming of target options (`active`, `global`) may need harmonization with existing user language.

## Dependencies
- `golazo_update` tool implementation and argument schema
- MCP server tool registration text (`server.py`, dispatch registry/formatter surfaces)
- Existing test suites covering update/status behavior
- README documentation/changelog process

## Migration / Rollout / Rollback Plan
- Rollout: ship schema, implementation, tests, and docs together in one release.
- Migration: no data migration; behavior defaults preserve existing callers.
- Rollback: revert target-selection code and schema fields; keep prior single-path update behavior.

## Observability Plan
- Include explicit `target` and action summary in update responses for easier troubleshooting.
- Ensure test failures identify whether issue is schema validation, command resolution, or result formatting.

## Test Strategy Summary
- Unit tests for target parsing and command resolution.
- Integration-style tests for update action flow with mocked installers/HTTP checks.
- Regression tests for status text and backward-compatible update calls.
