# GCP-0059 — Domain Expert Decision Notes

## Domain Assessment
- Domain expertise required: No additional specialized domain consultation is needed beyond path/contract consistency review.
- The requested changes are naming and path contract clarifications for bootstrap artifacts, not algorithmic, platform, security, or architecture expansions.
- Primary risk remains requirement drift across artifacts (story, design, role notes, implementation/tests/docs).

## Requirement Clarification (Not New Scope)
- This update is a requirement clarification, not a new scope area.
- Spine filename requirement is explicit: `.github/agents/golazo-copilot/orchestrator.md`.
- Copied roles location requirement is explicit: `.github/agents/golazo-copilot/roles/...`.
- Any wording that implies a generic/variable roles subfolder under `.github/agents` is non-compliant and replaced by the explicit path requirement above.
- Any legacy spine or roles path variants are non-compliant for this work item.

## Guidance to Downstream Roles
- Architect/Developer: treat these as fixed path contracts and align constants/helpers accordingly.
- QA: validate exact path literals in behavior and tests; include negative checks for legacy/incorrect names and generic subfolder phrasing in docs.
- Documenter: ensure help text and examples consistently use `.github/agents/golazo-copilot/orchestrator.md` and `.github/agents/golazo-copilot/roles/...`.
