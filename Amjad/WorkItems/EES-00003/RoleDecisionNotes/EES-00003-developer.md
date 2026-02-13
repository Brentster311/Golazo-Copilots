# EES-00003 — Developer Decision Notes

## TDD Summary
- **RED phase:** 19 new tests written first (7 model, 3 fact_extractor, 3 rule_generator, 3 gap_detector, 4 main integration). 8 initially failed.
- **GREEN phase:** Implemented changes in 4 files. All 159 tests pass (140 existing + 19 new).
- **Coverage:** 98% (unchanged from baseline).

## Changes Made

### `src/ees/models.py`
- `Rule.type` Literal expanded from `"positive"` to `"positive" | "ruleout"`.
- Single-line change, fully backward compatible.

### `src/ees/fact_extractor.py`
- Extended `_SYSTEM_PROMPT` with RULEOUT rule format and example JSON schema.
- `_parse_response` now reads `r.get("type", "positive")` and passes it to `Rule()`.

### `src/ees/main.py`
- `_confirm_rules` display: RULEOUT rules show `THEN RULEOUT <name>` instead of `THEN RULEOUT(*).Target = <name>`.
- Summary output: `Rules: N positive, M ruleout generated` replaces generic `Rules: N generated`.
- Rule listing in summary also uses RULEOUT display format.

### `src/ees/gap_detector.py`
- `detect_gaps()` broadened: checks `then.noun.lower()` for both `"rootcause"` and `"ruleout"`.
- RULEOUT rule conditions are now considered "connected" to diagnostic reasoning.

## Files Unchanged
- `rule_generator.py` — dedup is type-agnostic (works on conditions + then dicts).
- `yaml_store.py` — already serializes all Rule fields including type.
- `ontology_manager.py`, `incident_loader.py`, `exceptions.py` — no interaction with rule types.

## Test Results
- 159 tests pass: 39 model + 9 fact_extractor + 19 rule_generator + 21 gap_detector + 6 incident_loader + 35+4 main + 7 ontology + 15 yaml_store
- 98% coverage
