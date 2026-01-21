# User Story: GCP-005

**Status**: IMPLEMENTED

## User Story

- **Title**: Distribution Package Creator
- **As a**: GolazoCP distributor or end user
- **I want**: to run a command that packages GolazoCP into a distributable zip file
- **So that**: I can easily share or deploy GolazoCP to new projects without requiring a git clone

## Out of Scope
- Automatic versioning or release tagging
- Publishing to package registries (PyPI, npm, etc.)
- Installer wizards or GUI-based packaging
- Platform-specific installers (.msi, .deb, .dmg)
- Compression formats other than zip

## Assumptions
- **Assumption (explicit)**: The zip will be created in the current working directory with a predictable name (e.g., `GolazoCP-dist.zip`)
- **Assumption (explicit)**: Python's built-in `zipfile` module is sufficient (no external dependencies)
- **Assumption (explicit)**: The IDE-specific instruction files will be named `USAGE-VisualStudio.md` and `USAGE-VSCode.md`

## Acceptance Criteria (bulleted, testable)
- [ ] Running `python Golazo_Copilot.py --package` creates a zip file named `GolazoCP-dist.zip`
- [ ] The zip contains the complete `.github/` folder structure (copilot-instructions.md + roles/*.md)
- [ ] The zip contains `README.md`
- [ ] The zip contains `USAGE-VisualStudio.md` with Visual Studio-specific setup instructions
- [ ] The zip contains `USAGE-VSCode.md` with VS Code-specific setup instructions
- [ ] The command outputs the path to the created zip file on success
- [ ] The command returns exit code 0 on success, non-zero on failure

## Non-functional Requirements
- No external dependencies beyond Python standard library
- Zip creation should complete in under 5 seconds for typical payload size

## Telemetry / Metrics Expected
- None (CLI tool, no telemetry)

## Rollout / Rollback Notes
- Feature is additive; existing `--install` behavior unchanged
- Rollback: remove `--package` flag handling from script
