# SFI-002: Package s360_client as accia-s360 for Azure Artifacts

**Status**: IMPLEMENTED

## User Story

- **Title:** Package s360_client as accia-s360 for Azure Artifacts
- **As a:** Developer consuming the S360 API
- **I want:** A properly packaged Python library (accia-s360) published to Azure Artifacts
- **So that:** I can install it via pip and use it in other projects without copying code

## Out of Scope
- New API endpoints (use existing functionality)
- Breaking changes to the public API
- Documentation website
- CI/CD pipeline (future work item)

## Assumptions
- **Assumption (explicit):** Target Python 3.10+ (matches current development environment)
- **Assumption (explicit):** Use pyproject.toml for modern packaging (PEP 517/518)
- **Assumption (explicit):** Azure Artifacts feed already exists or will be created manually
- **Assumption (explicit):** Package will use semantic versioning starting at 0.1.0

## Acceptance Criteria
- [ ] Package structure follows Python packaging best practices (src layout)
- [ ] `pyproject.toml` defines package metadata, dependencies, and build system
- [ ] Package can be built locally with `python -m build`
- [ ] Package can be installed via `pip install accia-s360` from Azure Artifacts
- [ ] All existing tests pass after refactoring
- [ ] Public API is exposed via `from accia_s360 import S360Client`

## Non-Functional Requirements
- Package size < 500KB (excluding dependencies)
- No vendored dependencies (all via pip)
- Type hints preserved for IDE support

## Telemetry / Metrics Expected
- None for library package

## Rollout / Rollback Notes
- Initial release: 0.1.0
- Breaking changes require major version bump
- Rollback: Consumers can pin to previous version
