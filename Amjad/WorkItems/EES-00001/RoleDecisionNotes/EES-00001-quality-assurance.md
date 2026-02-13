# EES-00001 — Quality Assurance Decision Notes

## Review Findings Summary

| Severity | Count | IDs |
|----------|-------|-----|
| Critical | 3 | CR-1, CR-2, CR-3 |
| Major | 5 | MJ-1, MJ-2, MJ-3, MJ-4, MJ-5 |
| Minor | 3 | MN-1, MN-2, MN-3 |

### Critical items (must fix before dev):
- **CR-1, CR-2:** Design doc references old `Noun.Property = value` format in FR-2 and Summary — should use parameterized format
- **CR-3:** Incident YAML schema example is truncated/incomplete

### Major items (should fix):
- **MJ-3** is the most significant: rule generation logic is underspecified. The Architect needs to clarify whether the LLM proposes complete rules or just facts.
- **MJ-1, MJ-2:** Error handling gaps for invalid files and LLM parse failures
- **MJ-4:** Specialize action on root cause needs clarification
- **MJ-5:** Edited facts need input validation

### Minor items (deferrable):
- Instance tracking in ontology, fact-level provenance on rules, duplicate rule detection

## Test Coverage Summary

- **28 test cases** covering all 7 acceptance criteria
- Every AC has at least one test
- Happy paths, error cases, and edge cases included
- Test cases explicitly define expected failure messages where applicable

## Capability Registry
- Only a placeholder capability exists — no impact analysis needed

## Decisions
- Test cases TC-24 through TC-28 go beyond explicit ACs but address realistic failure modes from the risk table
- Root cause specialize (MJ-4) flagged as question for Architect rather than blocking QA
