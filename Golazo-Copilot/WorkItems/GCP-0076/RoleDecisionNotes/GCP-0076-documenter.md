# GCP-0076 Documenter Decision Notes

## Review

- Verified README capability-query documentation already identifies `WorkItems/capabilities.yaml` as canonical and root `capabilities.yaml` as migration input only.
- Added `golazo_capabilities` to the MCP tool list.
- Added `WorkItems/capabilities.yaml` to documented full-bootstrap outputs.
- Updated the bootstrap docstring to match the canonical output path.
- Preserved historical changelog entries describing prior root-path behavior.

## Release Boundary

No version or changelog entry was changed. Builder owns release metadata.

## Validation

Bootstrap and canonical-registry tests: 42 passed. Repository-wide Ruff: passed.
