# LLM Extender — Architecture Overview

## Project Summary

**LLM Extender** is a provider-agnostic Python library (3.10+) that gives developers a unified interface for calling LLMs. It supports sync and async operations, pluggable authentication, and swappable providers — all configured via a simple dataclass.

---

## Work Item Landscape

| ID | Title | Status |
|----|-------|--------|
| LLM-0001 | Provider-Abstracted LLM Client | ✅ Implemented |
| LLM-0002 | Config Persistence (JSON/YAML) | ❌ Cancelled |
| LLM-0003 | Pluggable Auth Manager | ✅ Implemented |
| LLM-0004 | Azure OpenAI Provider | 🔧 In Progress |

---

## Layer Architecture

```
┌──────────────────────────────────────────────────┐
│                   Consumer Code                   │
│         client.complete("prompt") -> str          │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│               LLMClient  (client.py)              │
│  • Facade / entry point                           │
│  • Accepts LLMConfig + optional AuthStrategy      │
│  • Resolves provider from PROVIDER_REGISTRY       │
│  • Delegates complete() / acomplete() to provider │
│  • Context manager (sync + async)                 │
└────────┬─────────────────────────────┬───────────┘
         │                             │
         ▼                             ▼
┌─────────────────┐         ┌──────────────────────┐
│  AuthStrategy    │         │  LLMProvider (ABC)   │
│  (auth/base.py)  │         │  (providers/base.py) │
│                  │         │                      │
│  resolve() → str │         │  complete(prompt)    │
│  aresolve()→ str │         │  acomplete(prompt)   │
│  repr = "***"    │         │  close() / aclose()  │
└───────┬──────────┘         └───────┬──────────────┘
        │                            │
   ┌────┴────┬────────┐        ┌────┴─────────────────┐
   ▼         ▼        ▼        ▼                       ▼
EnvVarAuth  MSIAuth  Callback  OpenAIProvider   AzureOpenAIProvider
                     Auth      (implemented)     (LLM-0004 — next)
```

---

## Module Map

| Module | Purpose | Story |
|--------|---------|-------|
| `llm_extender/client.py` | `LLMClient` facade + `PROVIDER_REGISTRY` | LLM-0001 |
| `llm_extender/config.py` | `LLMConfig` dataclass (api_key hidden from repr) | LLM-0001 |
| `llm_extender/exceptions.py` | Exception hierarchy (`LLMExtenderError` → children) | LLM-0001 |
| `llm_extender/providers/base.py` | `LLMProvider` ABC (complete/acomplete/close/aclose) | LLM-0001 |
| `llm_extender/providers/openai.py` | `OpenAIProvider` — httpx-based, `/v1/chat/completions` | LLM-0001 |
| `llm_extender/auth/base.py` | `AuthStrategy` ABC (resolve/aresolve, safe repr) | LLM-0003 |
| `llm_extender/auth/env_var.py` | `EnvVarAuth` — reads from `os.environ` | LLM-0003 |
| `llm_extender/auth/msi.py` | `ManagedIdentityAuth` — Azure MSI via `azure-identity` | LLM-0003 |
| `llm_extender/auth/callback.py` | `CallbackAuth` — user-supplied `() → str` callable | LLM-0003 |

---

## Key Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| **Strategy** | `AuthStrategy` → `EnvVarAuth`, `MSIAuth`, `CallbackAuth` | Pluggable credential resolution without coupling |
| **Strategy** | `LLMProvider` → `OpenAIProvider`, (future `AzureOpenAIProvider`) | Swap providers via config alone |
| **Registry** | `PROVIDER_REGISTRY` dict in `client.py` | Name-based provider lookup, clear error on miss |
| **Facade** | `LLMClient` | Single entry point hides provider complexity |
| **Context Manager** | `LLMClient.__enter__`/`__aenter__` | Deterministic resource cleanup (httpx clients) |

---

## Dependency Graph

```
llm-extender
├── httpx >=0.24              (required — sync+async HTTP)
├── azure-identity            (optional — only for ManagedIdentityAuth)
└── dev:
    ├── pytest >=7.0
    ├── pytest-asyncio >=0.21
    └── respx >=0.20
```

---

## Security Model

- **api_key** is `repr=False` on `LLMConfig` — never in logs/tracebacks
- **AuthStrategy** base class returns `"ClassName(***)"` for `repr`/`str`
- Credentials are resolved at runtime, never persisted to disk
- `EnvVarAuth` reads env vars; `CallbackAuth` calls user code; `MSIAuth` calls Azure token endpoint — none log the value

---

## What LLM-0004 Adds

The next work item introduces an `AzureOpenAIProvider` that:

- Targets Azure's URL: `{base_url}/openai/deployments/{deployment}/chat/completions?api-version={api_version}`
- Adds `deployment` and `api_version` fields to `LLMConfig`
- Registers as `"azure_openai"` in `PROVIDER_REGISTRY`
- Uses `Authorization: Bearer <token>` with Azure AD tokens (via `CallbackAuth` + `DefaultAzureCredential`)
- Reuses the same `LLMProvider` ABC contract — no changes to client or auth layer

---

## Test Coverage

Tests live in `tests/` and cover:

| File | Scope |
|------|-------|
| `test_client.py` | `LLMClient` creation, provider dispatch, errors |
| `test_openai_provider.py` | HTTP calls via respx mocking, error paths |
| `test_auth_base.py` | ABC contract, safe repr |
| `test_auth_env_var.py` | Env var resolution, missing var errors |
| `test_auth_msi.py` | MSI token acquisition (mocked) |
| `test_auth_callback.py` | Sync/async callback resolution |
| `test_auth_client_integration.py` | Client + auth strategies end-to-end |
| `test_auth_security.py` | No secrets in repr/str/logs |
| `conftest.py` | Shared fixtures |
