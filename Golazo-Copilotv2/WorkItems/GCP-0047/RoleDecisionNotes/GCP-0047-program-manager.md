# GCP-0047: Program Manager Decision Notes

## Design Decisions

### POA Closure as Terminal State
The retrospective → project-owner-assistant transition makes POA reachable from the end of the workflow. POA Closure has NO forward transition — it's a terminal state. This avoids infinite loops (POA → PM → ... → Retro → POA → PM → ...). The transition engine already supports this: retrospective currently has `["builder"]` as its only forward transition; we add `"project-owner-assistant"` to that list.

### Separate Closure Output
Recommending `{id}-closure.md` as a distinct required output rather than reusing `{id}-project-owner-assistant.md`. Rationale: the POA role now serves two distinct purposes (initial story creation vs. final closure), and the outputs have different content (story artifacts vs. AC validation + pending work items). Mixing them in one file would be confusing.

### QA Sharpening Strategy
Moved design-quality bullets to Architect rather than deleting them. This preserves coverage while eliminating the overlap. QA becomes the "can we test this?" role; Architect becomes the "is this well-designed?" role. Both still write to Review-Comments.md but in their respective sections.

### Security Checklist in Architect
Chose a checklist format (4 items) rather than a narrative requirement. This gives the LLM a concrete evaluation framework while keeping the section concise. Findings go in Capability-Impact.md under a "Security Assessment" heading — this reuses an existing artifact rather than creating a new one.

### PM Governance — Content Choices
Based the new sections on patterns observed across all other roles:
- Decision rules focus on scope management and alternatives evaluation (PM's core job)
- Escalation rules mirror the "create a new User Story" pattern used by QA, Architect, Developer
- Success criteria are measurable: "reviewable with minimal follow-ups" + "feasible, staged, measurable"
