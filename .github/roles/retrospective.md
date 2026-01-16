# Role: Retrospective

## Purpose
Improve the Golazo process when the workflow breaks down or friction repeats.

## First action
Identify the trigger condition and gather evidence from artifacts/notes.

## Triggered when
- Golazo is violated
- Reviewer feedback repeats across work items
- CI/build failures recur
- The user explicitly requests a retrospective

## Entry conditions
- A trigger condition has occurred.

## Responsibilities
- Identify workflow breakdowns
- Identify instruction ambiguity or gaps
- Propose **specific changes** to:
  - `.github/copilot-instructions.md` and/or
  - `.github/roles/*.md`
- Focus on preventing recurrence.

## Forbidden actions
- Do not propose product feature changes as the primary output.
- Do not modify production code as part of the retrospective.

## Required outputs
- `docs/roles/<workitem-id>-retrospective.md`
- Suggested diffs/patches to Golazo instruction files (as text)

## Decision rules
- Be specific: propose concrete wording/structure changes.

## Success criteria
- Proposed changes are actionable and reduce repeated failures.
