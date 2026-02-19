# EES-00017 Program Manager Notes

## Key Design Decisions
1. **Flat fields over nested dict**: `target_noun`, `target_instance`, `target_property`, `value` as top-level optional fields on `RuleOutput`. Simpler than a nested `target: {noun, instance, property}` dict — avoids an anonymous inner structure.
2. **Kept `description` for CHANGE_STATE**: Even structured outputs can carry an optional description as human-readable documentation. Required for `RULED_OUT`/`GAP`.
3. **Legacy detection via `target_noun` key**: `from_dict()` checks for `target_noun` to distinguish structured vs. legacy format. Simple and unambiguous.
4. **No rule evaluator changes**: It already calls `to_fact()` — the new structured path is transparent to the evaluator.
5. **Validation via `OntologyManager`**: `RuleOutput.validate(ontology_manager)` reuses `OntologyProperty.validate_value()` from EES-00016. No new validation framework.

## Scope Boundary
- Only `CHANGE_STATE` gets structured fields.
- `RULED_OUT` and `GAP` remain description-based — they signal what was eliminated/needed, not state mutations.
- LLM extractor prompt changes are explicitly out of scope.
