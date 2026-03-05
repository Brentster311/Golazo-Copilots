# GCP-0034: Project Owner Assistant Notes

## Decision Notes
- Root cause: `gcp_bootstrap` checks for `.git`, `pyproject.toml`, `package.json`, `Cargo.toml`, `.hg` but not `WorkItems/`
- The Golazo-Copilotv2 workspace has `WorkItems/` but none of those markers at its level — `.git` is at the parent repo root
- Bootstrap fell through to the parent directory, deploying `.github/` at the wrong level
- Fix: Add `WorkItems` to the workspace marker list as a directory check
- Express profile — single validation check addition
