# EES-00018 — Project Owner Assistant Decision Notes

## Origin
Third and final item from the schema brainstorm session. Addresses **observations 1 and 2**:

1. **Rules only rule out — where's the resolution?** Currently the engine loops until all rules are evaluated or a GAP fires. There's no "we found the answer" signal.
2. **Solution to what problem?** There's no explicit goal. The engine evaluates rules but doesn't know what question it's trying to answer.

## Key Design Decisions

### Goal as an Ontology Property
The goal is not a separate model — it's an `OntologyProperty` annotated with `is_goal: true`, `initial`, and `terminal`. This keeps the model count low and reuses existing typed-property infrastructure from EES-00016.

Example in ontology YAML:
```yaml
- name: Incident
  properties:
    - name: rootCause
      type: enum
      values: [unresolved, admin_role_missing, consent_not_granted, approval_pending, permission_denied, unknown]
      default: unresolved
      is_goal: true
      initial: unresolved
      terminal: [admin_role_missing, consent_not_granted, approval_pending, permission_denied, unknown]
```

### Two-Tier Rule Architecture
This item formalizes what emerged in the brainstorm:
- **Diagnostic rules** (existing): Check component states, emit CHANGE_STATE/RULED_OUT
- **Resolution rules** (new pattern, same model): Their CHANGE_STATE target is the goal property. They fire when enough diagnostic evidence exists to assign a root cause.

No new rule model is needed — a resolution rule is just a rule whose target happens to be the goal property.

### Three Terminal States
- `resolved` — a resolution rule fired and set the goal to a known terminal value
- `escalated` — a GAP rule fired (all known causes eliminated)
- `in_progress` — max iterations reached, inconclusive

## Dependency Chain
```
EES-00016 (typed ontology)
    └── EES-00017 (structured CHANGE_STATE)
            └── EES-00018 (this item — goal + termination)
```

## Backward Compatibility
If no goal property is declared in the ontology, the evaluator behaves exactly as it does today — iterates until no new rules fire. Goal-based termination is opt-in.
