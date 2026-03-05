# GCP-0065 Quality Assurance Notes

## QA Outcome
Design accepted with actionable clarifications captured in review comments.

## Critical Verification Requirements
- Validate automatic migration from legacy `capabilities.yaml` to `WorkItems/capabilities.yaml`.
- Validate deterministic precedence when both canonical and legacy files exist.
- Validate actionable failure messages for missing file and migration failures.

## TDD Guidance
Define/adjust tests before implementation to lock expected behavior and prevent regressions.
