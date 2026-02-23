# GCP-0050 Design Document — Subagent Orchestration Spine

## Summary
Rewrite `bootstrap-instructions.md` to transform Copilot from a single-agent model into an orchestrator that delegates each role's work to a focused subagent via `runSubagent`.

## Problem Statement
Currently, Copilot performs all 10 role phases in a single long conversation. By role 6-7, context pollution degrades output quality. The spine (bootstrap-instructions.md) needs to instruct Copilot to delegate each role to a fresh subagent with only the relevant context.

## Business Case
- **Why now:** GCP-0048 (self-contained role files) and GCP-0049 (gcp_role_context tool) are complete — the infrastructure exists.
- **Impact:** Cleaner context per role → higher quality outputs. Clear separation of orchestrator vs. worker responsibilities.
- **KPIs:** Spine readability (≤150 lines), Copilot follows the pattern without re-prompting.

## Proposed Approach

### Structure of the New Spine
The new `bootstrap-instructions.md` will have these sections:

1. **Header & Forbidden Actions** (kept from current)
2. **Orchestrator Mode** (NEW — the core change)
   - Orchestrator loop: `gcp_status` → `gcp_role_context` → `runSubagent` → collect output → `gcp_transition` → repeat
   - Orchestrator responsibilities: workflow control, gate enforcement, user summaries
   - Subagent responsibilities: creative work per role instructions
3. **Subagent Prompt Template** (NEW)
   - How to compose the `runSubagent` call with the bundle from `gcp_role_context`
   - Explicit "return your output, do not ask questions" instruction
4. **Between-Roles Summary** (NEW)
   - What the orchestrator displays between subagent runs
5. **Fallback Mode** (NEW)
   - If subagent spawning fails → inline execution (current V2 behavior)
   - Trigger condition clearly stated
6. **User-Override Mechanism** (NEW)
   - "work inline" / "no subagents" escape hatch
7. **Starting a New Work Item** (kept, slightly updated)
8. **Role Transitions** (kept)
9. **File Naming Convention** (kept)
10. **Gate Enforcement** (kept)
11. **Capability Registry** (kept)

### Key Design Decisions
- The spine instructs behavioral patterns — it cannot programmatically enforce subagent usage
- Fallback is graceful: if `runSubagent` is unavailable, the orchestrator works inline
- Subagent prompt template uses the markdown bundle from `gcp_role_context` as the full prompt
- Override mechanism is per-session (no persistent state)

## Alternatives Considered
1. **Programmatic orchestrator in Python** — Rejected: out of scope, requires GCP-0052+ work
2. **Keep current single-agent spine** — Rejected: defeats purpose of GCP-0048/0049
3. **Subagent per AC rather than per role** — Rejected: too fine-grained, roles are the natural unit

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Copilot doesn't follow orchestrator pattern | Clear, imperative language; fallback mode |
| Subagent output too large for orchestrator to process | `gcp_role_context` already has 100KB size guard |
| User confusion about what's happening | Between-roles summary provides visibility |

## Dependencies
- GCP-0048: Self-contained role files (completed)
- GCP-0049: gcp_role_context tool (completed)

## Test Strategy
- Visual inspection: verify all 7 ACs against the written markdown
- Line count verification (≤150 lines)
- Functional test: use the new spine in a real workflow session (covered by GCP-0052)
