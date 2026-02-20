# GCP-0045 — Project Owner Assistant Decision Notes

## Work Item
**GCP-0045**: Add Golazo Workflow Trigger Phrase Recognition to Copilot Instructions

## Scope Decision
**Single story** — This is a single-file change to `.github/copilot-instructions.md`. One user-observable outcome: the AI recognizes trigger phrases and immediately starts the workflow. No decomposition needed.

## Must-Ask Checklist Resolution
| Question | Answer | Rationale |
|----------|--------|-----------|
| Interface type | Instruction file (`.github/copilot-instructions.md`) | The request explicitly names this file and the trigger phrase mechanism. Not a CLI/GUI/API — it's AI prompt configuration. |
| Target platform | Cross-platform | Copilot instructions are platform-agnostic markdown consumed by VS Code on any OS. |
| Data persistence | File-based | Single markdown file edit. No database or cloud persistence involved. |

All three answers are unambiguously determined by the request context. No user clarification was needed.

## Key Decisions
1. **Placement**: The trigger-phrase section should be placed near the top of the instructions (before or alongside "REQUIRED: Before EVERY Response") for maximum visibility to the AI's context processing.
2. **No code changes**: This is purely an instruction-file update. No MCP server changes, no Python changes, no role-file changes.
3. **Trigger phrases are additive**: The new section adds behavior without modifying any existing sections. No risk of regression to current workflow rules.

## Assumptions Made
- The work-item ID pattern matches the existing regex `^[A-Za-z]{1,4}-\d{3,}$` already in the project-owner-assistant role file. No new pattern needed.
- "complete mode" is a user-defined shorthand meaning "create workitem with profile=complete". This matches the existing `gcp_create_workitem(profile="complete")` call.

## Risks
- **Low risk**: AI models may still occasionally fail to follow instructions despite explicit phrasing. This change maximizes the odds but cannot guarantee 100% compliance across all AI providers.
