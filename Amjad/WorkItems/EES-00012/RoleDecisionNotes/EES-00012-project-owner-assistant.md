# EES-00012 — Project Owner Assistant Decision Notes

## Decomposition Rationale
Part 3 of the v2 rule grammar refactor (see EES-00010 for full rationale). This work item updates the GUI to display v2 rules.

## Key Decisions
- **Depends on EES-00010 and EES-00011 (now EES-00013)**: Needs both the model and extraction to produce v2 rules before display makes sense. Both are complete.
- **Read-only display**: Rule editing in the GUI is out of scope.
- **Branch indication in evaluation view**: When the engine runs, the GUI should show which branch (THEN or ELSE) fired for each rule.
- **Live LLM status text**: User requested a continuously updating status indicator during LLM extraction. The status bar already exists (`status_var`); the extraction loop (multi-turn tool-calling from EES-00013) needs to emit progress callbacks that update it in real time.

## Must-Ask Checklist
- [x] Interface type: Existing Tkinter GUI (established)
- [x] Target platform: Windows (established)
- [x] Data persistence: YAML files (established)
- [x] User type: Technical / knowledge engineers (established)
