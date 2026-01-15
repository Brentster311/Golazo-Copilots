# Project Owner Notes: WIP-004 - Configurable AI Difficulty Levels

## Decisions Made

1. **Created from WIP-002 out-of-scope item**: "Multiple AI difficulty levels" was explicitly deferred
2. **Three difficulty levels defined**: Easy (random), Medium (current), Hard (minimax)
3. **Backward compatible**: Default to Medium preserves current behavior

## Alternatives Considered

1. **Two levels only (Easy/Hard)**: Simpler but less flexible
   - Rejected: Medium provides good middle ground
2. **Numeric difficulty slider**: More granular control
   - Rejected: Three discrete levels are clearer for users
3. **Adaptive difficulty**: Adjust based on player performance
   - Rejected: Too complex, out of scope

## Tradeoffs Accepted

- Hard mode (minimax) may be unbeatable - could frustrate users
- More code complexity with three strategies
- Work item created but not prioritized

## Known Limitations or Risks

- Minimax implementation adds complexity
- Hard mode may not be fun (always ties or wins)
- UI space needed for difficulty selector

## Source Reference

From `docs\workitems\WIP-002-user-story.md`:
> **Out of scope**
> - Multiple AI difficulty levels (only one difficulty for now)
