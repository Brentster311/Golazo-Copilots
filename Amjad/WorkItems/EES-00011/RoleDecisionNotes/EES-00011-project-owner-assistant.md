# EES-00011 — Project Owner Assistant Decision Notes

## Decomposition Rationale
Part 2 of the v2 rule grammar refactor (see EES-00010 for full rationale). This work item updates the LLM prompt and extraction pipeline to produce v2 rules.

## Key Decisions
- **Depends on EES-00010**: Cannot start until the data model accepts v2 rules.
- **Prompt must include both ELSE and no-ELSE examples**: So the LLM learns both patterns.
- **Gap detector updated here**: Since gap detection is tightly coupled to the rule format the LLM produces.

## Must-Ask Checklist
- [x] Interface type: Existing Tkinter GUI (established)
- [x] Target platform: Windows (established)
- [x] Data persistence: YAML files (established)
- [x] User type: Technical / knowledge engineers (established)
