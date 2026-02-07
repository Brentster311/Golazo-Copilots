# Design Doc: LLM-0003 — Pluggable Auth Manager

**Work Item:** LLM-0003  
**Author:** Program Manager  
**Date:** 2026-02-07  
**Status:** DRAFT

---

## 1. Summary

Build a pluggable authentication layer with an abstract `AuthStrategy` interface and three concrete implementations: `EnvVarAuth` (environment variable), `ManagedIdentityAuth` (Azure MSI), and `CallbackAuth` (user-supplied callable). Credentials are resolved at runtime and never persisted, logged, or exposed via string representations.

## 2. Problem Statement

LLM providers require API keys or tokens for authentication, but the source of these credentials varies by deployment environment: local dev uses env vars, Azure cloud uses Managed Identity, enterprise environments may use key vaults or custom retrieval mechanisms. A pluggable auth layer decouples credential resolution from the LLM client.

## 3. Business Case

| Dimension | Detail |
|---|---|
| **Why now** | LLM-0001 currently hardcodes `api_key` in config — this replaces it with flexible resolution |
| **Impact** | Enables secure, environment-appropriate credential management without code changes |
| **KPIs** | N/A for library — success = passing tests + no secret leaks |

## 4. Stakeholders

| Role | Interest |
|---|---|
| Library consumers | Plug in auth strategy matching their deployment |
| Security/compliance | No secrets in logs, disk, or repr |
| LLM-0001 | Client calls `auth.resolve()` instead of reading `config.api_key` |

## 5. Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `AuthStrategy` ABC with `resolve() -> str` and `async aresolve() -> str` methods | AC-1 |
| FR-2 | `EnvVarAuth(env_var: str)` — reads named env var | AC-2 |
| FR-3 | `ManagedIdentityAuth(scope: str)` — acquires Azure MSI token | AC-3 |
| FR-4 | `CallbackAuth(callback: Callable[[], str])` — calls user function | AC-4 |
| FR-5 | Credentials never persisted or logged | AC-5 |
| FR-6 | `__repr__`/`__str__` mask credential values | AC-6 |
| FR-7 | Clear error on missing/invalid credentials | AC-7 |

## 6. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | No secret value in any log output at any level |
| NFR-2 | `azure-identity` is optional — only required for `ManagedIdentityAuth` |
| NFR-3 | Type hints on all public surfaces |
| NFR-4 | Python 3.10+ compatibility |

## 7. Proposed Approach

### 7.1 Package Structure (additions to llm_extender/)

```
llm_extender/
├── auth/
│   ├── __init__.py      # Public exports
│   ├── base.py          # AuthStrategy ABC
│   ├── env_var.py       # EnvVarAuth
│   ├── msi.py           # ManagedIdentityAuth
│   └── callback.py      # CallbackAuth
└── exceptions.py        # AuthenticationError (added)
```

### 7.2 AuthStrategy ABC

```python
class AuthStrategy(ABC):
    @abstractmethod
    def resolve(self) -> str:
        """Resolve and return the credential. Never cache to disk."""
        ...

    @abstractmethod
    async def aresolve(self) -> str:
        """Async version of resolve."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(***)"

    def __str__(self) -> str:
        return self.__repr__()
```

### 7.3 EnvVarAuth

```python
class EnvVarAuth(AuthStrategy):
    def __init__(self, env_var: str):
        self._env_var = env_var

    def resolve(self) -> str:
        value = os.environ.get(self._env_var)
        if not value:
            raise AuthenticationError(f"Environment variable '{self._env_var}' is not set or empty")
        return value

    async def aresolve(self) -> str:
        return self.resolve()  # Env var lookup is non-blocking

    def __repr__(self) -> str:
        return f"EnvVarAuth(env_var='{self._env_var}')"
```

### 7.4 ManagedIdentityAuth

```python
class ManagedIdentityAuth(AuthStrategy):
    def __init__(self, scope: str = "https://cognitiveservices.azure.com/.default"):
        try:
            from azure.identity import ManagedIdentityCredential
        except ImportError:
            raise ImportError("ManagedIdentityAuth requires 'azure-identity'. Install with: pip install azure-identity")
        self._scope = scope
        self._credential = ManagedIdentityCredential()

    def resolve(self) -> str:
        token = self._credential.get_token(self._scope)
        return token.token

    async def aresolve(self) -> str:
        # azure-identity supports async via azure.identity.aio
        from azure.identity.aio import ManagedIdentityCredential as AsyncManagedIdentityCredential
        async_cred = AsyncManagedIdentityCredential()
        token = await async_cred.get_token(self._scope)
        await async_cred.close()
        return token.token

    def __repr__(self) -> str:
        return f"ManagedIdentityAuth(scope='{self._scope}')"
```

### 7.5 CallbackAuth

```python
class CallbackAuth(AuthStrategy):
    def __init__(self, callback: Callable[[], str], async_callback: Callable[[], Awaitable[str]] | None = None):
        self._callback = callback
        self._async_callback = async_callback

    def resolve(self) -> str:
        result = self._callback()
        if not result:
            raise AuthenticationError("Callback returned empty credential")
        return result

    async def aresolve(self) -> str:
        if self._async_callback:
            result = await self._async_callback()
        else:
            result = self._callback()
        if not result:
            raise AuthenticationError("Callback returned empty credential")
        return result

    def __repr__(self) -> str:
        return "CallbackAuth(callback=<function>)"
```

### 7.6 Integration Point with LLM-0001

After LLM-0003 is built, `LLMClient` gains an optional `auth` parameter:

```python
class LLMClient:
    def __init__(self, config: LLMConfig, auth: AuthStrategy | None = None):
        ...
```

If `auth` is provided, the client calls `auth.resolve()` to get the API key instead of reading `config.api_key`. This is backward-compatible — `config.api_key` still works for simple cases.

## 8. Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Store encrypted keys in config | User explicitly prohibits storing security artifacts |
| Use `keyring` library for OS credential store | Good future addition but out of scope |
| Single `AuthManager` class with mode enum | Less extensible; strategy pattern is cleaner for custom auth |
| Require async-only auth | Excludes simple sync use cases |

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Azure MSI not available in test env | High | Low | Mock `azure-identity` in tests; `ManagedIdentityAuth` is optional |
| Callback returns stale/expired credential | Medium | Medium | Document that callbacks should handle refresh; future: add TTL caching |
| Secret accidentally logged by caller | Medium | High | Library never logs secrets; document best practices for callers |

## 10. Dependencies

| Dependency | Direction | Detail |
|---|---|---|
| LLM-0001 | Backward | Client uses `auth.resolve()` to get credential |
| LLM-0002 | Parallel | Config stores `auth_strategy` type string; auth resolves actual credential |
| `azure-identity` | External (optional) | Required only for `ManagedIdentityAuth` |

## 11. Migration / Rollout / Rollback

- **New library** — no migration
- **Backward compatible:** `api_key` in config still works; auth is additive
- **Rollback:** Revert package version

## 12. Observability Plan

- None for initial version
- Future: log auth strategy type (never credential values) at DEBUG level

## 13. Test Strategy Summary

| Layer | What | How |
|---|---|---|
| Unit | `EnvVarAuth.resolve()` returns env var value | Set env var → resolve → assert match |
| Unit | `EnvVarAuth.resolve()` raises on missing var | Unset var → resolve → assert `AuthenticationError` |
| Unit | `ManagedIdentityAuth.resolve()` calls azure-identity | Mock `ManagedIdentityCredential` → assert `get_token` called |
| Unit | `CallbackAuth.resolve()` calls user function | Pass lambda → resolve → assert return value |
| Unit | `CallbackAuth.aresolve()` uses async callback when provided | Pass async lambda → aresolve → assert |
| Unit | `__repr__` never contains credential values | `repr(auth)` → assert no secret patterns |
| Unit | Missing credential raises clear error | Various failure scenarios → assert `AuthenticationError` |
