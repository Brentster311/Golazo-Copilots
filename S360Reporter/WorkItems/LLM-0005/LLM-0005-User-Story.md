# LLM-0005: Azure Chained Auth Strategy

## Status: IMPLEMENTED

## User Story

- **Title:** Azure Chained Auth Strategy
- **As a:** developer using LLM Extender with Azure OpenAI
- **I want:** an `AzureChainedAuth` strategy that automatically resolves credentials by trying Azure CLI first, then Managed Identity, then a config API key, and failing explicitly if none work
- **So that:** I get automatic token acquisition in both local dev (Azure CLI) and production (MSI) without relying on `DefaultAzureCredential`'s broad, opaque chain

## Acceptance Criteria

1. New `AzureChainedAuth` class in `llm_extender/auth/azure_chained.py` implements `AuthStrategy`
2. Credential resolution follows this **exact order**, stopping at first success:
   - **Step 1 — Azure CLI:** Try `AzureCliCredential` to get a token (covers local dev)
   - **Step 2 — Managed Identity:** Try `ManagedIdentityCredential` to get a token (covers Azure-hosted production)
   - **Step 3 — API Key:** Fall back to `LLMConfig.api_key` if a non-empty value is set
   - **Step 4 — Fail:** Raise `AuthenticationError` listing all three methods that were attempted
3. Constructor accepts `scope: str` parameter — defaults to `https://cognitiveservices.azure.com/.default` but **must be overridable** so the same class can acquire tokens for other Azure AD-protected resources (e.g., Microsoft Graph, custom APIs, authenticated HTTPS endpoints)
4. `resolve()` returns a valid credential string (sync)
5. `aresolve()` returns a valid credential string (async, using `azure.identity.aio` variants)
6. Raises `ImportError` with helpful message if `azure-identity` is not installed (only when Azure credential steps are reached)
7. Never uses `DefaultAzureCredential`

## Usage Example (target experience)

```python
from llm_extender import LLMClient, LLMConfig
from llm_extender.auth import AzureChainedAuth

# Default scope — Azure Cognitive Services (LLM API calls)
auth = AzureChainedAuth()

config = LLMConfig(
    provider="azure_openai",
    model="gpt-4o",
    base_url="https://open-ai-poc.openai.azure.com",
    deployment="gpt-4",
)

# Automatically uses Azure CLI token (local dev)
# or MSI token (production) — no manual token management
with LLMClient(config, auth=auth) as client:
    answer = client.complete("What is the capital of Washington state?")
    print(answer)
```

### Reuse for authenticated HTTPS fetching (LLM-0006)

```python
# Custom scope — e.g., for fetching Azure AD-protected URLs
url_auth = AzureChainedAuth(scope="https://graph.microsoft.com/.default")
token = url_auth.resolve()  # Bearer token for authenticated HTTP requests
```

## Out of Scope

- `DefaultAzureCredential` — explicitly excluded per PO direction
- Certificate-based or client-secret auth
- Automatic endpoint/URL discovery from Azure resource metadata
- Token caching beyond what the underlying azure-identity credentials provide

## Assumptions

- **Assumption (explicit):** `azure-identity` remains an optional dependency (lazy import). Steps 1 & 2 are skipped with a warning if it's not installed, falling through to step 3 (API key).
- **Assumption (explicit):** The API key fallback (step 3) reads from the config's `api_key` field, which may have been set by another auth strategy or directly.

## Non-functional Requirements

- No credentials stored or logged (same security posture as existing auth strategies)
- Async credentials must be properly closed to avoid resource leaks
- Each step's failure is caught silently and the chain continues; only if all steps fail does it raise

## Telemetry / Metrics Expected

- N/A (library code, no telemetry)

## Design Note: Reusability for LLM-0006 (URL Content Fetcher)

The configurable `scope` parameter is the key enabler for LLM-0006. When fetching authenticated HTTPS URLs:
- LLM API calls use `scope="https://cognitiveservices.azure.com/.default"` (default)
- URL fetches to Azure AD-protected endpoints pass a different scope (e.g., `https://graph.microsoft.com/.default` or a custom app URI)
- Same credential chain (CLI → MSI → key), same class, different scope

## Rollout / Rollback Notes

- Additive change — new auth class, no breaking changes to existing API
