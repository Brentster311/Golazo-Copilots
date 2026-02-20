# GCP-0045 Design Doc

## Summary
Add a "Trigger Phrase Recognition" section to `.github/copilot-instructions.md` that instructs the AI to immediately call `gcp_create_workitem` when it detects specific trigger phrases, without asking for confirmation.

## Problem Statement
The AI assistant fails to recognize Golazo workflow triggers in user messages. When a user says "new workitem", provides a work-item ID (e.g., `CVT-002`), or says "complete mode", the AI treats it as a conversational request rather than a workflow command. This has resulted in users needing to repeat themselves 3+ times, wasting message cycles and eroding confidence in process adherence.

## Business Case
- **Why now**: This is a zero-cost, high-impact fix. Every Golazo user hits this friction point.
- **Impact**: Eliminates 2–3 wasted messages per work item creation. Across dozens of work items per project, this saves significant user time and frustration.
- **KPIs**: 
  - Zero repeated-ask cycles when trigger phrases are used
  - First-message compliance rate = 100% for recognized trigger phrases

## Stakeholders
- **Golazo Copilot users** (primary): Benefit from immediate workflow initiation
- **Golazo maintainers**: Own the copilot-instructions.md file

## Functional Requirements
1. A new section titled "IMMEDIATE ACTION: Trigger Phrase Recognition" (or similar high-visibility heading) must be added to `.github/copilot-instructions.md`
2. The section must list these trigger phrases:
   - "new workitem" / "new work item"
   - Any string matching the work-item ID pattern `^[A-Za-z]{1,4}-\d{3,}$` (e.g., `GCP-0045`, `CVT-002`)
   - "complete mode"
3. The section must instruct the AI to IMMEDIATELY call `gcp_create_workitem(work_item_id="<id>", profile="complete")` without asking for confirmation
4. If the user provides a work-item ID, use it; if only a trigger phrase is given without an ID, derive the next sequential ID or ask for it

## Non-Functional Requirements
- Instructions must be concise (< 20 lines) and use imperative language
- Must not conflict with existing FORBIDDEN ACTIONS or gate enforcement rules
- Must be placed early in the file for maximum AI attention (before or adjacent to "REQUIRED: Before EVERY Response")

## Proposed Approach
Add a new section between "FORBIDDEN ACTIONS" and "REQUIRED: Before EVERY Response" with the heading and trigger rules. Use bold, imperative phrasing to maximize AI compliance.

### Proposed Section Content (Draft)
```markdown
## IMMEDIATE ACTION: Trigger Phrase Recognition

When the user's message contains ANY of these triggers, IMMEDIATELY call `gcp_create_workitem` — do NOT ask for confirmation:

| Trigger | Action |
|---------|--------|
| "new workitem" or "new work item" | Call `gcp_create_workitem(work_item_id="<id>", profile="complete")` |
| A work-item ID matching pattern `[A-Za-z]{1,4}-\d{3,}` (e.g., `GCP-0045`, `CVT-002`) | Use the provided ID in `gcp_create_workitem` |
| "complete mode" | Call `gcp_create_workitem` with `profile="complete"` |

**Rules:**
- If the user provides a work-item ID, use it exactly.
- If no ID is provided, determine the next sequential ID from existing WorkItems/ folders.
- Do NOT treat these as conversational requests. They are workflow commands.
- After creating the work item, proceed immediately to the project-owner-assistant role.
```

## Alternatives Considered
| Alternative | Why Rejected |
|-------------|-------------|
| Modify MCP server to auto-detect triggers | Over-engineered; the MCP server processes tool calls, not user messages. The AI instructions layer is the correct place. |
| Add a separate `.github/trigger-config.yaml` | Unnecessary indirection. A single section in copilot-instructions.md is simpler and more discoverable. |
| Do nothing; rely on user training | The retrospective shows this doesn't work. Users expect the AI to follow its own workflow. |

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| AI still ignores trigger phrases despite instructions | Low | Medium | Use imperative, bold formatting. Place section early. Test with fresh chat sessions. |
| False positive: user mentions "new workitem" conversationally | Very Low | Low | Unlikely in a dev context. If it happens, user can cancel. |
| Section conflicts with existing instructions | Very Low | Low | Section is additive; no existing content is modified. |

## Dependencies
- None. This is a standalone change to a single file.

## Migration / Rollout / Rollback Plan
- **Rollout**: Commit updated `.github/copilot-instructions.md`. Takes effect on next chat session.
- **Rollback**: Revert the added section. No data migration needed.

## Observability Plan
- Manual testing: Start a new chat, say "new workitem: <description>", verify immediate `gcp_create_workitem` call
- Track retro findings in future projects for regression

## Test Strategy Summary
- **Manual acceptance test**: In a fresh chat session, send "new workitem: test feature" and verify the AI calls `gcp_create_workitem` on the first message
- **Regression test**: Verify existing workflow commands ("gcp_status", etc.) still work correctly
- **Edge case test**: Send a work-item ID alone (e.g., "GCP-0099") and verify it triggers work item creation
