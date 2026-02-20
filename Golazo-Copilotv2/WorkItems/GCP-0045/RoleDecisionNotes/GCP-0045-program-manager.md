# GCP-0045 — Program Manager Decision Notes

## Work Item
**GCP-0045**: Add Golazo Workflow Trigger Phrase Recognition to Copilot Instructions

## Key Design Decisions

### 1. Section Placement
**Decision**: Place the trigger-phrase section between "FORBIDDEN ACTIONS" and "REQUIRED: Before EVERY Response"
**Rationale**: AI models weight early instructions more heavily. Placing this after forbidden actions (which must remain first) but before the per-response checklist ensures maximum visibility.

### 2. Imperative Language Style
**Decision**: Use bold, imperative phrasing ("IMMEDIATELY call", "do NOT ask")
**Rationale**: The retrospective showed the AI treated triggers as conversational. Imperative language with emphasis formatting leaves less room for misinterpretation.

### 3. Table Format for Triggers
**Decision**: Use a table mapping triggers to actions
**Rationale**: Tables are unambiguous, scannable, and map 1:1 from input to expected behavior. This is easier for both humans and AI to parse than prose.

### 4. No Code Changes
**Decision**: Instruction-file-only change
**Rationale**: The MCP server processes tool calls, not user messages. The AI instruction layer is the correct place to add message-pattern recognition rules.

## Open Questions
- None. All requirements are clear from the user story and retrospective context.

## Risks Acknowledged
- AI compliance is probabilistic, not guaranteed. This change maximizes the odds but cannot achieve 100% certainty across all AI model versions.
