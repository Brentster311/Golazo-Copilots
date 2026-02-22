# GCP-0046 — Program Manager Decision Notes

## Work Item
GCP-0046: Add Domain Expert Role to the Definition Phase

## Design Decisions

### Role Placement
Placed `domain-expert` between `program-manager` and `quality-assurance` because:
1. PM produces the Design Doc (the "what")
2. Domain Expert evaluates specialized concerns (the "what about X?")
3. QA reviews the full design including domain guidance (the "is it complete?")

This ordering ensures domain expertise informs the review rather than being an afterthought.

### Artifact Strategy
Domain experts write to the shared `{id}-Review-Comments.md` rather than a separate artifact because:
- Review Comments is already the canonical "feedback on the design" artifact
- QA and Architect already read Review Comments — domain guidance will be naturally incorporated
- Avoids artifact proliferation

### Transition Changes
- `program-manager` forward target changed from `quality-assurance` to `domain-expert`
- `quality-assurance` backward target changed from `program-manager` to `domain-expert`
- This makes the domain-expert step **mandatory** — PM cannot skip to QA
- If domain expertise is genuinely not needed, the domain-expert role documents this and transitions forward

### Test Impact
Existing tests that reference hardcoded role indices or validate PM → QA transitions will need updating. The design doc's test strategy covers these cases.

## Open Questions
None — the user's request was detailed and unambiguous.
