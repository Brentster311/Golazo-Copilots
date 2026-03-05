# GCP-0059 — Program Manager Decision Notes

## Decisions
1. Standardize bootstrap-generated artifacts under `.github/agents`.
2. Set spine artifact path and filename to exact literal `.github/agents/golazo-copilot/orchestrator.md`.
3. Set copied roles destination to concrete subfolder `.github/agents/golazo-copilot/roles/...` when role copy is enabled.
4. Preserve bootstrap option compatibility, including role-copy toggle behavior.
5. Require implementation, tests, and documentation to be updated in one coordinated change.

## Assumptions Applied
- Bootstrap is invoked through MCP tooling; no separate UI workflow change is required.
- Workspace file-system persistence remains the canonical storage mechanism.
- Cross-platform path handling remains required, with Windows as immediate validation context.
- Historical outputs are not retroactively moved; behavior applies to new/rerun bootstrap executions.

## Requirement Clarification Incorporated
- Roles folder location is moved to the explicit path `.github/agents/golazo-copilot/roles/...`.
- Spine output is required to be the explicit path `.github/agents/golazo-copilot/orchestrator.md`.

## Rationale
- Centralized output tree reduces ambiguity and improves discoverability.
- Explicit path contracts reduce implementation/test drift.
- Maintaining existing option semantics minimizes regression risk.

## Rejected Options
- Keeping roles under legacy `.github/roles`.
- Copying roles directly under `.github/agents` or `.github/agents/golazo-copilot` without `roles` subfolder.
- Changing spine filename away from `orchestrator.md` or changing its parent folder away from `.github/agents/golazo-copilot`.

## Risks & Mitigations
- Risk: stale docs/tests referencing old locations.
  - Mitigation: update docs and tests in same release unit.
- Risk: filename/path casing assumptions across filesystems.
  - Mitigation: use exact literal path assertions in tests.
- Risk: user confusion from legacy artifacts still present.
  - Mitigation: communicate migration behavior and expected new outputs in release notes.

## Handoff Notes
- Architect: validate path-resolution design boundaries and failure mode handling.
- Developer: implement scoped changes for path constants/helpers and preserve existing option behavior.
- QA: verify spine path, roles subfolder path, toggle behavior, and docs parity.
