# EES-00016 — Capability Impact Analysis

## Files Changed
- `src/ees/models.py` — `OntologyProperty` extended with `values`, `default`, `validate_value()`
- `src/ees/ontology_manager.py` — `validate_fact()` method added

## Directly Affected Capabilities
| Capability | Impact |
|---|---|
| data-models | `OntologyProperty` dataclass extended — additive only |
| ontology-management | New `validate_fact()` method — additive only |

## Transitively Affected Capabilities
| Capability | Impact | Risk |
|---|---|---|
| yaml-persistence | Serializes `OntologyProperty` — new fields have defaults, backward compatible | None |
| fact-extraction | Consumes ontology — may call `validate_fact()` in future (not in this item) | None |
| rule-generation | Uses ontology for dedup — unaffected | None |
| cli-orchestration | Calls evaluator — unaffected | None |
| rule-evaluation | Consumes rules/facts — unaffected | None |
| gui | Displays ontology — unaffected (reads via `to_dict()`) | None |

## Contract Compatibility
All existing contracts preserved. New fields have defaults. No method signatures changed.
