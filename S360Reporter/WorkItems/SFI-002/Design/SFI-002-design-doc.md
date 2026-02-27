# SFI-002 Design Document: accia-s360 Package

## Summary
Refactor the existing `s360_client` code into a properly packaged Python library named `accia-s360` that can be published to Azure Artifacts and consumed by other projects.

## Problem Statement
The current s360_client code exists only within this repository. Other projects (like S360Reporter) cannot easily consume it without copying files, which leads to:
- Code duplication across projects
- Version inconsistencies
- No clear dependency management
- Difficult updates and bug fixes

## Business Case

### Why Now
- SFI-003 (S360Reporter) requires s360_client as a dependency
- Team needs to share S360 API access across multiple tools
- Proper packaging enables versioning and controlled releases

### Impact
- Enables code reuse across ACCIA projects
- Establishes pattern for future internal packages
- Reduces maintenance burden

### KPIs
- Package successfully installable via pip
- Zero breaking changes to existing functionality
- All existing tests pass

## Stakeholders
- **Owner:** Brent Jensen
- **Consumers:** ACCIA team members, future projects

## Functional Requirements
1. Package exposes `S360Client` class as primary interface
2. Package exposes all existing endpoint methods
3. Package handles authentication via Azure CLI credentials
4. Package provides caching functionality

## Non-Functional Requirements
1. Package size < 500KB
2. Python 3.10+ compatibility
3. Type hints for IDE support
4. No vendored dependencies

## Proposed Approach

### Package Structure
```
accia-s360/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── accia_s360/
│       ├── __init__.py          # Public API exports
│       ├── client.py            # S360Client class
│       ├── auth.py              # Authentication
│       ├── cache.py             # Caching logic
│       ├── models.py            # Data models (if any)
│       └── endpoints/
│           ├── __init__.py
│           ├── base.py          # Base endpoint class
│           └── extended.py      # All endpoint implementations
└── tests/
    └── ...                      # Existing tests, adjusted imports
```

### Key Changes
1. **Rename package:** `s360_client` → `accia_s360` (underscore for Python import)
2. **Create pyproject.toml:** Modern packaging with build system
3. **Update imports:** All internal imports use new package name
4. **Public API:** Export only intended public classes/functions

### pyproject.toml Structure
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "accia-s360"
version = "0.1.0"
description = "Python client for Microsoft S360 API"
requires-python = ">=3.10"
dependencies = [
    "azure-identity>=1.15.0",
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "pytest-cov"]
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Keep code in-repo, copy to other projects | Simple | Duplication, version drift | Rejected |
| Git submodule | No packaging needed | Complex for consumers | Rejected |
| Azure Artifacts package | Clean pip install, versioning | Initial setup effort | **Selected** |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Import path changes break existing scripts | Medium | Medium | Update all imports in this repo before release |
| Azure Artifacts access issues | Low | High | Document feed URL and permissions |
| Missing dependencies | Low | Medium | Test pip install in clean environment |

## Open Questions
1. Azure Artifacts feed name? (Assumption: will use existing ACCIA feed or create one)
2. Should we include example scripts in the package? (Recommendation: No, keep package minimal)

## Dependencies
- Azure Artifacts feed access
- Azure CLI for authentication testing

## Migration / Rollout Plan

### Phase 1: Restructure (This Work Item)
1. Create new package structure in separate directory
2. Copy and refactor code
3. Update imports
4. Run tests
5. Build package locally

### Phase 2: Publish (Manual)
1. Configure Azure Artifacts credentials
2. Publish package: `twine upload --repository accia dist/*`
3. Test installation in clean environment

### Phase 3: Consume
1. SFI-003 adds `accia-s360` as dependency
2. Deprecate old s360_client directory

## Rollback Plan
- If package has issues, consumers can pin to specific version
- Source code remains in this repo as reference

## Observability Plan
- N/A for library package (no runtime telemetry)

## Test Strategy Summary
1. **Unit tests:** Existing tests adapted to new import paths
2. **Integration tests:** Verify package installs and imports correctly
3. **Smoke test:** Create simple script that uses installed package
