# EES-00016 — Program Manager Decision Notes

## Design Approach
Chose the minimal extension approach: add fields to existing `OntologyProperty` rather than introducing a new model. This keeps the change surface small and the dependency chain clean.

## Key Tradeoffs
- **Advisory vs. enforced validation**: Validation returns error strings, not exceptions. This is deliberate — the LLM extractor needs to propose facts that may use values the ontology doesn't know about yet. Enforcement happens when the user explicitly confirms a fact.
- **Four types only**: `string`, `enum`, `bool`, `long`. No `float` or `date` — YAGNI. Can always add later since the type field is a string, not a closed enum.
- **Case-sensitive enum values**: The ontology owner picks canonical casing. Matching is exact. This avoids ambiguity and keeps the validation logic trivial.

## Staging
This is a single-step implementation — no phased rollout needed. The change is purely additive to two files (`models.py`, `ontology_manager.py`) plus tests.
