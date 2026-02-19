# EES-00017 Capability Impact Analysis

## Files Changed
- `src/ees/models.py` — extend `RuleOutput` with structured fields

## Directly Affected Capabilities
- **data-models**: `RuleOutput` gains 4 optional fields, updated `to_dict`/`from_dict`/`to_fact`
- **rule-evaluation**: `to_fact()` now produces real ontology facts for structured CHANGE_STATE outputs

## Transitively Affected Capabilities
- **yaml-persistence**: Reads/writes rule YAML — handles both formats via `from_dict`/`to_dict`
- **fact-extraction**: Produces `RuleOutput` objects — existing constructor signature unchanged
- **rule-generation**: Filters rules — no direct access to output fields
- **cli-orchestration**: Calls rule evaluator — no direct access to output fields
- **gui**: Reads `output.description` for display — still works (description preserved)
- **ontology-management**: Referenced by `validate()` method — consumed, not modified

## Risk Assessment
- **LOW**: All new fields default to `None`. No existing constructors break.
- **NONE**: Rule evaluator already calls `to_fact()` — behavior change is transparent.
