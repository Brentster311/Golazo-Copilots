# GCP-0028: Design Document

## Summary
Add a `TechBestPractices.md` reference file to `.github/roles/` that technical roles (Architect, Developer, Refactor Expert) can consult for accumulated technical knowledge and known pitfalls.

## Problem Statement
Technical decisions are sometimes repeated or reversed because institutional knowledge isn't captured in a reusable format accessible during the workflow.

## Proposed Approach
1. Create `TechBestPractices.md` in default roles directory
2. Add `## Reference Documents` section to Architect, Developer, and Refactor Expert role files pointing to it
3. Include initial content (Azure Identity credential practices)
4. Ensure `gcp_bootstrap` copies the file when `include_roles=True`

## Alternatives Considered
- Embedding practices in each role file — rejected, causes duplication and maintenance burden

## Risks
- None significant — additive file, no code logic changes

## Test Strategy
- Verify bootstrap copies the file
- Verify role files reference it
- Existing tests pass
