# EES-00017: Structured RuleOutput with Typed State Transitions

**Status**: IMPLEMENTED

**User Story**

- **Title**: Replace free-text RuleOutput description with structured typed targets
- **As a**: knowledge engineer authoring and reviewing diagnostic rules
- **I want**: `CHANGE_STATE` rule outputs to specify a structured target (noun, instance, property) and a typed value instead of a free-text description like `"User.adminRole => confirmed"`
- **So that**: the engine can validate that a rule's output writes a legal value to a known property, state transitions are machine-readable (not narrative), and rule authoring errors are caught at definition time rather than at evaluation time

- **Out of scope**:
  - Goal declaration and evaluation termination (EES-00018)
  - Changes to `RULED_OUT` or `GAP` output kinds (they remain description-based — they reference what was eliminated, not a state to write)
  - LLM prompt/tool schema changes for the extractor (separate follow-up if needed)
  - GUI rule editor redesign

- **Assumptions**:
  - **Assumption (explicit)**: Depends on EES-00016 (typed ontology). `CHANGE_STATE` target values are validated against `OntologyProperty.validate_value()`
  - **Assumption (explicit)**: `RULED_OUT` and `GAP` continue to use `description: str` — they are signals, not state mutations. Only `CHANGE_STATE` gets the structured target.
  - **Assumption (explicit)**: Backward compatibility — existing rule YAML files with `then: {kind: CHANGE_STATE, description: "..."}` load via a migration path: parse the description string to extract noun.property and value where possible, or keep as-is with a deprecation warning.
  - **Assumption (explicit)**: The `RuleOutput.to_fact()` method is updated to produce a fact from the structured target rather than parsing the description string.

- **Acceptance Criteria (bulleted, testable)**:
  - `RuleOutput` for `CHANGE_STATE` kind has optional fields: `target: dict` (`{noun, instance, property}`) and `value: str` — used instead of `description` when present
  - `RuleOutput.to_fact()` produces a `Fact` from `target` + `value` when available, falling back to current description-parsing behavior for legacy rules
  - `RuleOutput.validate(ontology: OntologyManager) -> list[str]` checks that the target noun/property exists and the value is legal per the typed ontology
  - Rule YAML serialization emits the structured format; deserialization handles both old (description-only) and new (target+value) formats
  - The rule evaluator's `CHANGE_STATE` branch writes derived facts using the structured target, not by parsing a description string
  - Unit tests cover: structured serialization round-trip, legacy format loading, validation against ontology (valid/invalid values), `to_fact()` with both formats

- **Non-functional requirements**: No new dependencies; must not break existing rule YAML files
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: Additive fields on `RuleOutput`. Old YAML loads cleanly. Rules authored in the new format are not backward-compatible with pre-EES-00017 code.
