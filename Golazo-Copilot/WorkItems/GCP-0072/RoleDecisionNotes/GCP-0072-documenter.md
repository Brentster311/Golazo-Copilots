# GCP-0072 Documenter Decision Notes

## Documentation Updates

- Defined release version `5.1.0` in `pyproject.toml` before changelog maintenance.
- Updated the bootstrap walkthrough with the ADO Sync installation request, confirmation flow, supported scope destinations, overwrite behavior, and full-mode restriction.
- Updated the `golazo_bootstrap` API table with the three additive inputs and exact defaults.
- Clarified User scope behavior for orchestrator instructions and requested skill installation.
- Updated canonical bootstrap instructions to require displaying all schema defaults and obtaining explicit confirmation before installation.
- Added the `v5.1.0` changelog entry at the top of the versioned changelog.

## Accuracy Review

- Workspace destination matches implementation: `.github/skills/golazo-ado-sync/`.
- User destination matches implementation: `~/.copilot/skills/golazo-ado-sync/`.
- Documentation correctly states that installation is opt-in and limited to full mode.
- Documentation correctly describes partial overrides, validation, force/no-force behavior, and structured outcomes.
- No claims of Azure DevOps connectivity, authentication, or live board validation during bootstrap were added.
- No new documentation links were introduced, so there are no new link targets to validate.

## Release Rationale

`5.1.0` is a backward-compatible minor release because it adds optional public MCP inputs and a new bootstrap capability while preserving existing defaults and behavior.

## Validation

`py -3.14 -m pytest tests/test_gcp0066_documenter_changelog_policy.py tests/test_package_init_version.py tests/test_gcp_bootstrap.py tests/test_gcp0072_skill_bootstrap.py -q`

- Result: `56 passed`.