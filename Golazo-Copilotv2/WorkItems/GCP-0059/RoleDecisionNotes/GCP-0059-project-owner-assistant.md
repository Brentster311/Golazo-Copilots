# GCP-0059 — Project Owner Assistant Decision Notes

## Request captured
"When bootstrapping, the spine file must be saved at `.github/agents/golazo-copilot/orchestrator.md`. Roles if copied must be under `.github/agents/golazo-copilot/roles/...`."

## Scope decisions
- Kept scope to one user-observable outcome: bootstrap artifact destination/naming structure.
- Excluded unrelated bootstrap behavior and role content changes to keep the story shippable and testable as a single vertical slice.
- Did not create closure artifact in this stage per instruction.

## Assumptions (explicit)
- Interface type assumed to be MCP bootstrap tool behavior (no separate UI redesign requested).
- Platform assumed cross-platform compatibility with Windows as immediate validation environment.
- Persistence assumed file-system workspace outputs (no DB/cloud persistence involved).

## Requirements clarified as explicit contracts
- Spine output path is required to be exactly `.github/agents/golazo-copilot/orchestrator.md`.
- Copied roles output path is required to be exactly `.github/agents/golazo-copilot/roles/...`.
- Any legacy spine or roles paths are non-compliant for this work item.

## Acceptance criteria design rationale
- Criteria target path correctness, regression safety, option compatibility, and docs parity.
- Limited to 5 testable bullets to satisfy role constraints while covering functional and release-readiness checks.

## Risks noted for downstream roles
- Legacy filename/path expectations in tests/docs may require explicit handling across case-insensitive vs case-sensitive filesystems.
- Existing tests or docs may reference old spine location and require synchronized updates.
