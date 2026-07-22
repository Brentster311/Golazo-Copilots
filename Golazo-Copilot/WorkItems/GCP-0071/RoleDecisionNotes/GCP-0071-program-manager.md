# GCP-0071 Program Manager Notes

## Planning decisions
- Chosen approach: correct the workflow engine and instruction sources together so all profiles re-enter POA for closure.
- Express and spike keep their reduced role lists; only the post-retrospective closure step changes.

## Scope controls
- The work item covers transition semantics, closure-mode state entry, documentation, and tests in one slice.
- No broader redesign of profiles or role responsibilities is included.

## Review focus requested
- Confirm there are no remaining statements that express/spike end at retrospective.
- Confirm closure-only outputs remain gated until POA is re-entered in closure mode.