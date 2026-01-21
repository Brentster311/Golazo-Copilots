# GCP-002: Golazo CLI Tool and README Documentation

**Status**: IMPLEMENTED

## User Story

- **Title**: Create Golazo CLI Installer and Comprehensive README
- **As a**: Developer wanting to use the Golazo workflow in their repository
- **I want**: A CLI tool that installs/updates Golazo instructions in any repo, plus a README explaining how Golazo works
- **So that**: I can easily adopt Golazo in new projects and understand the workflow, roles, artifacts, and how to use them effectively

## Out of Scope
- GUI interface
- Web-based installer
- Package distribution (PyPI, npm, etc.) — future work
- Automated CI/CD integration
- Version management of instructions across repos

## Assumptions
- **Assumption (explicit)**: CLI will be Python-based (matching existing `Golazo_Copilot.py`)
- **Assumption (explicit)**: Git repository detection via `.git` folder traversal is acceptable
- **Assumption (explicit)**: The tool will copy instruction files from a bundled/embedded source (the files in `.github/` of this repo)
- **Assumption (explicit)**: README will be placed at the repository root level

## Acceptance Criteria (bulleted, testable)
- [x] Running `python Golazo_Copilot.py` from any directory within a git repo finds the repo root
- [x] The CLI creates/updates `.github/copilot-instructions.md` in the target repo
- [x] The CLI creates/updates all 10 role files in `.github/roles/`
- [x] The CLI prints success/failure messages to stdout
- [x] `README.md` exists at repo root with Golazo overview
- [x] README explains each of the 10 roles and their purpose
- [x] README documents the artifact structure (`WorkItems/<id>/...`)
- [x] README includes a Retrospective usage example

## Non-functional Requirements
- CLI must work on Windows, macOS, and Linux
- CLI must use only Python standard library (no external dependencies)
- README must be valid Markdown with proper heading hierarchy
- CLI must handle edge cases gracefully (no git repo, permission errors)

## Telemetry / Metrics Expected
- None for this work item (local CLI tool)

## Rollout / Rollback Notes
- Rollout: Merge to main branch; users can clone and run immediately
- Rollback: Revert commit; no persistent state to clean up
