# Design Doc: LLM-0002 — Configuration Management with JSON/YAML Persistence

**Work Item:** LLM-0002  
**Author:** Program Manager  
**Date:** 2026-02-07  
**Status:** DRAFT

---

## 1. Summary

Build a `LLMConfig` dataclass that holds all non-sensitive library configuration, with methods to load from and save to JSON/YAML files. Security artifacts are explicitly excluded from persistence — loading a file that contains secret fields raises an error or strips them with a warning.

## 2. Problem Statement

Developers need a structured, type-safe way to configure the LLM Extender library. Configuration should be shareable across environments (dev, staging, prod) via human-readable files, but secret values must never appear on disk.

## 3. Business Case

| Dimension | Detail |
|---|---|
| **Why now** | Config is foundational — LLM-0001 and LLM-0003 both depend on a structured config shape |
| **Impact** | Reduces boilerplate; enables environment-specific config files without security risk |
| **KPIs** | N/A for library — success = passing tests |

## 4. Stakeholders

| Role | Interest |
|---|---|
| Library consumers | Type-safe config with file persistence |
| LLM-0001 | Uses config for provider/model selection |
| LLM-0003 | Uses config for auth strategy type (not credentials) |

## 5. Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `LLMConfig` dataclass with provider, model, auth_strategy, base_url, extra params | AC-1 |
| FR-2 | `LLMConfig.from_json(path)` class method | AC-2 |
| FR-3 | `LLMConfig.from_yaml(path)` class method | AC-3 |
| FR-4 | `config.to_json(path)` and `config.to_yaml(path)` instance methods | AC-4 |
| FR-5 | Secret fields excluded from serialized output | AC-5 |
| FR-6 | `__repr__` and `__str__` mask secret values | AC-6 |
| FR-7 | Loading a file with secret fields raises `SecretInConfigError` or strips with warning | AC-7 |

## 6. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | JSON support with stdlib only (no extra deps) |
| NFR-2 | YAML support via optional `pyyaml` dependency |
| NFR-3 | Type hints on all public surfaces |
| NFR-4 | Python 3.10+ compatibility |

## 7. Proposed Approach

### 7.1 Package Structure (additions to llm_extender/)

```
llm_extender/
├── config.py            # LLMConfig dataclass, load/save, secret guard
└── exceptions.py        # SecretInConfigError (added)
```

### 7.2 LLMConfig Dataclass

```
@dataclass
class LLMConfig:
    provider: str                    # e.g., "openai"
    model: str                       # e.g., "gpt-4"
    auth_strategy: str               # e.g., "env_var", "msi", "callback"
    base_url: str | None = None      # Optional endpoint override
    extra: dict[str, Any] = field(default_factory=dict)  # Provider-specific params
```

### 7.3 Secret Field Guard

A constant set of known secret field names:

```python
SECRET_FIELD_NAMES = frozenset({"api_key", "token", "secret", "password", "credential", "key"})
```

- **On load:** If any top-level key in the parsed file matches `SECRET_FIELD_NAMES`, raise `SecretInConfigError` with a message identifying the offending field(s).
- **On save:** Only serialize the known safe fields (`provider`, `model`, `auth_strategy`, `base_url`, `extra`). Any transient runtime fields are excluded by design since they're not dataclass fields.
- **On repr/str:** `__repr__` returns field names and safe values only. No secret masking needed in this story since `LLMConfig` has no secret fields by design — secrets live in auth (LLM-0003).

### 7.4 JSON Load/Save

```python
@classmethod
def from_json(cls, path: str | Path) -> "LLMConfig":
    ...  # json.load → validate no secrets → construct

def to_json(self, path: str | Path) -> None:
    ...  # dataclasses.asdict → json.dump
```

### 7.5 YAML Load/Save

```python
@classmethod
def from_yaml(cls, path: str | Path) -> "LLMConfig":
    ...  # yaml.safe_load → validate no secrets → construct

def to_yaml(self, path: str | Path) -> None:
    ...  # dataclasses.asdict → yaml.dump
```

YAML methods raise `ImportError` with a helpful message if `pyyaml` is not installed.

## 8. Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Pydantic `BaseModel` instead of dataclass | Heavier dependency; stdlib dataclass is sufficient |
| TOML support | `tomllib` is read-only in stdlib (3.11+); adding `tomli-w` for write is scope creep |
| Encrypt secret fields in config file | Out of scope; adds complexity and key-management concerns |
| Allow secrets in config with encryption | User explicitly said "do not store security artifacts" |

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| User puts secrets in `extra` dict | Medium | High | Document that `extra` is for non-sensitive provider params only; future: scan `extra` values |
| `pyyaml` not installed when YAML used | Medium | Low | Clear `ImportError` message with install instructions |
| Config format evolves across versions | Low | Medium | Include a `version` field in serialized config for future migration |

## 10. Dependencies

| Dependency | Direction | Detail |
|---|---|---|
| LLM-0001 | Backward | LLM-0001 defines the initial minimal config; this story extends it |
| LLM-0003 | Forward | Auth strategy type is a string in config; auth manager resolves credentials |
| `pyyaml` | External (optional) | Required only for YAML support |

## 11. Migration / Rollout / Rollback

- **New library** — no migration
- **Rollback:** Revert package version

## 12. Observability Plan

- None for initial version

## 13. Test Strategy Summary

| Layer | What | How |
|---|---|---|
| Unit | `LLMConfig` round-trips through JSON save/load | Create config → save → load → assert equality |
| Unit | `LLMConfig` round-trips through YAML save/load | Create config → save → load → assert equality |
| Unit | Loading a file with secret fields raises `SecretInConfigError` | Write a JSON file with `api_key` → load → assert raises |
| Unit | Saving never includes secret field names | Save → read raw file → assert no secret keys present |
| Unit | `__repr__` does not contain secret values | `repr(config)` → assert no secret patterns |
| Unit | YAML methods raise `ImportError` when pyyaml missing | Mock import → assert helpful error |
