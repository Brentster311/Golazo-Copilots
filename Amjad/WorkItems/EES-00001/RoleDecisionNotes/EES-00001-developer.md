# EES-00001 — Developer Decision Notes

## Summary
Implemented the core learning loop per the design doc. TDD approach: wrote 66 tests first (red phase), then implemented production code until all passed (green phase).

## Implementation Inventory

### Production Code
| Module | Purpose | Lines |
|--------|---------|-------|
| `src/ees/models.py` | Dataclasses: Fact, Rule, Incident, OntologyNoun, RootCause, LLMResponse | ~230 |
| `src/ees/yaml_store.py` | YAML persistence: atomic read/write for all data files, ID generation | ~130 |
| `src/ees/ontology_manager.py` | Ontology CRUD: case-insensitive matching, update from confirmed facts | ~60 |
| `src/ees/incident_loader.py` | File loading + validation: not found, empty, binary, >500KB warning | ~55 |
| `src/ees/fact_extractor.py` | Azure OpenAI integration: ChainedTokenCredential auth, JSON mode, retry | ~170 |
| `src/ees/rule_generator.py` | Rule dedup + filtering: exact duplicate check, confirmed-fact matching | ~55 |
| `src/ees/main.py` | CLI entry point: argparse, two-phase confirmation flow, full workflow | ~230 |

### Test Code
| Test Module | Test Count | Covers |
|-------------|------------|--------|
| `tests/test_models.py` | 26 | Fact parsing, serialization, operators, Rule dedup |
| `tests/test_yaml_store.py` | 17 | Incident/rule/ontology/rootcause YAML I/O, ID generation, validation |
| `tests/test_ontology_manager.py` | 7 | Case-insensitive matching, new entries, mixed scenarios |
| `tests/test_incident_loader.py` | 5 | File not found, empty, binary, large file, happy path |
| `tests/test_fact_extractor.py` | 6 | LLM extraction, empty response, API failure, retry, auth verification |
| `tests/test_rule_generator.py` | 5 | Rule fields, flat logic, instance preservation, dedup, empty facts |
| **Total** | **66** | All 7 acceptance criteria covered |

### Test Fixtures
- `tests/fixtures/sample_incident.txt` — realistic incident report
- `tests/fixtures/mock_llm_response.json` — valid LLM JSON response
- `tests/fixtures/mock_llm_empty.json` — empty facts/rules LLM response
- `tests/fixtures/mock_llm_malformed.txt` — unparseable LLM output

## Key Decisions

### DD-1: Azure OpenAI Auth
Used `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())` per TechBestPractices.md. The `_make_token_provider` wrapper creates a callable that `AzureOpenAI` accepts as `azure_ad_token_provider`.

### DD-2: ruamel.yaml over PyYAML
`ruamel.yaml.YAML()` with `default_flow_style=False` for clean block-style output. Round-trips preserve structure.

### DD-3: Windows-compatible tests
The readonly directory test (TC-24) was adapted for Windows — `os.chmod` doesn't enforce directory permissions on Windows. Changed to test writing to a nonexistent directory instead.

### DD-4: Fact parsing regex
`FACT_PATTERN` handles all valid operators including multi-char ones (`contains`, `!contains`, `>=`, `<=`). Ordered to match `>=` before `>` in the alternation.

### DD-5: Two-phase confirmation in CLI
Phase 1: Confirm/edit/reject/specialize individual facts.
Phase 2: Confirm/edit/reject proposed rules.
Root cause confirmation is c/e/r only (not parameterized, per architect decision AD-7).

## Test Results
```
66 passed in 0.97s
```

All acceptance criteria covered. No design flaws discovered during implementation.
