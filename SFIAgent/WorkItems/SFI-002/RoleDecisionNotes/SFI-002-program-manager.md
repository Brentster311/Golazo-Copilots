# SFI-002 Program Manager Notes

## Design Decisions

### Package Name
- **PyPI name:** `accia-s360` (with hyphen, user specified)
- **Import name:** `accia_s360` (with underscore, Python convention)

### Build System
Selected **hatchling** as build backend because:
- Modern and well-maintained
- Simple configuration
- Good defaults for src-layout

### Directory Structure
Selected **src-layout** because:
- Prevents accidental imports from source during testing
- Industry best practice for packages
- Clear separation of package code from project files

### Version Strategy
- Starting at **0.1.0** (pre-1.0 indicates API may change)
- Semantic versioning for all releases
- Breaking changes require major version bump after 1.0

## Scope Boundaries
- **In scope:** Code restructuring, packaging, local build
- **Out of scope:** CI/CD automation, documentation site

## Dependencies Identified
- SFI-003 depends on this work item
- Azure Artifacts feed must exist (manual setup)

## Risk Assessment
- Low risk overall - this is a restructuring, not new functionality
- Main risk is import path changes breaking existing scripts

## Recommendations for QA
1. Verify all existing tests pass with new imports
2. Test pip install in clean virtual environment
3. Verify public API matches documentation
