# GCP-0072 Architect Decision Notes

## Outcome

Approved for development. Public inputs, result shape, path resolution, rendering, validation, atomic replacement, security, and compatibility boundaries are explicit in Architect Notes.

## Key Decisions

- Add opt-in installation and explicit confirmation fields to the existing bootstrap API.
- Allow omitted configuration only when the caller explicitly confirms the full packaged defaults.
- Merge supplied overrides over canonical defaults, then validate the complete effective object.
- Store canonical defaults as a structured package resource and enforce parity with the human-readable `SKILL.md`.
- Copy and validate the entire skill tree in staging before exposing the final directory.
- Reject skill installation in `orchestrator-only` mode.
- Preserve all existing bootstrap inputs and result fields; add structured skill outcomes.
- Use standard-library file APIs and existing PyYAML only.

## Security Review

No authentication or network boundary changes. The implementation must constrain writes to fixed scope-derived destinations, avoid caller-controlled paths, avoid printing full configuration objects, and never accept or persist credentials or tokens.

## Capability Review

Automated impact found no registered capabilities because the registry contains only an unrelated placeholder. Actual affected product behavior and compatibility implications are documented in `GCP-0072-Capability-Impact.md`.

## Follow-Up

A separate maintenance work item should replace the placeholder capability registry with real Golazo capability cards. This does not block implementation.