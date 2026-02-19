# EES-00017 Developer Notes

## TDD Summary
- **RED**: 23 tests written (TC-17-01 through TC-17-23). 18 failed, 5 passed (legacy path tests that already worked).
- **GREEN**: Extended `RuleOutput` with 4 optional fields, `is_structured` property, updated `to_dict`/`from_dict`/`to_fact`, added `validate()` method. All 23 tests pass.
- **Regression**: Full suite 322/322 passing (299 existing + 23 new).

## Implementation Details
- Added `target_noun`, `target_instance`, `target_property`, `value` as optional fields (default `None`)
- `is_structured` property: `True` when `target_noun is not None`
- `to_fact()`: structured path produces `Fact(noun=target_noun, ...)`, legacy path unchanged
- `validate(ontology_manager)`: delegates to `OntologyManager.validate_fact()` for structured outputs, returns `[]` for legacy/RULED_OUT/GAP
- `from_dict()`: reads structured fields via `.get()` — handles both formats
- Added `TYPE_CHECKING` import for `OntologyManager` to avoid circular import
- No changes to `rule_evaluator.py` — it already calls `to_fact()` transparently

## Files Changed
- `src/ees/models.py` — `RuleOutput` extended
- `tests/test_models.py` — 23 new tests in 4 classes
