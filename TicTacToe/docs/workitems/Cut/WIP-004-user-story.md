# User Story: WIP-004 - Configurable AI Difficulty Levels

**Status**: ?? BACKLOG

**Source**: WIP-002 User Story (explicitly listed as out of scope), potential future enhancement

## Title
Add Configurable AI Difficulty Levels

## As a
User playing against the AI

## I want
The ability to choose between different AI difficulty levels (Easy, Medium, Hard)

## So that
I can adjust the challenge level to match my skill or mood

## Out of scope
- AI playing as X (human always X)
- AI vs AI mode
- Online/network play
- Machine learning or adaptive AI

## Assumptions
- Current AI strategy becomes "Medium" difficulty
- Easy: Random valid moves
- Hard: Minimax algorithm (optimal play)
- Selection via dropdown or radio buttons
- Setting persists across game resets

## Acceptance Criteria
- [ ] UI control to select AI difficulty (Easy/Medium/Hard)
- [ ] Easy mode: AI makes random valid moves
- [ ] Medium mode: Current priority-based strategy (Win > Block > Center > Corner > Side)
- [ ] Hard mode: Minimax algorithm for optimal play
- [ ] Difficulty selection persists when game is reset
- [ ] AI toggle still works (enable/disable AI)
- [ ] All existing functionality preserved

## Non-functional requirements
- No external dependencies
- Single-file structure maintained
- Hard mode should respond within 1 second

## Telemetry / metrics expected
- None

## Rollout / rollback notes
- Backward compatible
- Default to Medium (current behavior)
