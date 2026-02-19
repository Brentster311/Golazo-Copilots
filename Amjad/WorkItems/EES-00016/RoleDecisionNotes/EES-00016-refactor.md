# EES-00016 Refactor Notes

## Refactoring Applied

### Removed duplicate `_CHAINING_KINDS` constant
- **Before:** `_CHAINING_KINDS` was defined separately on both `OntologyProperty` (models.py) and `OntologyManager` (ontology_manager.py) with identical values.
- **After:** `OntologyManager.validate_fact()` now references `OntologyProperty._CHAINING_KINDS` — single source of truth.
- **Rationale:** Eliminates risk of the two sets drifting out of sync.

## No Other Refactoring Needed
- `validate_value()` match/case is clean and readable.
- `to_dict()` / `from_dict()` follow established project pattern.
- Test structure mirrors production code well.

## Test Status
- 299/299 passing after refactor.
