# EES-00018 Capability Impact Analysis

## Files Changed
- `src/ees/models.py` — OntologyProperty goal fields, new Goal dataclass, EvaluationResult.goal_status
- `src/ees/rule_evaluator.py` — goal parameter, termination logic

## Directly Affected Capabilities
- **data-models**: OntologyProperty gains 3 fields, new Goal dataclass, EvaluationResult gains `goal_status`
- **rule-evaluation**: `evaluate()` gains optional `goal` parameter, termination checks added to loop

## Transitively Affected Capabilities
- **yaml-persistence**: Serializes OntologyProperty — handles new fields via `.get()` defaults
- **cli-orchestration**: Calls `evaluate()` — signature unchanged (new param is optional)
- **gui**: Reads `EvaluationResult` — `goal_status` field added but GUI doesn't use it yet (follow-up)
- **fact-extraction**: Produces rules — unaffected
- **rule-generation**: Filters rules — unaffected
- **ontology-management**: Manages OntologyProperty — new fields are passive annotations

## Risk Assessment
- **LOW**: All new fields have defaults. `evaluate()` signature is backward compatible.
- **NONE**: No existing callers pass `goal=` argument. No existing code reads `goal_status`.
