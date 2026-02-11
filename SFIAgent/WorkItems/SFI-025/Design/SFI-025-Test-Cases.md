# SFI-025 — Test Cases

## Test Case Mapping to Acceptance Criteria

| AC | Test Case(s) |
|----|-------------|
| Configure LLM button visible | TC-01 |
| Dialog opens with fields | TC-02, TC-03 |
| Auto-detect happy path | TC-04, TC-05 |
| Auto-detect errors | TC-06, TC-07, TC-08 |
| Save persists config | TC-09 |
| Config loads on LLM analysis | TC-10, TC-11 |
| Pre-populated on reopen | TC-12 |

---

## TC-01: Configure LLM button exists on main screen

**Type**: Unit  
**Scenario**: App starts → controls row contains "Configure LLM" button  
**Expected**: Button with text "Configure LLM" is present in the controls frame  
**Failure message**: "Expected 'Configure LLM' button in controls row"

## TC-02: Dialog opens with empty fields (no saved config)

**Type**: Unit  
**Scenario**: No saved LLM config → click Configure LLM → dialog opens  
**Expected**: Endpoint field is empty, Deployment shows "gpt-4o", API Version shows "2024-10-21"  
**Failure message**: "Expected default field values when no config saved"

## TC-03: Dialog opens with saved config pre-populated

**Type**: Unit  
**Scenario**: Saved config exists (endpoint=`https://my.openai.azure.com/`, deployment=`gpt-35`, api_version=`2025-01-01`) → open dialog  
**Expected**: Fields pre-populated with saved values  
**Failure message**: "Expected dialog fields to match saved config"

## TC-04: Auto-detect happy path — configs discovered

**Type**: Unit (mock `discover_azure_configs`)  
**Scenario**: Click Auto-detect → returns 2 configs  
**Expected**: Combobox populated with 2 items, each showing endpoint + deployment  
**Failure message**: "Expected discovered configs in selection dropdown"

## TC-05: Auto-detect selection populates fields

**Type**: Unit  
**Scenario**: Discovered configs in dropdown → user selects one  
**Expected**: Endpoint, Deployment, and API Version fields populated from selected config  
**Failure message**: "Expected fields to populate from selected discovered config"

## TC-06: Auto-detect — no configs found

**Type**: Unit (mock returns empty list)  
**Scenario**: Click Auto-detect → returns `[]`  
**Expected**: Info message displayed: "No Azure OpenAI deployments found"  
**Failure message**: "Expected info message when no configs discovered"

## TC-07: Auto-detect — ImportError (missing SDK)

**Type**: Unit (mock raises `ImportError`)  
**Scenario**: Click Auto-detect → `ImportError` raised  
**Expected**: Error message mentioning SDK installation  
**Failure message**: "Expected ImportError to show SDK install instructions"

## TC-08: Auto-detect — other error

**Type**: Unit (mock raises `Exception`)  
**Scenario**: Click Auto-detect → generic exception  
**Expected**: Error message displayed with exception text  
**Failure message**: "Expected error message for discovery failure"

## TC-09: Save persists config to settings.json

**Type**: Unit  
**Scenario**: Enter endpoint + deployment + api_version → click Save  
**Expected**: `_load_setting('llm_endpoint')` returns the saved endpoint; same for deployment and api_version. Dialog closes.  
**Failure message**: "Expected config to persist to settings.json after Save"

## TC-10: LLM analysis uses saved config over env vars

**Type**: Unit  
**Scenario**: Saved config has endpoint `https://saved.openai.azure.com/` → launch LLM analysis  
**Expected**: Analysis uses saved endpoint, not env var  
**Failure message**: "Expected saved config to take priority over env vars"

## TC-11: LLM analysis falls back to env vars when no saved config

**Type**: Unit  
**Scenario**: No saved LLM config → env vars set → launch LLM analysis  
**Expected**: Analysis uses `LLMConfig.from_env()`  
**Failure message**: "Expected fallback to env vars when no saved config"

## TC-12: Clear button removes saved config

**Type**: Unit  
**Scenario**: Saved config exists → open dialog → click Clear  
**Expected**: Fields reset to defaults, `_load_setting('llm_endpoint')` returns default (empty)  
**Failure message**: "Expected Clear to remove saved config and reset fields"

## TC-13: Save validates endpoint format

**Type**: Unit  
**Scenario**: Enter endpoint without `https://` → click Save  
**Expected**: Validation error shown, config NOT saved  
**Failure message**: "Expected validation error for invalid endpoint URL"
