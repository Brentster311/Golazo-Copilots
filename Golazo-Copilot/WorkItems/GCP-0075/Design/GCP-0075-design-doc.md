# GCP-0075 Design Document

## Summary

Make the enforced `documenter -> builder` workflow executable without backward transitions. Documenter will review non-release user documentation. Builder will own release classification, the PEP 440 version update in `pyproject.toml`, the newest-first README changelog entry, validation, build, commit, and push.

## Problem Statement

Documenter currently requires a version from future Builder notes, while Builder claims ownership of versioning and says it must run before Documenter. The actual transition order runs Documenter first. Contributors must violate instructions or transition backward.

## Business Case

A forward-only completion path reduces workflow friction, duplicated builds, and ambiguous release ownership. Success means one Documenter pass followed by one Builder pass, with policy tests detecting future contradictions.

## Stakeholders

- Golazo workflow contributors
- Release maintainers
- Consumers of packaged and bootstrap-generated role instructions

## Functional Requirements

- Documenter reviews implementation documentation without requiring release metadata or future Builder artifacts.
- Builder selects patch/minor/major from delivered scope, updates the single canonical version, validates PEP 440 monotonicity, writes the matching changelog entry, builds artifacts, validates capabilities, then commits and pushes.
- Neither role requires an artifact from a future role.
- Packaged defaults, bootstrap-generated copies, README role order, and policy tests agree.
- Complete and Express remain executable; Spike remains unchanged and has no release-documentation role.

## Non-Functional Requirements

Keep instructions concise, deterministic, cross-platform, and free of runtime or state-schema changes. Preserve semantic-version and PEP 440 policies.

## Proposed Approach

1. Rewrite Documenter responsibilities and entry conditions to exclude release metadata and future Builder dependencies.
2. Rewrite Builder responsibilities to own versioning and changelog together after Documenter, removing references to transitioning back.
3. Correct README role ordering and release-flow guidance.
4. Add policy tests over packaged role text and a forced bootstrap copy to verify consistency and reject circular language.

## Alternatives Considered

- Reorder Builder before Documenter: rejected because it changes workflow state and makes final documentation unavailable before commit.
- Keep backward transitions: rejected because rework should not be mandatory for the happy path.
- Add a new release-manager role: rejected as unnecessary complexity.

## Risks And Mitigations

- Builder may choose an incorrect bump: retain explicit patch/minor/major rules and require monotonic PEP 440 and changelog consistency checks.
- Generated roles may drift: bootstrap-copy test compares installed text to packaged defaults.
- README may drift: policy assertions cover role order and ownership language.

## Dependencies

Packaged Markdown role resources, bootstrap role copying, `pyproject.toml`, README changelog, and existing transition order.

## Migration, Rollout, And Rollback

No state migration. New package installs and forced bootstrap refreshes receive corrected role text. Existing customized workspace roles are not overwritten unless users choose force. Rollback restores Markdown and tests only.

## Observability

No external telemetry. Policy tests and Builder notes expose version/changelog validation outcomes; retrospective metrics track backward completion transitions.

## Test Strategy

Test packaged role ownership, absence of future-role dependencies, Complete and Express compatibility, actual transition order, README consistency, and force-bootstrap generated copies. Run focused policy tests, full coverage, Ruff, and package build.
