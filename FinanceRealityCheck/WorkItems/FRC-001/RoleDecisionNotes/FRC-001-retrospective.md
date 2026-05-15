# FRC-001 Retrospective

## What went well
- Role-by-role artifact gates kept scope disciplined from vision through implementation.
- TDD flow was successful: clear red baseline, then green with reproducible commands.
- Capability-impact and capability-validation checks were consulted at architecture, developer/refactor, and builder stages.
- Build and packaging verification surfaced release readiness before closure.

## What didn't go well
- Environment setup flow caused repeated interruptions due canceled environment tool calls and path confusion.
- Mixed git context (workspace as subdirectory of a larger repo with unrelated sibling changes) created risk of accidental staging.
- Branch context drift (AGL-001 vs FRC-001) introduced avoidable friction during builder stage.

## Action items
1. Add a short "Workspace Git Scope Check" step to Builder first action:
   - Run git rev-parse --show-toplevel and git status --short -- .
   - Stage files via explicit path list when workspace is a subdirectory.
2. Add a "Python Environment Decision" step to Developer first action:
   - Confirm upfront whether to use workspace venv or global interpreter.
   - Persist that decision in role notes to avoid repeated setup attempts.
3. Add a reusable command block in TechBestPractices for venv activation on Windows PowerShell with fallback execution-policy command.
4. Add a checklist item in Documenter/Builder handoff to ensure release version and changelog labels are synchronized exactly once.

## Metrics
- Setup friction metric: number of blocked/canceled environment setup attempts per work item (target <= 1).
- Git safety metric: number of commits with unintended staged files outside workspace path (target = 0).
- Flow efficiency metric: elapsed time from developer start to builder completion (target decreases across next 3 work items).
- Gate reliability metric: number of transition failures due missing required outputs (target = 0 after role template tuning).
