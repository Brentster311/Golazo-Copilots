# EES-00012 — Project Owner Assistant Decision Notes

## Decomposition Rationale
Part 3 of the v2 rule grammar refactor (see EES-00010 for full rationale). This work item updates the GUI to display v2 rules.

## Key Decisions
- **Depends on EES-00010 and EES-00011**: Needs both the model and extraction to produce v2 rules before display makes sense.
- **Read-only display**: Rule editing in the GUI is out of scope.
- **Branch indication in evaluation view**: When the engine runs, the GUI should show which branch (THEN or ELSE) fired for each rule.

## Must-Ask Checklist
- [x] Interface type: Existing Tkinter GUI (established)
- [x] Target platform: Windows (established)
- [x] Data persistence: YAML files (established)
- [x] User type: Technical / knowledge engineers (established)
