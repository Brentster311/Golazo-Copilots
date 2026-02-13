# EES-00003 — Capability Impact Analysis

## Files Changed
- `src/ees/models.py`
- `src/ees/fact_extractor.py`
- `src/ees/main.py`
- `src/ees/gap_detector.py`

## Capabilities Affected

| Capability | Impact | Contract Change |
|-----------|--------|----------------|
| data-models | `Rule.type` Literal expanded from `"positive"` to `"positive" \| "ruleout"` | No — `to_dict()`/`from_dict()` unchanged, backward compat via default |
| fact-extraction | Prompt extended, `_parse_response` reads `type` | No — `extract() -> LLMResponse` unchanged |
| cli-orchestration | Display + summary changes | No — `process_incident()` signature unchanged |

## Capabilities NOT Affected
- yaml-persistence — already serializes all Rule fields
- rule-generation — type-agnostic dedup
- ontology-management — no rule type interaction
- incident-loading — no rule type interaction

## Transitive Impact
- cli-orchestration depends on data-models, fact-extraction → both affected but contracts preserved
- No breaking changes to any capability contract
