# Architect Notes: WIP-002 - AI Player Option for O

## Decisions Made

1. **Approved extension of existing class**: No need for separate AI class
2. **tkinter BooleanVar for state**: Standard pattern, works well
3. **root.after() for delay**: Correct non-blocking approach
4. **AI_DELAY as class constant**: Recommended for maintainability

## Alternatives Considered

1. **Separate AIPlayer class**: 
   - Would be cleaner OOP
   - Overkill for simple strategy
   - Rejected for this scope

2. **Threading for AI delay**:
   - More complex
   - tkinter not thread-safe
   - Rejected - use `after()` instead

## Tradeoffs Accepted

- All AI logic in single class (acceptable for scope)
- No abstraction for different AI strategies (can add later if needed)

## Known Limitations or Risks

- Extending to multiple AI difficulties would require refactoring
- Current design is optimized for single difficulty level
