# Developer Notes — GCP-0040

## Summary
Added `capabilities-template.yaml` as a package resource and integrated it into `gcp_bootstrap`.

## Changes
1. **New file**: `src/golazo_copilot/capabilities-template.yaml` — self-documenting YAML template with comment header, schema description, and one example capability
2. **Modified**: `src/golazo_copilot/tools/gcp_bootstrap.py` — added capabilities.yaml creation block after `.gitkeep`, follows same skip/force pattern, wrapped in try/except
3. **New tests**: 7 tests in `TestBootstrapCapabilitiesTemplate` class in `test_gcp_bootstrap.py`

## Test Results
177 passed (was 170)
