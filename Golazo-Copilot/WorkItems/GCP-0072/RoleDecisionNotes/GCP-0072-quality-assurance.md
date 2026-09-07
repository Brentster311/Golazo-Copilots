# GCP-0072 Quality Assurance Decision Notes

## Review Outcome

Approved for architecture with four required clarifications recorded in review comments: explicit confirmation state, canonical default completeness, atomic replacement, and deterministic mode behavior.

## Test Strategy Decisions

- Map every acceptance criterion to named cases with explicit expected failures.
- Extend the existing `test_gcp_bootstrap.py` fixtures for temporary workspace and monkeypatched home behavior.
- Test generated content and package-source immutability directly.
- Test no-force, force, invalid-input, and simulated write-failure paths.
- Keep tests isolated from live user directories, Azure authentication, and Azure DevOps.
- Require focused coverage above 70% for changed modules.

## Scope Control

No acceptance criteria were added. The recommendation that `orchestrator-only` reject skill installation resolves an existing design question while preserving that mode's documented behavior.

## Automated Test Timing

Executable tests are deferred to the Developer TDD red phase because Architecture must first finalize the public input and structured result contracts. The test cases provide exact intent and failure messages for that implementation.