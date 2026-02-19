# EES-00017 Quality Assurance Notes

## Review Summary
- Design doc approved with one edge case flagged (partial structured fields)
- 23 test cases defined covering: to_fact (5), validate (8), serialization (8), regression (2)
- All acceptance criteria mapped to at least one test case

## Edge Cases Added to Test Cases
- TC-17-13: Partial structured fields (target_noun set, but target_property/value missing) → must produce validation error
- TC-17-02: None instance defaults to wildcard "*"
- TC-17-10: Legacy format skips validation entirely

## Coverage Assessment
| Acceptance Criterion | Test Cases |
|---------------------|------------|
| Structured fields on RuleOutput | TC-17-01, TC-17-14 |
| to_fact from structured target | TC-17-01, TC-17-02 |
| to_fact legacy unchanged | TC-17-03, TC-17-04, TC-17-05 |
| validate against ontology | TC-17-06 through TC-17-12 |
| Partial fields error | TC-17-13 |
| Serialization round-trip | TC-17-14 through TC-17-21 |
| Backward compatibility | TC-17-22, TC-17-23 |
