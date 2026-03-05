# GCP-0065 Design Doc

## Summary
Update Golazo capability discovery so `WorkItems/capabilities.yaml` is the canonical location. If a legacy `capabilities.yaml` is found at repository root (or any non-canonical supported legacy location), the system should move it to `WorkItems/capabilities.yaml`.

## Problem Statement
Repository layout has changed and capability metadata now belongs under `WorkItems/`. Existing logic may still depend on old paths, causing ambiguity, failed lookups, or duplicated files.

## Business Case
- Why now: current and upcoming work items depend on consistent capability discovery.
- Impact: reduces setup friction and avoids manual path fixes.
- KPIs:
  - 100% pass for capability resolution tests with canonical path.
  - 0 manual steps required to relocate legacy capability file for normal workflows.

## Stakeholders
- Golazo maintainers
- Project owners using capability impact analysis
- Contributors running capability-aware workflow commands

## Functional Requirements
- `golazo_capabilities(action="list")` must read from `WorkItems/capabilities.yaml`.
- `golazo_capabilities(action="impact", files=[...])` must use `WorkItems/capabilities.yaml`.
- If legacy `capabilities.yaml` exists outside `WorkItems/` and canonical file is missing, move legacy file to `WorkItems/capabilities.yaml`.
- If both legacy and canonical files exist, canonical file is source of truth and legacy file handling must be explicit (warn and leave untouched, or deterministic overwrite policy documented in code/tests).
- Missing-file errors must clearly state expected canonical path.

## Non-Functional Requirements
- Cross-platform path handling (Windows/Linux/macOS).
- Deterministic behavior with test coverage for move and conflict scenarios.
- No measurable latency regression for typical repo scans.

## Proposed Approach
- Centralize capability file resolution in a single helper used by `list`, `show`, `impact`, and `validate` operations.
- Add migration logic:
  - Check canonical path first.
  - If absent, check legacy path(s).
  - If found, ensure `WorkItems/` exists and move file to canonical path.
  - Return canonical path to callers.
- Add conflict-handling branch for canonical+legacy coexistence.
- Update user-facing error messages and tests.

## Alternatives Considered
- Keep dual-path reads forever: rejected due to ambiguity and technical debt.
- Fail fast when file is not canonical: rejected due to poor backward compatibility.

## Risks, Mitigations, Open Questions
- Risk: accidental overwrite during move if canonical file appears concurrently.
  - Mitigation: guard move with existence checks and deterministic conflict policy.
- Risk: filesystem permission errors during move.
  - Mitigation: return actionable error including source and target paths.
- Open question: when both files exist, should legacy file be retained with warning or auto-removed?
  - Interim decision: retain legacy file and log warning unless overwrite policy already exists.

## Dependencies
- Existing capability parsing utilities
- File operations module used by MCP tools
- Unit/integration test framework

## Migration / Rollout / Rollback Plan
- Migration: automatic move on first command invocation that resolves capabilities.
- Rollout: merge with tests covering canonical, legacy-only, and dual-file scenarios.
- Rollback: revert resolver/move logic and tests if regressions occur.

## Observability Plan
- Include clear logs or error messages for:
  - migration performed
  - migration skipped due to canonical existing
  - migration failure with reason

## Test Strategy Summary
- Unit tests for resolver and migration logic.
- Integration tests for `golazo_capabilities` actions against temporary workspace layouts:
  - canonical only
  - legacy only (assert move)
  - both present (assert deterministic behavior)
  - none present (assert error text)
