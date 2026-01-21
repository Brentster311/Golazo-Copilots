# GCP-002: Project Owner Assistant Decision Document

## Work Item
GCP-002 — Golazo CLI Tool and README Documentation

## Decisions Made

### 1. Single User Story (not decomposed)
The request contains two deliverables (CLI tool + README), but they represent a **single user-observable outcome**: "I can adopt Golazo in my project and understand how to use it."

**Rationale**: The CLI without documentation is incomplete, and documentation without an easy install mechanism reduces adoption. They form one cohesive deliverable.

### 2. Python CLI (not interactive installer)
User specified CLI interface explicitly. Python is appropriate because:
- `Golazo_Copilot.py` already exists (empty)
- Python is cross-platform
- Standard library is sufficient (no dependencies)

### 3. Repo root detection via `.git` traversal
Standard approach used by git hooks, pre-commit, and similar tools. Walk up directory tree until `.git` folder found.

### 4. Embedded source files
The CLI will read from the `.github/` folder in the same repo where the script lives, then copy to the target repo. This keeps the source of truth in one place.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Split into 2 stories (CLI + README) | Too small individually; tightly coupled deliverables |
| Interactive prompts in CLI | User didn't request; adds complexity; can be future enhancement |
| Download instructions from URL | Requires network; offline use is valuable |
| YAML/JSON config for customization | Out of scope; keep simple for v1 |

## Tradeoffs Accepted

- No version checking (won't warn if target repo has newer instructions)
- No selective role installation (all-or-nothing copy)
- README is static (not generated from role files)

## Known Limitations or Risks

1. **File overwrite**: CLI will overwrite existing files without backup — documented behavior
2. **No validation**: Won't verify copied files are valid Markdown
3. **Hardcoded paths**: Assumes `.github/` structure; not configurable

## Questions Resolved

| Question | Resolution |
|----------|------------|
| Interface type? | CLI (user specified) |
| Target platform? | Cross-platform (Windows, macOS, Linux) |
| Dependencies? | Standard library only |

## Scope Justification

Acceptance criteria count: **8 items** — this exceeds the 7-item guideline, but:
- 4 items are CLI behavior (single feature)
- 4 items are README content (single document)
- Both are simple file operations, not complex logic

Keeping as one story avoids artificial fragmentation.
