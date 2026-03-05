# GCP-0050 Developer Notes

## What Was Implemented

Rewrote `golazo-copilot/src/golazo_copilot/bootstrap-instructions.md` — the package-level spine template deployed by `gcp_bootstrap` to `.github/copilot-instructions.md`.

### Changes Made

**Replaced content** — the original ~90-line file was rewritten to incorporate the subagent orchestration spine while preserving all existing workflow sections.

**New sections added:**
- **Orchestrator Mode** — defines the 8-step orchestrator loop (status → context → spawn → collect → verify → transition → summary → repeat)
- **Subagent Prompt Template** — prescribes `runSubagent` call pattern with the `gcp_role_context` bundle
- **Between-Roles Summary** — display format after each subagent completes
- **Fallback Mode** — automatic switch to inline execution if `runSubagent` fails; no retry
- **User Override** — "work inline" / "use subagents" commands to toggle mode

**Preserved sections (updated):**
- Forbidden Actions (unchanged)
- REQUIRED Before Every Response (updated to reference orchestrator loop)
- Starting a New Work Item (unchanged)
- Role Transitions (compacted role list to arrow notation)
- File Naming Convention (unchanged)
- Gate Enforcement (unchanged)
- Capability Registry (unchanged)

**Removed from package template:**
- Trigger Phrase Recognition section — this is workspace-specific and belongs in `.github/copilot-instructions.md`, not the package-level template

### Line Count

Final: **137 lines** (AC7 target ≤150 ✓)

## Decisions

1. **Trigger phrases excluded from package template** — these are deployment-specific and should be added by the workspace's copilot-instructions.md, not baked into every installation
2. **Role list compacted to arrow notation** — saves 9 lines while remaining readable
3. **Responsibilities merged into two-line format** — clear division between orchestrator and subagent without verbose bullet lists
4. **Fallback is session-sticky** — once inline mode is triggered by a failure, it stays inline (no flapping)

## Test Results

371 tests passing, 0 regressions. No new tests needed — this is a documentation/template change, not code logic.
