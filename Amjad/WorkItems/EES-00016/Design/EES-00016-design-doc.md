# EES-00016 — Design Doc: Typed Ontology Properties

## Summary
Extend `OntologyProperty` with typed value constraints (`enum`, `bool`, `long`), legal value lists, and defaults. Add validation logic to `OntologyManager` so fact values can be checked against the ontology at confirm time. **Note**: `string` type was removed per Project Owner directive — all properties must be `enum`, `bool`, or `long`.

## Problem Statement
Today `OntologyProperty` has only `name` and `type` (defaulting to `"enum"`), but `type` is now enforced. Previously fact values were free-form strings — the engine stored `"admin-granted"`, `"confirmed"`, `"required"` with no schema to constrain them. This means:
- Rules can reference values that don't exist or are misspelled
- The LLM generates narrative text as values instead of machine-readable tokens
- No validation happens at any point in the pipeline
- Operators and knowledge engineers can't tell what the legal states of a property are

## Business Case
- **Why now**: EES-00017 (structured CHANGE_STATE) and EES-00018 (goal-based termination) both depend on the ontology having typed properties. This is the foundation.
- **Impact**: Reduces rule authoring errors, enables engine validation, and makes fact values predictable
- **KPIs**: Zero new runtime dependencies; `string` type deliberately removed — no backward compatibility with untyped properties

## Stakeholders
- Knowledge engineers (authoring facts/rules)
- Rule evaluator engine (consuming typed values)
- LLM extractor (proposing facts validated against the ontology)

## Functional Requirements

### FR-1: OntologyProperty New Fields
```python
@dataclass
class OntologyProperty:
    name: str
    type: str = "enum"             # enforced: enum|bool|long
    values: list[str] = field(default_factory=list)   # NEW: legal values for enum
    default: str | None = None    # NEW: starting value
```

### FR-2: OntologyProperty.validate_value()
```python
def validate_value(self, v: str) -> bool:
    """Return True if v is a legal value for this property's type."""
```
- `enum`: `v in self.values` (case-sensitive)
- `bool`: `v in ("true", "false")`
- `long`: `v.lstrip("-").isdigit()`
- unknown type: `False` (reject)

### FR-3: OntologyManager.validate_fact()
```python
def validate_fact(self, fact: Fact) -> list[str]:
    """Return list of validation error strings. Empty = valid."""
```
- Unknown noun → error
- Unknown property on known noun → error
- Value fails `validate_value()` → error

### FR-4: Serialization
`to_dict()` emits `values` and `default` fields. `from_dict()` reads them with defaults `values=[]` and `default=None`.

## Non-Functional Requirements
- No new dependencies
- `string` type removed — properties must specify `enum`, `bool`, or `long`
- Validation errors are strings (not exceptions) for advisory use

## Proposed Approach

### Step 1: Extend OntologyProperty (models.py)
Add `values` and `default` fields. Update `to_dict()` and `from_dict()`. Add `validate_value()` method.

### Step 2: Add validate_fact to OntologyManager (ontology_manager.py)
New method that looks up the noun, finds the property, and calls `validate_value()`.

### Step 3: Unit Tests
- `test_models.py`: Add tests for `OntologyProperty` — all four types, edge cases
- `test_ontology_manager.py`: Add tests for `validate_fact()` — valid/invalid/missing noun/missing prop

### Step 4: Update ontology YAML if any exists
Currently no `ontology.yaml` file exists in `data/`. No migration needed yet.

## Alternatives Considered
1. **Separate TypeSchema model**: Rejected — adds complexity without benefit. OntologyProperty already has a `type` field.
2. **Validation as exceptions**: Rejected — advisory warnings are more useful for LLM extraction. Errors should be collectable strings.
3. **Case-insensitive enum matching**: Rejected — values should be exact. The ontology owner defines canonical casing.

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Existing YAML has `type: string` | Low | Medium | `validate_value()` rejects — must migrate to `enum`/`bool`/`long` |
| LLM generates values not in enum | Medium | Low | Validation is advisory during extraction; enforcement at confirm |

## Dependencies
- None (this is the foundation layer)
- EES-00017 depends on this

## Migration / Rollout / Rollback
- **Rollout**: Breaking change — `string` type removed. Deploy with awareness.
- **Rollback**: Revert models.py to restore `string` support.
- **Data migration**: Any existing YAML with `type: string` must be updated to `enum`/`bool`/`long`.

## Observability Plan
- N/A — internal model change, no runtime telemetry

## Test Strategy Summary
| Test | Description | Type |
|------|-------------|------|
| validate_value enum valid | Value in values list → True | Unit |
| validate_value enum invalid | Value not in list → False | Unit |
| validate_value bool valid | "true"/"false" → True | Unit |
| validate_value bool invalid | "yes" → False | Unit |
| validate_value long valid | "42", "-1" → True | Unit |
| validate_value long invalid | "abc" → False | Unit |
| validate_value invalid type | Unknown type → False | Unit |
| from_dict backward compat | Missing values/default → empty/None | Unit |
| to_dict round trip | Serialize + deserialize = same | Unit |
| validate_fact unknown noun | Returns error | Unit |
| validate_fact unknown prop | Returns error | Unit |
| validate_fact valid | Returns empty list | Unit |
| validate_fact invalid value | Returns error with detail | Unit |
