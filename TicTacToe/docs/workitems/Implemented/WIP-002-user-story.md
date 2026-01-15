# User Story: WIP-002 - AI Player Option for O

**Status**: ? IMPLEMENTED

## Title
O Player Can Be Designated as AI Player

## As a
User who wants to play tic-tac-toe alone

## I want
The option to designate the O player as an AI opponent

## So that
I can enjoy the game without needing a second human player

## Out of scope
- Multiple AI difficulty levels (only one difficulty for now)
- AI playing as X
- Network/online AI
- AI vs AI mode
- Saving/loading AI preferences

## Assumptions
- AI will always play as O (human is always X)
- AI makes moves automatically after human moves
- A simple toggle or checkbox enables/disables AI mode
- AI uses a reasonable strategy (not random, not perfect)
- Game can be switched between AI and two-player mode via reset or toggle

## Acceptance Criteria
- [x] UI provides a way to enable/disable AI opponent (checkbox or toggle)
- [x] When AI is enabled, O moves are made automatically after X moves
- [x] AI makes legal moves only (empty cells)
- [x] AI makes reasonably intelligent moves (blocks wins, takes wins when available)
- [x] AI mode can be toggled on/off without restarting the application
- [x] When AI is disabled, game reverts to two-player mode
- [x] AI move has a slight delay (e.g., 500ms) for better UX
- [x] Status label reflects AI is thinking/moving when appropriate
- [x] All existing two-player functionality continues to work when AI is disabled

## Non-functional requirements
- No external dependencies (AI logic must be self-contained)
- AI should respond within 1 second
- Single file implementation maintained

## Telemetry / metrics expected
- None required

## Rollout / rollback notes
- Backward compatible - existing two-player mode unchanged
- Single file update
