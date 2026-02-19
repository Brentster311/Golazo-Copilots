# EES-00017 — Review Comments

## Design Doc Review

### Clarity & Completeness
- **PASS**: Flat-field approach is clearly justified and well-documented
- **PASS**: Both legacy and structured serialization paths are explicitly defined
- **PASS**: `to_fact()` behavior for both paths is specified with concrete examples

### Feasibility & Sequencing
- **PASS**: Single-step implementation touching only `models.py` (and rule YAML migration)
- **PASS**: Rule evaluator requires no changes — `to_fact()` abstraction holds
- **PASS**: Dependency on EES-00016 is satisfied

### Edge Cases to Address
1. **Partial structured fields**: What if `target_noun` is set but `target_property` is None? **Recommendation**: `validate()` should catch this as an error — all four structured fields must be present together for CHANGE_STATE. Add a consistency check.
2. **Empty value string**: What if `value=""` for a structured CHANGE_STATE? **Recommendation**: Allow it — an empty string may be a legal enum value (if explicitly in `values` list). Validation will catch it if it's not legal.
3. **RULED_OUT/GAP with accidental target fields**: What if someone sets `target_noun` on a RULED_OUT output? **Recommendation**: Ignore structured fields for non-CHANGE_STATE kinds. `validate()` and `to_fact()` should only use them when `kind == "CHANGE_STATE"`.
4. **Description field on structured CHANGE_STATE**: Should `to_dict()` still emit `description` for structured outputs? **Recommendation**: Yes, if it's non-empty. Useful as human-readable documentation alongside the machine-readable fields.

### Naming
- **PASS**: `target_noun`, `target_instance`, `target_property`, `value` are clear and unambiguous
- **PASS**: `validate()` method name is consistent with `OntologyProperty.validate_value()`

### Capability Impact
- 8 capabilities transitively affected. Changes are additive (new optional fields defaulting to None). No existing signatures change. Existing tests should pass without modification.
- GUI `gui_adapters.py` reads `output.description` for display — this will still work since description is preserved.

## Verdict
**Approved** — proceed to test cases. Address edge case #1 (partial structured fields validation) in the test cases.

---

## Architect Notes

### Architectural Alignment
- **PASS**: Extends existing dataclass pattern — consistent with codebase style
- **PASS**: Flat optional fields over nested dict — matches the project's preference for simple, explicit structures
- **PASS**: `validate()` delegates to `OntologyManager` → reuses EES-00016 infrastructure without new coupling

### Contracts
- `to_fact()` contract: structured path produces a real ontology fact; legacy path produces a pseudo-fact. Consumer (`rule_evaluator.py`) doesn't need to know the difference — it just calls `to_fact()`.
- `validate(ontology_manager) -> list[str]` contract: same error-list pattern as `OntologyManager.validate_fact()`. Consistent API.
- Serialization contract: `from_dict(to_dict(x)) == x` for both structured and legacy formats.

### Capability Impact
- Files: `models.py` (direct), `rule_evaluator.py` (no code changes, but behavior changes via `to_fact()`)
- 8 capabilities transitively affected. All changes are additive. No existing signatures changed.
- GUI `gui_adapters.py`: reads `output.description` for display — still works since description is preserved.

### Blast Radius
- Minimal: new optional fields default to `None`. All existing `RuleOutput("CHANGE_STATE", "desc")` constructors continue to work.
- Rule YAML migration (R-001 through R-004) is data-only — the code handles both formats.

### Security / Privacy
- N/A — internal model, no user input, no network, no secrets.

### Verdict
**Approved** — proceed to implementation.
