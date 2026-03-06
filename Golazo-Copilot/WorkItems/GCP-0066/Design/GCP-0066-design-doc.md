# GCP-0066 Design Doc

## Summary
Enforce a release-documentation policy where the Documenter role must maintain the changelog at the end of `golazo-copilot/README.md`, and the release version must be defined/updated before any changelog update is made.

## Problem Statement
Current workflow guidance allows changelog edits to happen ad hoc, creating drift between release version metadata and changelog entries. This increases risk of publishing undocumented versions or documenting versions that were not finalized.

## Business Case
- Why now: recent release activity required manual changelog follow-up, exposing ordering gaps.
- Impact: improves release traceability and lowers documentation/version mismatch risk.
- KPIs:
  - 100% of release-related work items include version-first then changelog updates.
  - 0 releases with missing changelog entry for the published version.

## Stakeholders
- Golazo maintainers
- Release managers and package publishers
- Consumers relying on README changelog for upgrade context

## Functional Requirements
- Documenter role instructions explicitly require changelog maintenance at the end of `README.md`.
- Workflow guidance must require version definition/update before changelog update.
- Validation/test coverage must enforce sequencing expectation in role behavior and/or workflow checks.
- Existing role flow remains intact except for new policy checks and messaging.

## Non-Functional Requirements
- Deterministic, clear validation/error messages when sequencing is violated.
- Backward compatibility with existing work item transitions.
- Minimal additional runtime overhead.

## Proposed Approach
- Update Documenter role default instructions to include mandatory changelog maintenance requirement and placement guidance.
- Update Builder/Documenter guidance so version update is an explicit prerequisite for changelog updates.
- Add or update tests that verify:
  - Documenter instruction text includes changelog requirement.
  - Version-before-changelog ordering expectations are present and enforced by existing workflow checks where applicable.
- Ensure README changelog section format remains stable.

## Alternatives Considered
- Separate `CHANGELOG.md`: rejected for now due to explicit requirement to keep changelog at end of `README.md`.
- Keep policy as tribal convention: rejected due to inconsistent outcomes.

## Risks, Mitigations, Open Questions
- Risk: ambiguous ownership between Builder and Documenter.
  - Mitigation: explicitly define sequence and role boundaries in role files.
- Risk: tests assert wording too rigidly.
  - Mitigation: assert semantic requirements with resilient matching.
- Open question: should transition gate hard-fail if changelog/version evidence missing, or rely on role compliance and tests only?

## Dependencies
- Default role instruction files under `src/golazo_copilot/roles/defaults/`
- Existing role validation tests
- README changelog conventions

## Migration / Rollout / Rollback Plan
- Rollout: update role docs and tests in one change set.
- Migration: no data migration required.
- Rollback: revert role instruction and test changes if regressions occur.

## Observability Plan
- Ensure failing tests clearly indicate missing changelog or missing version-first requirement.
- Capture role decision notes documenting compliance evidence in work items.

## Test Strategy Summary
- Unit/integration tests for role content expectations.
- Regression tests for existing transition behavior to confirm no unintended gate breakage.
