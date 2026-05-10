# TIM-0004 — Project Owner Assistant Decision Notes

## Scope Decisions

**Six documents in scope** (confirmed against User Story):
1. Delivery Is Existential - 2
2. Harambee and Mission Teams
3. The Delivery Manifesto
4. AWARE Framework and Mission Teams
5. Delivery Is an Infinite Game
6. The Role of the Senior IC Leader

**Explicitly excluded**: The April 16 Working Session invitation (htm file) — it is an event invitation, not a substantive corpus document.

## WHY / HOW / WHAT Framing

- **WHY** = The threat, problem, or urgency Tim is responding to
- **HOW** = The mechanisms, structures, and principles Tim proposes
- **WHAT** = The specific outputs, behaviors, or artifacts readers should expect to see

## Assumptions

- `OFP_Delivery.md` lives at workspace root (not inside WorkItems or Agile)
- Tone is neutral and accurate — this is a summary introduction, not a response or critique
- Each section should be readable in under 90 seconds (~200–300 words)
- The file is designed to be expanded in TIM-0005+ with actual response sections

## Acceptance Criteria (confirmed testable)

1. OFP_Delivery.md exists with a title and framing paragraph before the document summaries
2. Each of the six Tim documents has its own named section
3. Each section contains WHY, HOW, and WHAT sub-headers with concise prose
4. Language is executive-accessible: concrete, no jargon
5. File is committed to git

## Implementation Approach

Single Markdown file with a preamble section followed by six document-summary sections. No bullet dumps in the sub-headers — prose only, kept to 2–4 sentences per sub-header for 90-second readability.
