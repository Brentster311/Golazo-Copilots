# GCP-009: Design Document

## Summary
Update the Golazo spine to include explicit Project Root definition rules that work across Visual Studio and VS Code, eliminating the ambiguous `<ProjectName>` token.

## Problem Statement
Copilot frequently creates Golazo artifacts (WorkItems, role documents) in incorrect locations because:
1. The `<ProjectName>` token is ambiguous and Copilot interprets it inconsistently
2. No clear distinction between "Repo Root" and "Project Root"
3. No IDE-specific guidance for determining where artifacts should go

This causes friction as users must manually move files or correct Copilot.

## Business Case

### Why Now
- Multiple work items (GCP-001 through GCP-008) have encountered this issue
- Each correction wastes time and breaks flow
- Foundation work — fixing this improves all future work items

### Impact
- **Positive**: Copilot creates files correctly on first attempt
- **Positive**: Reduced user frustration and corrections
- **Positive**: Clearer documentation for new Golazo adopters

### KPIs
- Zero file location corrections needed per work item (target)
- Copilot self-identifies correct Project Root without user intervention

## Stakeholders
| Role | Interest |
|------|----------|
| Developers (VS) | Artifacts appear next to their project file |
| Developers (VS Code) | Artifacts appear in expected workspace location |
| Golazo maintainers | Fewer support questions about file paths |

## Functional Requirements

### FR-1: Project Root Definition Section
Add new section to spine with:
- Definition of Project Root
- Definition of Repo Root
- Clear distinction between the two

### FR-2: IDE-Specific Rules
| IDE | Rule |
|-----|------|
| Visual Studio | Project Root = directory containing active project file (`.csproj`, `.pyproj`, `.fsproj`, `.vbproj`, `.vcxproj`) |
| VS Code | Project Root = directory containing project manifest (see list below) |

**VS Code Project Manifests** (in priority order):
1. `package.json` (Node.js/JavaScript)
2. `pyproject.toml` or `setup.py` (Python)
3. `Cargo.toml` (Rust)
4. `go.mod` (Go)
5. `pom.xml` or `build.gradle` (Java)
6. `*.csproj` or `*.sln` (C#/.NET)
7. `Makefile` (C/C++/general)

### FR-3: VS Code Fallback with Confirmation
If no manifest found:
1. Propose workspace folder as Project Root
2. **Ask Project Owner to confirm** before creating any artifacts
3. Document the confirmed location for session

### FR-4: Remove `<ProjectName>` Token
- Search and replace all instances in spine
- Replace with clear relative path examples

### FR-5: Path Examples
Include explicit correct/incorrect examples:
```
? Correct: WorkItems/GCP-009/GCP-009-User-Story.md
? Wrong:   Golazo-Copilot/WorkItems/GCP-009/GCP-009-User-Story.md
? Wrong:   <ProjectName>/WorkItems/GCP-009/GCP-009-User-Story.md
? Wrong:   C:\Users\...\WorkItems\GCP-009\GCP-009-User-Story.md
```

## Non-Functional Requirements

- Rules must be deterministic (same input = same output)
- Documentation must be scannable (tables, bullets)
- Self-correction guidance if Copilot starts in wrong directory

## Proposed Approach

### Phase 1: Add Project Root Definition Section
Insert after "Role instruction loading rule" section:
```markdown
## Project Root Definition (IMPORTANT)

**Project Root** is where Golazo artifacts (WorkItems, tests, etc.) are created.

### How to Determine Project Root

| IDE | Project Root Location |
|-----|----------------------|
| **Visual Studio** | Directory containing the active project file (`.csproj`, `.pyproj`, `.fsproj`, `.vbproj`, `.vcxproj`) |
| **VS Code** | Directory containing a project manifest file (see list below) |

**VS Code Project Manifests** (check in order):
- `package.json`, `pyproject.toml`, `setup.py`, `Cargo.toml`
- `go.mod`, `pom.xml`, `build.gradle`, `*.csproj`, `*.sln`, `Makefile`

**VS Code Fallback**: If no manifest is found, ask the Project Owner:
> "I couldn't find a project manifest file. Is the workspace folder `<path>` the correct Project Root for Golazo artifacts?"

### Project Root vs Repo Root

| Term | Definition | Contains |
|------|------------|----------|
| **Repo Root** | Git repository root | `.git/`, `.github/copilot-instructions.md` |
| **Project Root** | User's project directory | Project file, `WorkItems/`, source code |

These may be the same directory (single-project repo) or different (multi-project repo, monorepo).
```

### Phase 2: Update Artifact Paths Section
Replace current paths using `<ProjectName>` with:
```markdown
### Artifact Paths (relative to Project Root)

- User Stories: `WorkItems/<workitem-id>/<workitem-id>-User-Story.md`
- Design Docs: `WorkItems/<workitem-id>/Design/<workitem-id>-Design-Doc.md`
- Review Comments: `WorkItems/<workitem-id>/Design/<workitem-id>-Review-Comments.md`
- Test Cases: `WorkItems/<workitem-id>/Design/<workitem-id>-Test-Cases.md`
- Role Notes: `WorkItems/<workitem-id>/RoleDecisionNotes/<workitem-id>-<role>.md`
```

### Phase 3: Add Self-Correction Guidance
```markdown
### Before Creating Files

1. Identify Project Root using the rules above
2. Verify your working directory matches Project Root
3. If unsure, ask: "Is `<current directory>` the Project Root?"

**If you created files in the wrong location**: Stop, acknowledge the error, and help the user move the files to the correct Project Root.
```

## Alternatives Considered

| Alternative | Evaluation | Decision |
|-------------|------------|----------|
| Keep `<ProjectName>` token | Continues to cause confusion | Rejected |
| Always use Repo Root | Breaks multi-project repos | Rejected |
| Marker file (`.golazo-project`) | Extra setup for users | Rejected |
| Only support Visual Studio | Excludes VS Code users | Rejected |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Copilot still misinterprets | Low | Medium | Explicit examples, self-correction guidance |
| Unusual project structures | Low | Low | Fallback requires confirmation |
| Breaking existing repos | Low | Medium | Paths are more explicit, not fundamentally changed |

## Dependencies
- None. Documentation-only change.

## Migration / Rollout Plan

### Rollout
1. Update spine with new section
2. Remove all `<ProjectName>` tokens
3. Update VERSION to 1.1.2
4. Update CHANGELOG
5. Single commit, push to branch, PR to main

### Rollback
- Revert commit if issues found
- No data migration needed

## Test Strategy Summary
1. Verify spine contains new "Project Root Definition" section
2. Verify no `<ProjectName>` tokens remain in spine
3. Verify path examples are correct
4. Manual test: Start new work item, verify Copilot creates files in Project Root
