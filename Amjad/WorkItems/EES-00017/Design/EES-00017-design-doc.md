# EES-00017 — Design Doc: Structured RuleOutput with Typed State Transitions

## Summary
Replace the free-text `description` field on `CHANGE_STATE` rule outputs with structured `target` (noun, instance, property) and `value` fields. This makes state mutations machine-readable, validates them against the typed ontology (EES-00016), and eliminates the need to parse description strings like `"User.adminRole => confirmed"`.

## Problem Statement
Today every `RuleOutput` — regardless of kind — stores its payload as a single `description: str`. For `CHANGE_STATE` outputs this means:
- The engine's `to_fact()` method creates a pseudo-fact `Fact(noun="CHANGE_STATE", property=description, ...)` which doesn't directly mutate ontology state
- Rule authors write narrative strings like `"User.adminRole => confirmed"` that can't be validated
- No connection between the output and the typed ontology — the value `"confirmed"` is never checked against `OntologyProperty.validate_value()`
- The `CHANGE_STATE` description format is inconsistent across rules (some use `=>`, some use `=`, some omit the noun)

## Business Case
- **Why now**: EES-00016 just landed typed ontology properties. The typed values are useless unless outputs actually write validated values.
- **Impact**: Rules produce machine-verifiable state mutations. Rule authoring errors caught at definition time.
- **KPIs**: All `CHANGE_STATE` outputs in the rule YAML files are structurally valid against the ontology.

## Stakeholders
- Knowledge engineers (authoring rules with structured outputs)
- Rule evaluator engine (consuming structured state transitions)
- GUI (displaying structured output details)

## Functional Requirements

### FR-1: Extend RuleOutput with optional structured fields
```python
@dataclass
class RuleOutput:
    kind: Literal["CHANGE_STATE", "RULED_OUT", "GAP"]
    description: str                           # kept for RULED_OUT / GAP
    target_noun: str | None = None             # NEW (CHANGE_STATE only)
    target_instance: str | None = None         # NEW (CHANGE_STATE only)
    target_property: str | None = None         # NEW (CHANGE_STATE only)
    value: str | None = None                   # NEW (CHANGE_STATE only)
```

Design choice: flat fields rather than a nested `target: dict`. This keeps the dataclass simple, avoids an inner class, and makes serialization straightforward. The four fields are only used when `kind == "CHANGE_STATE"`.

### FR-2: RuleOutput.to_fact() — structured path
When `target_noun` is set (structured output):
```python
Fact(noun=target_noun, instance=target_instance or "*",
     property=target_property, operator="==", value=value)
```
When `target_noun` is None (legacy):
```python
Fact(noun=self.kind, instance="*", property=self.description,
     operator="==", value="true")  # current behavior
```

### FR-3: RuleOutput.validate(ontology_manager) -> list[str]
For `CHANGE_STATE` with structured fields:
1. Look up `target_noun` in ontology → error if missing
2. Look up `target_property` on that noun → error if missing
3. Call `OntologyProperty.validate_value(value)` → error if invalid

For `RULED_OUT`/`GAP` or legacy `CHANGE_STATE` (no target): return `[]` (no validation).

### FR-4: Serialization
**New format** (structured CHANGE_STATE):
```yaml
then:
  kind: CHANGE_STATE
  target_noun: User
  target_instance: $u
  target_property: adminRole
  value: confirmed
```

**Legacy format** (description-based — still loads):
```yaml
then:
  kind: CHANGE_STATE
  description: User.adminRole => confirmed
```

`from_dict()` detects structured vs. legacy by checking for `target_noun` key.
`to_dict()` emits structured fields when present; otherwise emits `description`.

### FR-5: Rule evaluator integration
No changes to `rule_evaluator.py` needed — it already calls `output.to_fact()`, which will now produce proper ontology-targeted facts for structured outputs.

## Non-Functional Requirements
- No new dependencies
- Legacy rule YAML files load unchanged (backward compatible)
- New-format rules are not backward-compatible with pre-EES-00017 code (acceptable — internal tool)

## Proposed Approach

### Step 1: Extend RuleOutput (models.py)
Add `target_noun`, `target_instance`, `target_property`, `value` fields. Update `to_dict()`, `from_dict()`, `to_fact()`. Add `validate()` method.

### Step 2: Unit Tests
- Structured `to_fact()` produces correct `Fact`
- Legacy `to_fact()` unchanged
- Structured `validate()` catches unknown noun, unknown property, invalid value
- Legacy `validate()` returns no errors
- Serialization round-trip for both formats
- `from_dict()` handles both structured and legacy

### Step 3: Migrate existing rule YAML files (R-001 through R-004)
Convert `CHANGE_STATE` descriptions to structured format. Leave `RULED_OUT` descriptions as-is.

## Alternatives Considered
1. **Nested `target: dict`**: Rejected — adds serialization complexity and an anonymous inner structure without benefit. Flat fields are explicit.
2. **Separate `ChangeStateOutput` subclass**: Rejected — introduces polymorphism in a dataclass-based system. Flat optional fields are simpler.
3. **Remove `description` entirely from CHANGE_STATE**: Rejected — some CHANGE_STATE outputs may be too complex for structured fields. Keep description as optional documentation.

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GUI code reads `description` directly for CHANGE_STATE display | Medium | Low | GUI falls back to `description` if no structured fields; test gui_adapters |
| LLM extractor produces old-format outputs | Medium | Low | Extractor change is out of scope — `from_dict` handles legacy format |
| Existing tests break due to new fields | Low | Low | New fields default to None — existing constructors still work |

## Dependencies
- EES-00016 (typed ontology) — IMPLEMENTED ✓

## Migration / Rollout / Rollback
- **Rollout**: Additive fields on `RuleOutput`. Legacy YAML loads unchanged.
- **Rollback**: Revert models.py. Structured YAML fields are ignored by old `from_dict`.
- **Data migration**: Update R-001 through R-004 CHANGE_STATE outputs to structured format.

## Observability Plan
- N/A — internal model change

## Capability Impact
- **Directly affected**: `data-models`, `rule-evaluation`
- **Transitively affected**: `yaml-persistence`, `fact-extraction`, `rule-generation`, `cli-orchestration`, `gui`
- All changes are additive (new optional fields). Transitive consumers won't break unless they explicitly access the new fields.

## Test Strategy Summary
| Test | Description | Type |
|------|-------------|------|
| structured to_fact | Produces Fact with noun/instance/property/value | Unit |
| legacy to_fact | Unchanged behavior (kind as noun, description as property) | Unit |
| validate valid | Known noun, known prop, legal value → [] | Unit |
| validate unknown noun | → error | Unit |
| validate unknown property | → error | Unit |
| validate invalid value | → error | Unit |
| validate legacy | No target → [] | Unit |
| to_dict structured | Emits target_noun/target_instance/target_property/value | Unit |
| to_dict legacy | Emits description only | Unit |
| from_dict structured | Reads target fields | Unit |
| from_dict legacy | Reads description, no target fields | Unit |
| round-trip | Serialize + deserialize = same | Unit |
| RULED_OUT unchanged | Still uses description, validate returns [] | Unit |
