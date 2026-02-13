# EES-00003 — Program Manager Decision Notes

## Design Decisions

### D-1: RULEOUT Stored as Rule with type="ruleout"
RULEOUT rules reuse the existing `Rule` dataclass with `type="ruleout"` and a convention for `then`: `noun="RULEOUT"`, `instance="*"`, `property="Target"`, `value=<RootCauseName>`. This avoids creating a separate model class while keeping RULEOUT rules distinguishable in YAML output.

### D-2: LLM Prompt Extension (not replacement)
The existing `_SYSTEM_PROMPT` is extended with RULEOUT format and examples. The LLM returns both positive and RULEOUT rules in the same `rules` array with a `type` field.

### D-3: rootcauses.yaml Not Modified by RULEOUT
RULEOUT rules reference existing root cause names but do not create new root cause entries. This prevents RULEOUT rules from polluting the root cause registry.

### D-4: GAP Detector Broadened
`detect_gaps()` expands its "connected to root cause" check to include rules where `then.noun` is "RULEOUT" (in addition to "RootCause"). This ensures RULEOUT rule condition facts are not falsely flagged as orphaned.

### D-5: No Changes to yaml_store, rule_generator, ontology_manager
These components are type-agnostic — they serialize/deserialize/deduplicate based on structure, not type semantics.

## Risks Addressed
- Backward compatibility via default type="positive" in from_dict().
- RULEOUT display uses distinct format in CLI confirmation flow.

## Files Affected
- `src/ees/models.py` — Rule.type Literal expansion
- `src/ees/fact_extractor.py` — Prompt + _parse_response
- `src/ees/main.py` — Display, summary, rootcause exclusion
- `src/ees/gap_detector.py` — Connected-fact broadening
