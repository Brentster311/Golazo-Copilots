# GCP-0066 Architect Notes

## Architecture Decision
Approve policy-focused implementation via role instruction updates and tests.

## Key Constraints
- Version source remains `pyproject.toml`.
- Changelog remains maintained at end of `golazo-copilot/README.md`.
- Sequence must be explicit: version update before changelog maintenance.

## Capability Impact Summary
`golazo_capabilities(action="impact")` reported no affected capabilities for planned files.

## Operability Notes
Prefer semantic assertion tests over brittle exact-text assertions.
