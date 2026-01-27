# GCP-009: Clarify Project Root Definition for Cross-IDE Compatibility

**Status**: IMPLEMENTED

## User Story

- **Title**: Clarify Project Root definition to eliminate artifact path confusion
- **As a**: Developer using Golazo with GitHub Copilot
- **I want**: Clear, unambiguous rules for determining Project Root in both Visual Studio and VS Code
- **So that**: Copilot creates workflow artifacts (WorkItems, role documents) in the correct location every time

## Out of Scope

- Changing the artifact folder structure (WorkItems/<id>/...)
- Modifying role responsibilities
- Changing DoR/DoD gates
- Supporting IDEs other than Visual Studio and VS Code

## Assumptions

- **Assumption (explicit)**: Visual Studio users always have a project file (.csproj, .pyproj, .fsproj, .vbproj, etc.)
- **Assumption (explicit)**: VS Code users typically have a project manifest file, but may not always
- **Assumption (explicit)**: The `<ProjectName>` token in current instructions is the source of confusion and should be removed

## Acceptance Criteria (bulleted, testable)

- [ ] Spine contains a "Project Root Definition" section with explicit rules
- [ ] Visual Studio rule: Project Root = directory containing the active project file (`.csproj`, `.pyproj`, `.fsproj`, `.vbproj`, etc.)
- [ ] VS Code rule: Project Root = directory containing a project manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `*.csproj`, `Makefile`)
- [ ] VS Code fallback: If no manifest found, use workspace folder AND confirm with Project Owner before creating artifacts
- [ ] All `<ProjectName>` tokens removed from spine and replaced with explicit relative paths
- [ ] Artifact path examples show correct vs incorrect paths
- [ ] Distinction between "Repo Root" and "Project Root" is clearly documented

## Non-functional Requirements

- Rules must be unambiguous (no interpretation needed)
- Rules must work for both single-project and multi-project repositories
- Instructions should help Copilot self-correct if it starts in wrong directory

## Telemetry / Metrics Expected

- Manual verification: Copilot creates files in correct location on first attempt
- Reduced need for user to correct file paths

## Rollout / Rollback Notes

- **Rollout**: Update spine in single commit; version bump to 1.1.2
- **Rollback**: Revert commit if issues found
- **Impact**: Existing repos using `<ProjectName>` pattern may need path adjustments
