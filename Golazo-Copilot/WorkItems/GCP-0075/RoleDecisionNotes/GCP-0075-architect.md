# GCP-0075 Architect Decision Notes

## Decision

Approve Builder-owned release metadata aligned to Complete's Documenter-before-Builder order and Express's Builder-only completion path.

## Boundaries

- Canonical policy lives in packaged role Markdown.
- Bootstrap copies canonical resources unchanged.
- README summarizes the same order, profile compatibility, and ownership.
- Policy tests enforce positive ownership and forbidden circular phrases.

## Security And Compatibility

No code execution, dependency, API, state, authentication, or data-handling behavior changes. Existing non-force bootstrap protection remains intact.

## Capability Impact

`bootstrap-skill-installation` is directly affected only in generated role content; skill installation behavior is unchanged.
