# EES-00016: Typed Ontology Properties with Enum/Bool Values

**Status**: IMPLEMENTED

**User Story**

- **Title**: Add typed values, defaults, and validation to OntologyProperty
- **As a**: knowledge engineer building diagnostic rules
- **I want**: ontology properties to declare their type (`enum`, `bool`, `long`), legal values (for enums), and a default value — so that fact values are validated against the ontology and expressed as typed data instead of free-form narrative text
- **So that**: facts like `User($u).directoryRole == global_admin` use constrained enum values instead of sentences like `"admin-granted"`, enabling the engine to validate inputs, detect illegal state transitions, and present clear state to operators

- **Out of scope**:
  - Restructuring `RuleOutput` (separate work item EES-00017)
  - Goal declaration / evaluation termination (separate work item EES-00018)
  - GUI changes to ontology editor (will adapt to new fields naturally)
  - Changing the Noun(instance).Property parsing syntax

- **Assumptions**:
  - **Assumption (explicit)**: `OntologyProperty` already has a `type` field — this work extends it with `values: list[str]` and `default: str | None`
  - **Assumption (explicit)**: Validation is advisory during extraction (log warnings) but enforced when the user confirms a fact — confirmed facts with illegal values are rejected
  - **Assumption (explicit)**: Backward compatibility is NOT maintained — the `string` type was removed per Project Owner directive. Every property must be `enum`, `bool`, or `long`.
  - **Assumption (explicit)**: The three supported types are `enum` (must be in `values` list), `bool` (`true`/`false`), and `long` (integer). This covers all current and foreseeable property needs.

- **Acceptance Criteria (bulleted, testable)**:
  - `OntologyProperty` has fields: `type: str` (enum|bool|long), `values: list[str]` (legal values for enum type), `default: str | None` (starting value)
  - `OntologyProperty.validate_value(v: str) -> bool` returns True if the value is legal for the property's type (e.g., value in `values` for enum, `true`/`false` for bool, parseable int for long); unknown types return False
  - `OntologyProperty.to_dict()` and `from_dict()` serialize/deserialize the new fields
  - `from_dict()` defaults to `type="enum"` when type is not specified
  - `OntologyManager.validate_fact(fact: Fact) -> list[str]` returns validation errors if the fact's value is not legal for its noun/property type
  - Unit tests cover: enum validation (legal/illegal), bool validation, long validation, invalid type rejection, missing property (unknown noun/prop)

- **Non-functional requirements**: No new dependencies; pure dataclass/logic changes
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: `string` type removed. Existing YAML with `type: string` will load but `validate_value()` will reject all values — properties must be migrated to `enum`, `bool`, or `long`.
