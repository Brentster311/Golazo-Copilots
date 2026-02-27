# SFI-036 — Project Owner Assistant Decision Notes

## Decision: Single User Story (no decomposition)

This is a single code cleanup task with one observable outcome: `tk_app.py` is gone, the app still works, tests still pass. Decomposing further would create artificial dependencies between sub-stories.

## Must-Ask Checklist Resolution

All four normally-required questions are already answered by the existing project context:

- **Interface type**: Existing Tk GUI desktop app — no change (this is a code cleanup, not a feature).
- **Target platform**: Windows — no change.
- **Data persistence**: No change — this is purely import retargeting.
- **User type**: Developer (the "user" of this story is the developer maintaining the codebase).

## Scope Decisions

1. **Why delete vs. keep as re-export shim?** — The monolith is 3,132 lines of fully duplicated code. A re-export shim would still leave the dead code importable and create confusion. Clean deletion is the correct approach.

2. **Migration map included in story** — Because ~60+ imports across ~12 files must be retargeted, the story includes an explicit mapping table so the developer knows exactly where each symbol should come from. This avoids guesswork during implementation.

3. **BUILD_MANIFEST.md update** — Included as in-scope since it documents the PyInstaller build command which references `tk_app.py`.
