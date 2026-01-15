# Program Manager Notes: WIP-002 - AI Player Option for O

## Decisions Made

1. **Priority-based AI strategy**: Win > Block > Center > Corner > Side
   - Provides good gameplay without being unbeatable
   - Simple to implement and test
   
2. **500ms delay for AI moves**: Makes game feel natural
   - Constant can be adjusted if needed
   - Status feedback during delay

3. **Checkbox for AI toggle**: Simple, intuitive control
   - Positioned below grid, above reset button
   - Uses tkinter BooleanVar for state management

4. **AI always plays as O**: Simplifies logic, human always starts

## Alternatives Considered

1. **Minimax with alpha-beta pruning**: 
   - Perfect play but not fun
   - Rejected for this iteration

2. **Machine learning approach**:
   - Would require external dependencies
   - Overkill for tic-tac-toe
   - Rejected

3. **Radio buttons for mode selection**:
   - More explicit but takes more space
   - Checkbox is simpler
   - Rejected

## Tradeoffs Accepted

- AI is beatable (by design - more fun)
- Fixed delay (not adaptive)
- No difficulty levels in this iteration

## Known Limitations or Risks

- AI strategy is deterministic (same game = same AI response)
- No learning or adaptation
- Edge cases around toggling mid-game need careful handling
