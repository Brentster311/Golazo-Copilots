# EES-00006 — Test Cases

## Unit Tests: SettingsManager

### TC-1: Load settings from YAML file
- **Input:** `settings.yaml` exists with `azure_openai.endpoint: "https://test.openai.azure.com/"`
- **Expected:** `load()` returns dict with endpoint = `"https://test.openai.azure.com/"`

### TC-2: Load returns defaults when no file exists
- **Input:** No `settings.yaml` file
- **Expected:** `load()` returns built-in defaults (endpoint=`https://open-ai-poc.openai.azure.com/`, deployment=`gpt5.2`, api_version=`2025-12-11`)

### TC-3: Save creates settings.yaml
- **Input:** `save(data_dir, {"endpoint": "https://x.openai.azure.com/", "deployment": "gpt-4o", "api_version": "2025-01-01"})`
- **Expected:** `settings.yaml` written with correct YAML structure

### TC-4: Env var overrides default
- **Input:** No `settings.yaml`, env var `AZURE_OPENAI_ENDPOINT` set to `"https://env.openai.azure.com/"`
- **Expected:** `get_effective("endpoint")` returns `("https://env.openai.azure.com/", "env")`

### TC-5: Config overrides env var
- **Input:** `settings.yaml` has endpoint, env var `AZURE_OPENAI_ENDPOINT` also set
- **Expected:** `get_effective("endpoint")` returns the config value with source `"config"`

### TC-6: Blank config field falls back to env var
- **Input:** `settings.yaml` has endpoint = `""`, env var `AZURE_OPENAI_ENDPOINT` set
- **Expected:** `get_effective("endpoint")` returns the env var value with source `"env"`

### TC-7: Get effective returns source "default"
- **Input:** No config, no env var
- **Expected:** `get_effective("endpoint")` returns default with source `"default"`

### TC-8: Save and reload round-trip
- **Input:** Save settings, then load — values match

## Unit Tests: FactExtractor kwargs

### TC-9: FactExtractor accepts endpoint/deployment/api_version kwargs
- **Input:** `FactExtractor(endpoint="https://x/", deployment="gpt-4o", api_version="2025-01-01")`
- **Expected:** Client created with those values (no env var lookup)

### TC-10: FactExtractor kwargs=None falls back to env vars
- **Input:** `FactExtractor()` with env vars set
- **Expected:** Existing behavior unchanged

## Manual Tests: Settings Dialog

### TC-11: Dialog opens from File menu
- **Steps:** File → Settings
- **Expected:** Modal dialog appears with three fields

### TC-12: Dialog pre-fills effective values
- **Steps:** Set env vars, open Settings
- **Expected:** Fields show env var values with "(from env)" labels

### TC-13: Save and relaunch
- **Steps:** Enter values in dialog, click Save, close and relaunch app, open Settings
- **Expected:** Saved values shown with "(from config)" labels

### TC-14: Extract uses saved settings
- **Steps:** Save settings via dialog, load incident, click Extract Facts
- **Expected:** LLM call uses the saved endpoint/deployment
