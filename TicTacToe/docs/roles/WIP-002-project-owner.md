# Project Owner Notes: WIP-002 - AI Player Option for O

## Decisions Made

1. **AI plays as O only**: Simplifies implementation - human always goes first as X
2. **Single difficulty level**: Avoid scope creep; implement "medium" intelligence that blocks and takes wins
3. **Toggle-based activation**: Checkbox is simple and intuitive for users
4. **Slight delay on AI moves**: 500ms delay makes game feel more natural, not jarring
5. **No external dependencies**: AI logic will be built-in, no ML libraries

## Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Multiple difficulty levels | More engaging | Scope creep, more testing | Rejected for WIP-002 |
| AI can play as X or O | Flexible | More complex UI and logic | Rejected - AI is O only |
| Minimax perfect AI | Unbeatable | Never fun to play against | Rejected - medium difficulty |
| Random AI | Simple | Not fun, too easy | Rejected |

## Tradeoffs Accepted

- Only one difficulty level (can add more in future work item)
- AI always O (simpler, human always starts)
- Delay may feel slow to some users (but prevents jarring instant moves)

## Known Limitations or Risks

- AI strategy needs to be good enough to be fun but not unbeatable
- Toggle state needs to persist correctly during game reset
- Edge case: toggling AI mid-game needs defined behavior

## Justification

User explicitly requested AI opponent for single-player mode. This is a natural extension of WIP-001 that maintains backward compatibility with existing two-player functionality.
