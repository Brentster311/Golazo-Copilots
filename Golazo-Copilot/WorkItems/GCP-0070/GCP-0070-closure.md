# GCP-0070 Closure

## Delivery Summary

- Removed the `golazo_update` MCP tool from the current Golazo Copilot public surface.
- Replaced self-update guidance with explicit manual package installation and upgrade commands in the bootstrap spine and README.
- Bumped the package version from `4.4.0` to `5.0.0` to reflect the breaking tool-surface change.

## Acceptance Criteria Validation

- PASS: The MCP server no longer advertises or dispatches `golazo_update`.
- PASS: Bootstrapped orchestrator instructions now include the correct Azure Artifacts `pip install --upgrade` guidance.
- PASS: Public documentation no longer directs users to a `golazo_update` MCP tool.
- PASS: Regression coverage validates both the removed tool surface and the new install guidance.

## Verification Evidence

- `python -m pytest tests/test_gcp_bootstrap.py tests/test_gcp0061_server_modular_refactor.py tests/test_server_formatters.py tests/test_server_legacy_coverage.py tests/test_gcp0066_documenter_changelog_policy.py` -> `85 passed`
- `python -m pip wheel . --no-deps -w dist-builder-check` -> built `golazo_copilot-5.0.0-py3-none-any.whl`

## Git Status

- Committed on `main` with: `GCP-0070: Remove golazo_update and replace it with spine install guidance`
- Pushed to `origin/main`
- Published commit: `a4036b5`

## Follow-up Items

- Add or restore an orchestrator-facing role transition wrapper.
- Clean up the placeholder capability registry entry that currently fails validation.
- Refresh stale bootstrapped instruction files in a separate maintenance pass.