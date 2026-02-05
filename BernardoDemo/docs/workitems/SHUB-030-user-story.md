# SHUB-030: Apollo Article Drafter

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: AI-assisted Apollo article drafting from case patterns
- **As a**: Apollo content author
- **I want**: The AI to generate article drafts based on common case resolutions
- **So that**: I can create high-quality self-help content faster

## Scope

- **In scope**:
  - Generate article draft from case cluster analysis
  - Follow Apollo template structure automatically
  - Include: title, description, symptoms, solutions, resources
  - Suggest diagnostics to embed based on case resolution patterns
  - Validate against authoring guidelines
  - Support both issue-based and how-to article types
  
- **Out of scope**:
  - Auto-publishing (editorial review still required)
  - Image/video generation
  - GT (Guided Troubleshooter) creation (separate story SHUB-031)

## Acceptance Criteria (bulleted, testable)

- [ ] User can request: "Draft an article for VM RDP connectivity issues"
- [ ] Generated draft follows Apollo template structure
- [ ] Draft includes symptom variations from actual cases
- [ ] Draft includes resolution steps ordered by frequency
- [ ] Draft passes 80%+ of validation rules automatically
- [ ] User can iterate: "Make the troubleshooting steps more detailed"

## Non-functional Requirements

- Draft generation: < 30s
- Template compliance: 100%
- Validation rule compliance: > 80% on first draft

## Telemetry / Metrics Expected

- Drafts generated per author per week
- Edit distance from draft to published (quality measure)
- Time from draft to publish vs. baseline

## Dependencies

- SHUB-011 (Documentation RAG) for guideline awareness
- SHUB-023 (Improvement Items) for pattern identification
