# User Story: WIP-006 - Rename Project Folders

**Status**: ? IMPLEMENTED

**Source**: RETRO-003 - Folder Structure Not Reviewed

## Title
Rename Project Folders from PythonApplication2

## As a
Developer or user of this codebase

## I want
The project folders renamed from `PythonApplication2` to descriptive names

## So that
- Folder names clearly indicate what the project contains
- Project structure is intuitive and navigable
- Naming is consistent with the application purpose

## Out of scope
- Changing any code functionality
- Restructuring the folder hierarchy
- Changing solution-level docs folder location

## Assumptions
- Visual Studio project/solution files will need updates
- Git will track as rename preserving history
- WIP-005 (file rename) should be completed first or combined with this
- May require careful coordination with VS project system

## Acceptance Criteria
- [x] Outer folder renamed: `PythonApplication2\` ? `PythonApplication3\`
- [x] Inner folder renamed: `PythonApplication2\PythonApplication2\` ? `PythonApplication3\TicTacToe\`
- [x] `.pyproj` file renamed and updated
- [x] `.sln` file updated with new paths
- [x] All 37 tests pass
- [x] Game runs correctly
- [ ] Git history preserved (shown as rename, not delete+add)

## Implementation Notes
User manually implemented with different naming than originally specified:
- Outer folder: `PythonApplication3` (instead of `tictactoe`)
- Inner folder: `TicTacToe` (descriptive as intended)

## Non-functional requirements
- No functionality changes
- Visual Studio project must still open and work correctly
- All existing tests pass

## Telemetry / metrics expected
- None

## Rollout / rollback notes
- More invasive than file rename - affects VS project structure
- Consider combining with WIP-005 in single refactoring effort
- Backup/commit before attempting
- May need to recreate VS project if rename fails

## Dependencies
- Consider completing WIP-005 first, or combining both work items
