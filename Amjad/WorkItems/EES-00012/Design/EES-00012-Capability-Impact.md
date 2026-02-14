# EES-00012 — Capability Impact Analysis

## Files in Design Scope

| File | Changes |
|------|---------|
| `src/ees/fact_extractor.py` | Add `on_status` callback parameter to `extract()` |
| `src/ees/gui/adapters.py` | Update `rules_to_rows()`, `eval_result_to_display()` for v2 |
| `src/ees/gui/app.py` | Add else column, update detail dialog, update eval display, wire status callback |
| `tests/test_fact_extractor.py` | Add tests for `on_status` callback |
| `tests/test_gui_adapters.py` | Add/update tests for v2 rule display |

## Directly Affected Capabilities

- **fact-extraction**: `on_status` param added to `extract()` — additive, backward compatible
- **gui**: Adapter outputs and display logic updated — internal presentation changes

## Transitively Affected Capabilities

- **cli-orchestration**: Depends on `fact-extraction`. No changes needed — doesn't use `on_status` or adapters directly.

## Contract Compatibility

| Capability | Contract | Status |
|-----------|----------|--------|
| fact-extraction | `extract(text, ontology, *, max_turns=10)` → `LLMResponse` | **Preserved** — `on_status` is additive keyword-only |
| gui | `rules_to_rows()` → `list[dict]` | **Extended** — adds `else` key to output dict |
| gui | `eval_result_to_display()` → `dict` | **Modified** — `outputs` replaces deprecated keys. Single consumer updated in lockstep |
| cli-orchestration | N/A | **Unaffected** |
