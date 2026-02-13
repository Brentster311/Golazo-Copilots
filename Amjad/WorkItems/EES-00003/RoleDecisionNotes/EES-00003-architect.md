# EES-00003 — Architect Decision Notes

## Architectural Decisions

### A-1: RULEOUT + GAP Combination is Valid
RULEOUT rules can have status GAP. A RULEOUT GAP means "something eliminates root cause X, but we don't know the full intermediate reasoning." The `type` and `status` fields are orthogonal dimensions.

### A-2: RULEOUT Conditions Count as Connected for GAP Detection
Facts consumed by RULEOUT rules are diagnostically relevant and should not be flagged as orphaned. `detect_gaps()` broadened to check `then.noun.lower() in ("rootcause", "ruleout")`.

### A-3: then Convention for RULEOUT
`then = RuleThen(noun="RULEOUT", instance="*", property="Target", value=<RootCauseName>)`. This reuses the existing `RuleThen` structure without model changes while making RULEOUT rules clearly distinguishable in YAML.

### A-4: Backward Compatibility
`Rule.from_dict()` already uses `.get("type", "positive")`. All existing rules load without changes.

### A-5: rootcauses.yaml Isolation Confirmed
Root cause creation path uses `_confirm_root_cause()` result, not rule `then` values. No risk of RULEOUT rules creating root cause entries.

## QA Findings Resolution
- MJ-1: Resolved — RULEOUT + GAP is valid
- MJ-2: Resolved — RULEOUT conditions count as connected
- MN-1: Confirmed — display reads `rule.then.value`
- MN-2: Confirmed — no code change needed
- MN-3: Resolved — summary format: `N positive, M ruleout generated`

## Files to Modify
1. `src/ees/models.py` — `Rule.type` Literal expansion
2. `src/ees/fact_extractor.py` — Prompt extension + `_parse_response` type field
3. `src/ees/main.py` — RULEOUT display + summary
4. `src/ees/gap_detector.py` — Connected-fact broadening

## Files Unchanged
- `src/ees/rule_generator.py` — type-agnostic dedup
- `src/ees/yaml_store.py` — already serializes all Rule fields
- `src/ees/ontology_manager.py` — no rule type interaction
- `src/ees/incident_loader.py` — no rule type interaction
