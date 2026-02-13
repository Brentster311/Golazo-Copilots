# EES-00002 — Capability Impact Analysis

**Work Item:** EES-00002 — GAP Rule Detection & Refinement  
**Date:** 2025-02-01

## Files Changed

| File | Change Type |
|------|-------------|
| `src/ees/models.py` | Modified — extend Rule model with GAP fields, add GapRefinement |
| `src/ees/rule_generator.py` | Modified — is_duplicate() skips GAP rules |
| `src/ees/main.py` | Modified — insert GAP detection/refinement steps |
| `src/ees/yaml_store.py` | No change needed — Rule.to_dict/from_dict handles serialization |
| `src/ees/gap_detector.py` | **New** — GapDetector class |

## Directly Affected Capabilities (4)

| Capability | Impact | Contract Change? |
|------------|--------|-----------------|
| **data-models** | Rule.status extended from `CONFIRMED` to `CONFIRMED\|GAP\|RESOLVED`. New optional fields: `requires`, `produces`, `note`. New `GapRefinement` dataclass. | Yes — `Rule.to_dict()` conditionally emits new fields. `Rule.from_dict()` handles missing fields via defaults. `Rule.is_duplicate_of()` unchanged. |
| **rule-generation** | `is_duplicate()` adds guard clause to skip GAP-status rules. | No contract change — same signature, refined behavior. |
| **cli-orchestration** | New workflow steps between rule confirmation and ontology update. New `_confirm_gaps()` function. GAP summary in output. | No contract change — `process_incident()` signature unchanged. |
| **yaml-persistence** | No code change. Rule serialization changes handled entirely by `Rule.to_dict()/from_dict()`. | No contract change. |

## Transitively Affected Capabilities (2)

| Capability | Impact | Action Required |
|------------|--------|----------------|
| **fact-extraction** | Depends on data-models. `LLMResponse` unchanged. `FactExtractor.extract()` unchanged. | None — no breaking changes to Fact or LLMResponse. |
| **ontology-management** | Depends on data-models. `OntologyManager.update_from_facts()` uses Fact model. | None — Fact model unchanged. |

## New Capability

| Capability | Description |
|------------|-------------|
| **gap-detection** | Detects orphaned facts and creates GAP rules; refines existing GAPs when new rules overlap. Key file: `src/ees/gap_detector.py`. Depends on: data-models. |

## Contract Compatibility

All changes are additive:
- New optional fields on Rule with sensible defaults
- New type on Rule.status (extends, doesn't break)
- New guard clause in is_duplicate (narrows, doesn't break)
- Existing tests for CONFIRMED rules remain valid without modification

## Risk Assessment

| Risk | Level |
|------|-------|
| Existing CONFIRMED rule YAML files load without issues | Low — from_dict() uses .get() defaults |
| Rule.to_dict() backward compat | Low — new fields omitted when empty |
| is_duplicate() behavior change | Low — only affects GAP-status rules which don't exist yet |
| process_incident() flow disruption | Medium — careful step insertion needed, covered by tests |
