# EES-00017 — Project Owner Assistant Decision Notes

## Origin
Continues from the schema brainstorm that produced EES-00016, EES-00017, EES-00018. This item addresses **observation 4 (continued)** — the rule output layer.

Currently `RuleOutput` carries:
```python
kind: Literal["CHANGE_STATE", "RULED_OUT", "GAP"]
description: str  # e.g., "User.adminRole => confirmed"
```

The `description` field is:
- Free text — no validation possible
- Uses past-tense narrative ("granted", "confirmed", "completed") instead of typed enum/bool values
- Requires string parsing to extract the target property and new value

## Key Design Decision: Only CHANGE_STATE Gets Structured Targets
- `CHANGE_STATE` mutates state → needs a structured target + validated value
- `RULED_OUT` is a signal ("we checked X and it's not the cause") → description is fine
- `GAP` is an escalation signal → description is fine

This keeps the change focused and avoids over-engineering the signal types.

## Dependency
Requires EES-00016 (typed ontology) to validate that output values are legal for the target property.

## Migration Strategy
Old YAML format:
```yaml
then:
  kind: CHANGE_STATE
  description: "User.adminRole => confirmed"
```

New YAML format:
```yaml
then:
  kind: CHANGE_STATE
  target:
    noun: User
    instance: $u
    property: directoryRole
  value: global_admin
```

`from_dict()` detects which format is present and loads accordingly. Old format emits a deprecation log entry but works.
