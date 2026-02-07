# Test Cases: LLM-0002

**Work Item:** LLM-0002  
**Author:** Quality Assurance  
**Date:** 2026-02-07

---

## Test Framework
- `pytest`
- `tmp_path` fixture for file I/O

## Test File Structure
```
tests/
├── test_config.py           # LLMConfig tests
└── conftest.py              # Shared fixtures
```

---

## TC-1: LLMConfig dataclass has required fields (AC-1)

| Field | Value |
|---|---|
| **Type** | Unit — Structural |
| **Given** | `LLMConfig` class |
| **When** | Creating `LLMConfig(provider="openai", model="gpt-4", auth_strategy="env_var")` |
| **Then** | Instance has `provider`, `model`, `auth_strategy`, `base_url`, `extra` fields |
| **Failure message** | `"LLMConfig should have all required fields"` |

## TC-2: Config round-trips through JSON (AC-2, AC-4)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path |
| **Given** | A `LLMConfig` instance |
| **When** | `config.to_json(path)` then `LLMConfig.from_json(path)` |
| **Then** | Loaded config equals original |
| **Failure message** | `"Config should round-trip through JSON without data loss"` |

## TC-3: Config round-trips through YAML (AC-3, AC-4)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path |
| **Given** | A `LLMConfig` instance |
| **When** | `config.to_yaml(path)` then `LLMConfig.from_yaml(path)` |
| **Then** | Loaded config equals original |
| **Failure message** | `"Config should round-trip through YAML without data loss"` |

## TC-4: Saved JSON file does not contain secret field names (AC-5)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | A `LLMConfig` instance saved to JSON |
| **When** | Reading the raw JSON file content |
| **Then** | No key in the JSON matches `SECRET_FIELD_NAMES` |
| **Failure message** | `"Saved config file must never contain secret field names"` |

## TC-5: Saved YAML file does not contain secret field names (AC-5)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | A `LLMConfig` instance saved to YAML |
| **When** | Reading the raw YAML file content |
| **Then** | No key in the YAML matches `SECRET_FIELD_NAMES` |
| **Failure message** | `"Saved config file must never contain secret field names"` |

## TC-6: Loading a file with api_key field raises SecretInConfigError (AC-7)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | A JSON file containing `{"provider": "openai", "model": "gpt-4", "api_key": "sk-123"}` |
| **When** | `LLMConfig.from_json(path)` is called |
| **Then** | Raises `SecretInConfigError` with message identifying `api_key` |
| **Failure message** | `"Loading config with secret field 'api_key' should raise SecretInConfigError"` |

## TC-7: Loading a file with token field raises SecretInConfigError (AC-7)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | A JSON file containing `{"provider": "openai", "model": "gpt-4", "token": "abc"}` |
| **When** | `LLMConfig.from_json(path)` is called |
| **Then** | Raises `SecretInConfigError` with message identifying `token` |
| **Failure message** | `"Loading config with secret field 'token' should raise SecretInConfigError"` |

## TC-8: repr() does not expose secrets (AC-6)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | A `LLMConfig` instance |
| **When** | `repr(config)` is called |
| **Then** | Output contains no values matching common secret patterns |
| **Failure message** | `"repr() must not expose any secret values"` |

## TC-9: YAML methods raise ImportError when pyyaml not installed

| Field | Value |
|---|---|
| **Type** | Unit — Error Case |
| **Given** | `pyyaml` is not importable (mocked) |
| **When** | `LLMConfig.from_yaml(path)` is called |
| **Then** | Raises `ImportError` with message mentioning `pyyaml` |
| **Failure message** | `"YAML methods should raise ImportError with install instructions when pyyaml is missing"` |

## TC-10: Config with extra dict round-trips correctly

| Field | Value |
|---|---|
| **Type** | Unit — Edge Case |
| **Given** | Config with `extra={"temperature": 0.7, "max_tokens": 100}` |
| **When** | Save to JSON → load |
| **Then** | `extra` dict is preserved |
| **Failure message** | `"extra dict should be preserved through serialization"` |

## TC-11: Loading config with secret in extra dict is detected

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | A JSON file with `{"provider":"openai","model":"gpt-4","auth_strategy":"env_var","extra":{"api_key":"sk-123"}}` |
| **When** | `LLMConfig.from_json(path)` is called |
| **Then** | Raises `SecretInConfigError` |
| **Failure message** | `"Secrets in extra dict should also be detected"` |

---

## Acceptance Criteria Coverage Matrix

| AC | Test Cases |
|---|---|
| AC-1: LLMConfig fields | TC-1 |
| AC-2: Load from JSON | TC-2 |
| AC-3: Load from YAML | TC-3 |
| AC-4: Save to JSON/YAML | TC-2, TC-3, TC-4, TC-5 |
| AC-5: No secrets in persisted files | TC-4, TC-5 |
| AC-6: repr/str mask secrets | TC-8 |
| AC-7: Secret field detection on load | TC-6, TC-7, TC-11 |
