# GCP-002: Program Manager Decision Document

## Work Item
GCP-002 — Golazo CLI Tool and README Documentation

## Decisions Made

### 1. Simple Copy Architecture (not template-based)
The CLI will copy files directly rather than generating from templates.

**Rationale**: The instruction files are static content. Template generation adds complexity without benefit for v1.

### 2. Script-relative Source Path
Source files are located relative to `Golazo_Copilot.py`, not hardcoded absolute paths.

**Rationale**: Makes the tool portable — works regardless of where repo is cloned.

### 3. Overwrite Without Backup (v1)
Existing files will be overwritten without creating backups.

**Rationale**: Keeps v1 simple. Users can use git to recover previous versions. Backup flag can be added in future work item.

### 4. Exit Codes for Scripting
- Exit 0: Success
- Exit 1: Failure

**Rationale**: Enables integration with scripts, CI, and other automation.

### 5. README at Repo Root (not in .github/)
README.md goes in repository root, not `.github/`.

**Rationale**: Standard convention; GitHub displays root README on repo homepage.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Interactive mode (prompts) | Adds complexity; user didn't request |
| Config file for customization | Over-engineering for v1 |
| Dry-run flag | Nice-to-have; future work |
| Colorized output | Requires external library or complex ANSI handling |

## Tradeoffs Accepted

- No backup of overwritten files (simplicity over safety)
- No progress bar (single-digit file count doesn't warrant it)
- No `--help` flag detail (argparse basics only)

## Known Limitations or Risks

1. **Self-installation**: Running in this repo will overwrite its own files (harmless but potentially confusing)
2. **No update detection**: Won't tell user if files are already current
3. **No partial install**: All-or-nothing; can't install just the spine

## Sequencing

1. Implement `find_repo_root()` first (core dependency)
2. Implement file copy functions
3. Implement main orchestration
4. Create README.md last (can reference working tool)

## Success Metrics

- CLI runs successfully on Windows, macOS, Linux
- All 11 files copied correctly (1 spine + 10 roles)
- README passes Markdown linting
- Zero external dependencies
