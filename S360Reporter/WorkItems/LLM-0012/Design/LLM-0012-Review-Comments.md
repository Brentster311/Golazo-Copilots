# LLM-0012 — Design Review Comments

## Overall Assessment
The design is **clear, well-scoped, and feasible**. The 403-based filtering approach is pragmatic. A few items to address:

## Comments

### 1. [Minor] `api_version` default behavior
The design says "pre-filled with `api_version`" but doesn't specify which value. Recommendation: use the `_DEFAULT_API_VERSION` from `azure_openai.py` (`2024-12-01-preview`) as the default, and allow the `api_version` parameter to override it. The deployment object from Azure SDK doesn't include an API version — it's a client-side concept.

**Resolution**: Use `_DEFAULT_API_VERSION` from the existing provider module.

### 2. [Minor] `model` field mapping
The Azure SDK deployment object has `properties.model.name` (e.g., `gpt-4o`) and the deployment itself has a `name` (e.g., `gpt-4`). The `LLMConfig.model` should map to the **underlying model name** (from `properties.model.name`) and `LLMConfig.deployment` to the **deployment name**. The design says this correctly but worth making explicit in code.

**Resolution**: Confirmed — already correct in design.

### 3. [Low Risk] Missing `base_url` vs `endpoint` naming
`LLMConfig` uses `base_url` but the design doc says "endpoint." These are the same field. No issue, just noting for developer clarity.

**Resolution**: Use `base_url` consistently in code (matches `LLMConfig`).

### 4. [Edge Case] Resources with zero deployments
A resource may exist with RBAC access but have no deployments. The function should silently skip these (not error).

**Resolution**: Already handled by the list-deployments approach — empty list = no configs for that resource.

### 5. [Approved] No concerns with 403-based filtering
This is the right call. Avoids `azure-mgmt-authorization` dependency and complex role-hierarchy resolution.

## Verdict: **Approved with minor notes above** — no blockers.

---

## Architect Notes

### Architectural Alignment
The design fits cleanly into the existing layer architecture. `discovery.py` is a new leaf module with no reverse dependencies — it imports `LLMConfig` but nothing imports it except the thin `LLMClient.discover()` delegation. This is correct isolation.

### API Contract
```python
def discover_azure_configs(
    *,
    subscription_id: str | None = None,
    api_version: str | None = None,
) -> list[LLMConfig]:
    ...
```
- Keyword-only args: **approved** — prevents positional misuse
- Return type `list[LLMConfig]`: **approved** — concrete, typed, directly usable
- Empty list on no results: **approved** — avoids exception-as-flow-control

### Security & Privacy
- **No tokens in returned objects**: `LLMConfig.api_key` will be `""` (empty string). Callers must pass `AzureChainedAuth()` separately. This is correct — tokens are short-lived and should be resolved at call time, not discovery time.
- **No credential logging**: The `AzureCliCredential` is used only transiently for management API calls. Confirmed safe.
- **RBAC check via 403**: Acceptable. The management API call itself is authenticated — we're not leaking resource existence to unauthorized users.

### Dependency Choices
- `azure-mgmt-cognitiveservices>=13.5`: Correct — this is the standard SDK for managing Cognitive Services resources
- `azure-mgmt-resource>=23.0`: Correct — needed for subscription enumeration
- Both are well-maintained Microsoft SDKs with stable APIs
- **Note**: These are `[azure-discover]` optional deps — no impact on users who don't need discovery

### Failure Isolation
- Per-subscription error handling: if one sub fails, others still get scanned — **good**
- Per-resource 403 handling: skip and continue — **good**
- `ImportError` for missing SDK: raised immediately with install instructions — **good**
- No retry logic needed — management APIs are idempotent reads

### Scalability
- Sequential subscription scanning is fine for the target use case (1–5 subs)
- `subscription_id` filter avoids enumeration entirely — good escape hatch
- Not a concern for a dev-machine tool

### Verdict: **Architecturally approved.** No new work items required.
