# EES-00016 — Developer Decision Notes

## Implementation Summary

### Files Changed
1. **`src/ees/models.py`** — `OntologyProperty` dataclass:
   - Added `values: list[str]` field (default `[]`)
   - Added `default: str | None` field (default `None`)
   - Added `validate_value(v: str) -> bool` method using `match` statement for enum/bool/long/string
   - Updated `to_dict()` to emit `values` and `default` (only when non-empty/non-None)
   - Updated `from_dict()` to read new fields with safe defaults

2. **`src/ees/ontology_manager.py`** — `OntologyManager`:
   - Added `_CHAINING_KINDS` class constant
   - Added `validate_fact(fact: Fact) -> list[str]` method

### Files Added (tests)
3. **`tests/test_ontology_manager.py`** — 27 new test cases across 3 test classes:
   - `TestOntologyPropertyValidateValue` (16 tests)
   - `TestOntologyPropertySerialization` (5 tests)
   - `TestOntologyManagerValidateFact` (6 tests)

## TDD Cycle
- **Red**: Tests written first, all failed with `TypeError: unexpected keyword argument 'values'`
- **Green**: Production code implemented, all 34 ontology manager tests pass
- **Regression**: Full suite — 299 tests passed, 0 failures

## Design Decisions During Implementation
- `to_dict()` only emits `values` and `default` when they have meaningful content (non-empty list, non-None). This keeps serialized YAML clean.
- `validate_value` for `long` type uses `v.lstrip("-").isdigit() and v != "-"` to handle negatives correctly while rejecting a bare minus sign.
- `validate_fact` skips chaining pseudo-nouns (`RULED_OUT`, `CHANGE_STATE`, `GAP`) — these aren't real ontology entities.
