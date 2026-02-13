# Developer Decision Notes — EES-00007

## Implementation Summary
- Created `src/ees/gui/kusto_client.py` — KustoClient with `fetch_incident()` method
- Extended `src/ees/gui/settings.py` — added `load_kusto()`, `save_kusto()`, Kusto defaults
- Extended `src/ees/gui/app.py` — Incident ID field, Fetch from Kusto button, SettingsDialog Kusto section
- Added `azure-kusto-data>=4.0` to `pyproject.toml` dependencies
- Created `tests/test_kusto.py` — 9 tests (5 KustoClient, 4 SettingsManager Kusto)

## Key Decisions
1. **Import guard**: `try/except ImportError` for `azure-kusto-data` — Fetch button disabled if not installed
2. **`_execute_query` method**: Separated Kusto SDK interaction into a single method for easy mocking
3. **Input sanitization**: Regex `^[\w\-]+$` validates incident IDs before KQL query
4. **Section-preserving save**: Refactored `SettingsManager.save()` and added `_load_raw()`/`_write_raw()` helpers so saving Kusto settings doesn't clobber OpenAI settings and vice versa
5. **Worker thread**: Kusto fetch uses same `run_in_worker` pattern as LLM calls — non-blocking UI

## Test Results
- 226 tests pass (217 existing + 9 new)
- No regressions
