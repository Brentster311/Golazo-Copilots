# GCP-0028: Test Cases

## Test Strategy
- Existing bootstrap tests verify role file copying — TechBestPractices.md included in the set
- Manual verification that 3 role files reference the document

## Test Cases
1. **Bootstrap copies TechBestPractices.md** — `gcp_bootstrap(include_roles=True)` copies file to workspace
2. **Role references exist** — Architect, Developer, Refactor Expert role files contain `TechBestPractices.md` reference
3. **Initial content** — File contains Azure Identity credential practice
4. **Existing tests pass** — No regressions
