# EES-00010 — Project Owner Assistant Decision Notes

## Decomposition Rationale
The v2 rule grammar refactor was decomposed into three work items:
1. **EES-00010** (this): Data model + engine — the foundation
2. **EES-00011**: LLM prompt + extraction — depends on EES-00010
3. **EES-00012**: GUI display — depends on EES-00010 and EES-00011

Each is independently testable. EES-00010 can be verified with unit tests alone. EES-00011 adds LLM integration. EES-00012 adds visual display.

## Key Decisions
- **Breaking change accepted**: The v2 grammar is fundamentally different from v1. Existing rules need re-extraction.
- **ELSE is optional**: Simplifies rules that only need to fire on match (like R4 in the example).
- **Three output types only**: CHANGE_STATE, RULED_OUT, GAP. BECAUSE and Conclusion were deferred per user direction.
- **AND only**: OR decomposed into multiple rules. Matches v1 decision.
- **GAP is terminal**: Does not chain. CHANGE_STATE and RULED_OUT are chainable.

## Must-Ask Checklist
- [x] Interface type: Existing Tkinter GUI (established in prior work items)
- [x] Target platform: Windows (established)
- [x] Data persistence: YAML files (established)
- [x] User type: Technical / knowledge engineers (established)
