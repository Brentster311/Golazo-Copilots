# FRC-006 Review Comments

## Domain Expert Review
- Keep UI contract-bound to API fields only; avoid introducing inferred finance analytics in this shell story.
- Prioritize deterministic render text for status and errors to support non-technical validation.

## Quality Assurance Review
- Add automated tests for:
  - successful health render
  - successful planner summary render
  - API unavailable error render
- Verify frontend startup command is documented and reproducible.

## Architect Notes
- Keep API client isolated from view components.
- Use route-level separation for health and summary pages.
- Avoid coupling frontend startup to backend process lifecycle; treat backend as external local dependency.
