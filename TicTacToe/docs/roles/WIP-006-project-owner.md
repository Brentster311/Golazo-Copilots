# Project Owner Notes: WIP-006 - Rename Project Folders to tictactoe

## Decisions Made

1. **Rename to `tictactoe`**: Consistent with file rename (WIP-005)
2. **Include VS project file updates**: Required for project to work
3. **Recommend combining with WIP-005**: Single refactoring effort is cleaner

## Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Rename folders to `tictactoe` | Clear, consistent | VS project complexity | ? Selected |
| Keep folder names, only rename files | Less invasive | Inconsistent naming | Rejected |
| Recreate project from scratch | Clean structure | Loses git history | Rejected |
| Flatten to single folder | Simpler structure | May break VS expectations | Rejected |

## Tradeoffs Accepted

- More complex than file rename
- VS project files need careful updating
- Risk of breaking project if done incorrectly

## Known Limitations or Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| VS project breaks | Medium | Backup first, test after |
| Git history lost | Low | Use `git mv`, verify rename tracking |
| Path references break | Medium | Search all files for old paths |

## Dependencies

- **WIP-005**: File rename should be done together or first
- Consider combining WIP-005 and WIP-006 into single implementation

## Source Reference

From `docs\roles\RETRO-003-retrospective.md`:
> The project folder structure uses generic Visual Studio default names (`PythonApplication2\PythonApplication2\`) that provide no context about the application.
