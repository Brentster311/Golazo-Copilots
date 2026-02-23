# GCP-0053 — POA Decision Notes (Project Owner Assistant)

## Context
During GCP-0052 session, observed that retrospective ended the workflow without returning to POA for closure/acceptance. The agent itself flagged this as a gap: "the complete profile should include a final POA acceptance role after retrospective."

## Key Decisions

### 1. Scope: Complete profile only
- `express` and `spike` profiles remain unchanged — they end at retrospective
- Only `complete` profile enforces the POA closure loop

### 2. POA closure is a distinct state, not a new role
- No 11th role — POA is re-entered with context that distinguishes "closure" from "initial entry"
- The existing `## Closure` section in POA role file already describes the closure tasks
- State model needs a way to distinguish these two entry modes

### 3. Output validator must be context-aware
- On initial POA entry: `{id}-closure.md` is NOT required
- On closure re-entry: `{id}-closure.md` IS required
- This is the core technical challenge — the output validator currently parses Required Outputs statically from the role markdown

### 4. Retrospective role must explicitly hand off
- Retrospective role instructions need to state: "transition to project-owner-assistant for closure"
- This is both a role file change and a programmatic enforcement in `gcp_transition`
