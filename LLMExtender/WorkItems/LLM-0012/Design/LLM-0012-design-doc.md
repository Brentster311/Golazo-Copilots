# LLM-0012 Design Document — Auto-Discover Azure OpenAI Configurations

## Summary

Add a `discover_azure_configs()` function (also exposed as `LLMClient.discover()`) that uses Azure CLI credentials to scan all accessible subscriptions, enumerate Azure OpenAI resources the caller has RBAC permission on, list their deployments, and return ready-to-use `LLMConfig` objects. Zero-config setup for developers logged in via `az login`.

## Problem Statement

Today, configuring LLM Extender for Azure OpenAI requires manually collecting 4 pieces of information: endpoint URL, deployment name, model name, and API version. With `disableLocalAuth: true` becoming the default on Azure OpenAI resources, API keys don't work — making the manual setup even more confusing since users must also understand `AzureChainedAuth`. Developers shouldn't need to visit the Azure Portal to use their own resources.

## Business Case

- **Why now**: The team's own resources have local auth disabled; manual config is a friction point blocking adoption.
- **Impact**: Reduces first-use setup from ~10 manual steps to 2 lines of code.
- **KPIs**: Time-to-first-completion for new users; reduction in auth-related support questions.

## Stakeholders

- Library consumers (developers using `llm_extender`)
- Library maintainers (testing, dependency management)

## Functional Requirements

1. Enumerate all Azure subscriptions accessible via `AzureCliCredential`
2. For each subscription, list Cognitive Services accounts of kind `OpenAI`
3. For each resource, check the user's RBAC role assignments for inference-capable roles
4. For each accessible resource, list all deployments
5. Return a `list[LLMConfig]` with one entry per deployment, pre-filled with `provider`, `base_url`, `deployment`, `model`, `api_version`

## Non-Functional Requirements

- Complete within 30s for 1–5 subscriptions
- No credentials persisted, logged, or in returned objects
- Idempotent — safe to call multiple times
- Graceful degradation: missing SDK → `ImportError` with install instructions; no accessible resources → empty list

## Proposed Approach

### New Module: `llm_extender/discovery.py`

```python
def discover_azure_configs(
    *,
    subscription_id: str | None = None,  # filter to one sub
    api_version: str | None = None,      # override default
) -> list[LLMConfig]:
```

**Implementation flow:**
1. Import `azure.identity.AzureCliCredential` and `azure.mgmt.cognitiveservices.CognitiveServicesManagementClient` — raise `ImportError` if missing
2. Create credential via `AzureCliCredential()`
3. List subscriptions via `azure.mgmt.resource.SubscriptionClient` (or accept `subscription_id` filter)
4. For each subscription, create `CognitiveServicesManagementClient` and list accounts filtered to `kind == 'OpenAI'`
5. For each account, list deployments via `client.deployments.list()`
6. For each deployment, build an `LLMConfig(provider="azure_openai", model=deployment.properties.model.name, base_url=account.properties.endpoint, deployment=deployment.name, api_version=...)`
7. Return collected list

**RBAC check**: Rather than calling the Authorization API (which adds complexity and another SDK dependency), we'll use a pragmatic approach: attempt to list deployments on each resource. If the user lacks `Microsoft.CognitiveServices/accounts/deployments/read`, the list call returns 403 → skip that resource. This is simpler, faster, and avoids the `azure-mgmt-authorization` dependency.

### Expose on LLMClient

```python
class LLMClient:
    @staticmethod
    def discover(**kwargs) -> list[LLMConfig]:
        from llm_extender.discovery import discover_azure_configs
        return discover_azure_configs(**kwargs)
```

### New optional dependency group

```toml
[project.optional-dependencies]
azure-discover = [
    "azure-identity>=1.14",
    "azure-mgmt-cognitiveservices>=13.5",
    "azure-mgmt-resource>=23.0",
]
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Use `az` CLI subprocess calls | No SDK dependency | Fragile parsing, slow, cross-platform issues | Rejected |
| Check RBAC via Authorization API | Precise permission check | Adds `azure-mgmt-authorization` dep, complex role hierarchy | Rejected — use 403-based filtering |
| Return dicts instead of `LLMConfig` | Simpler | Loses type safety, not directly usable with `LLMClient` | Rejected |
| Discover from env vars / config file | No Azure SDK needed | Doesn't solve the core problem | Rejected |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Azure SDK breaking changes | Low | Medium | Pin minimum versions; test against latest |
| Slow discovery with many subscriptions | Low | Medium | Accept `subscription_id` filter param |
| User lacks subscription-level read | Low | Low | Catch `HttpResponseError`, skip sub, log warning |
| Rate limiting on management API | Very Low | Low | Sequential calls are fine for <100 resources |

## Open Questions

None — all resolved in user story discussion.

## Dependencies

- `azure-identity>=1.14` (already optional dep for `AzureChainedAuth`)
- `azure-mgmt-cognitiveservices>=13.5` (new)
- `azure-mgmt-resource>=23.0` (new, for subscription enumeration)

## Migration / Rollout / Rollback

- **Additive only** — no breaking changes to existing API
- New optional dependency group `[azure-discover]`
- Rollback: remove the module and `LLMClient.discover` classmethod

## Observability

- Logging at `INFO` level: subscriptions scanned, resources found, deployments returned
- Logging at `DEBUG` level: individual resource/deployment details
- Logging at `WARNING` level: skipped resources (403), skipped subscriptions (error)

## Test Strategy

- **Unit tests**: Mock `CognitiveServicesManagementClient` and `SubscriptionClient` to verify config assembly, empty results, 403 handling, missing SDK
- **Integration test** (marked `@pytest.mark.live`): Real `az login` discovery against test subscription
- **No new CI dependencies**: Unit tests use mocks only
