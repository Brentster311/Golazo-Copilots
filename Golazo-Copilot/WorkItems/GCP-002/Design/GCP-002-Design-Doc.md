# GCP-002: Design Document

## Summary
Create a Python CLI tool (`Golazo_Copilot.py`) that installs the Golazo workflow instructions into any git repository, plus comprehensive documentation (`README.md`) explaining the workflow, roles, artifacts, and usage.

## Problem Statement
Developers who want to adopt the Golazo workflow in their projects currently have no easy way to:
1. Install the necessary instruction files (`.github/copilot-instructions.md` and role files)
2. Understand what Golazo is, how it works, or why they should use it

This creates a barrier to adoption and leaves users without guidance on the workflow's benefits and proper usage.

## Business Case

### Why Now
- GCP-001 established the foundational Golazo files in this repository
- Without tooling and documentation, these files remain inaccessible to other projects
- Developer productivity gains from Golazo are unrealized without adoption mechanisms

### Impact
- **Positive**: Any developer can adopt Golazo in <1 minute with a single command
- **Positive**: README provides self-service onboarding, reducing questions/confusion
- **Measurable**: Track repository clones/forks as adoption proxy

### KPIs
- Time to install Golazo: Target <30 seconds
- README comprehensiveness: All 10 roles documented
- Cross-platform compatibility: Works on Windows, macOS, Linux

## Stakeholders
- **Primary**: Developers adopting Golazo in new/existing repositories
- **Secondary**: Repository maintainers managing Golazo instructions
- **Tertiary**: Teams evaluating structured AI-assisted development workflows

## Functional Requirements

### CLI Tool (`Golazo_Copilot.py`)
| ID | Requirement |
|----|-------------|
| F1 | Find git repository root by traversing up from current directory |
| F2 | Create `.github/` directory if it doesn't exist |
| F3 | Copy `copilot-instructions.md` to target `.github/` |
| F4 | Create `.github/roles/` directory if it doesn't exist |
| F5 | Copy all 10 role files to target `.github/roles/` |
| F6 | Print success message with list of created/updated files |
| F7 | Print error message if not in a git repository |
| F8 | Handle file permission errors gracefully |

### README Documentation
| ID | Requirement |
|----|-------------|
| D1 | Explain what Golazo is (elevator pitch) |
| D2 | List benefits of using Golazo |
| D3 | Document each of the 10 roles with purpose summary |
| D4 | Explain the artifact structure (`WorkItems/<id>/...`) |
| D5 | Provide Retrospective role usage example |
| D6 | Include quick-start installation instructions |

## Non-Functional Requirements
| ID | Requirement |
|----|-------------|
| NF1 | Python 3.7+ compatibility |
| NF2 | Zero external dependencies (standard library only) |
| NF3 | Cross-platform (Windows, macOS, Linux) |
| NF4 | UTF-8 file encoding throughout |
| NF5 | Graceful error handling (no stack traces for users) |

## Proposed Approach

### CLI Architecture
```
Golazo_Copilot.py
??? find_repo_root()      # Walk up directories looking for .git/
??? get_source_path()     # Get path to .github/ in script's directory
??? ensure_directory()    # Create directory if missing
??? copy_file()           # Copy single file with error handling
??? install_golazo()      # Main orchestration function
??? main()                # Entry point with argument parsing
```

### Algorithm: Find Repository Root
```python
def find_repo_root(start_path):
    current = start_path
    while current != parent(current):  # Not at filesystem root
        if exists(current / ".git"):
            return current
        current = parent(current)
    return None  # Not in a git repo
```

### File Copy Strategy
1. Determine source directory (where `Golazo_Copilot.py` lives)
2. Determine target directory (git repo root)
3. Copy spine file: `source/.github/copilot-instructions.md` ? `target/.github/copilot-instructions.md`
4. Copy role files: `source/.github/roles/*.md` ? `target/.github/roles/*.md`

### README Structure
```markdown
# Golazo Copilot
## What is Golazo?
## Benefits
## The 10 Roles
## Artifact Structure
## Quick Start
## Using the Retrospective Role (Example)
## License
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Shell script installer | Simpler for Unix | Not cross-platform | Rejected |
| Download from URL | Always latest | Requires network | Rejected |
| Git submodule | Standard git workflow | Complex for users | Rejected |
| Package manager (pip) | Professional distribution | Overkill for v1 | Future work |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User runs from wrong directory | Medium | Low | Clear error message pointing to git repo requirement |
| Overwrites customized files | Medium | Medium | Document behavior; future: add `--backup` flag |
| Python not installed | Low | High | Document Python requirement in README |
| Permission denied on target | Low | Medium | Catch exception, print helpful message |

## Open Questions
*None — all fundamental questions resolved in User Story.*

## Dependencies
- GCP-001 must be complete (provides source instruction files) ?

## Migration / Rollout / Rollback Plan

### Rollout
1. Merge to main branch
2. Users clone repo and run `python Golazo_Copilot.py` in their target project

### Rollback
- Revert commit
- Users who installed can manually delete `.github/copilot-instructions.md` and `.github/roles/`

## Observability Plan
- CLI prints all actions to stdout
- Exit code 0 on success, 1 on failure
- No telemetry or logging to external systems

## Test Strategy Summary
- Unit tests for `find_repo_root()` with mock filesystem
- Integration test: run CLI in temp git repo, verify files created
- Edge case tests: no git repo, permission errors, existing files
- Manual cross-platform verification
