# GCP-0026: Design Document

## Summary
Update all 9 default role files in `.github/roles/` to include properly formatted `## Required Outputs` sections with typed `file:` and `dir:` prefixes, enabling GCP-0025's output validation to work out of the box.

## Problem Statement
GCP-0025 introduced output validation but default role files lacked the structured `## Required Outputs` format needed for automatic validation.

## Proposed Approach
- Add `## Required Outputs` section to each of the 9 role files
- Use `file:` prefix for file outputs and `dir:` prefix for directory outputs
- Use `{id}` placeholder for work item ID substitution
- Additive change only — no existing sections modified

## Alternatives Considered
- Hardcode outputs in Python — rejected, role files should be the source of truth

## Risks
- None significant — additive change, no breaking changes

## Test Strategy
- Existing 165 tests continue to pass
- Manual verification of output format in each role file
