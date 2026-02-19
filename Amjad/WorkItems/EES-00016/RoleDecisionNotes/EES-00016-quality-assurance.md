# EES-00016 — Quality Assurance Decision Notes

## Review Summary
Design doc reviewed and approved with minor edge case additions. The implementation surface is small (two files) and well-bounded.

## Edge Cases Added
1. Empty enum `values` list → reject all (TC-16-03)
2. Case-sensitive enum matching (TC-16-04)
3. Unknown type fallback to True (TC-16-16)
4. Chaining pseudo-nouns skip validation (TC-16-27)

## Test Coverage Assessment
- 27 test cases covering all four types, serialization round-trips, backward compatibility, and `validate_fact` with various noun/property/value combinations
- Each acceptance criterion from the user story has at least one corresponding test case
- No gaps identified

## Capability Impact
Checked against `capabilities.yaml` — this change affects the core models and ontology manager. No GUI or evaluator changes are in scope.
