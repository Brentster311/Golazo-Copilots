# LLM-0012 Developer Decision Notes

## Implementation Summary

Implemented `LLMClient.discover()` — a static method that auto-discovers Azure OpenAI
configurations from Azure CLI credentials. TDD approach: 13 test cases written first,
then production code to make them pass.

## Key Design Decisions

### 1. Lazy SDK Import Pattern (`_ensure_azure_sdk`)

**Decision:** Use module-level globals (`AzureCliCredential`, `SubscriptionClient`,
`CognitiveServicesManagementClient`) initialized to `None`, populated on first call
via `_ensure_azure_sdk()` with a `_sdk_loaded` boolean guard.

**Rationale:** Allows `import llm_extender.discovery` to succeed even when the Azure
SDK is not installed (users get a clear `ImportError` only when they call the
function). Also enables clean mocking in tests via `patch.object()` on the module
globals, without fighting with real imports.

**Alternative considered:** Top-level `try/except ImportError` — rejected because it
made mocking in tests unreliable (the real SDK would be imported at module load time,
preventing mock injection).

### 2. `azure-mgmt-subscription` (not `azure-mgmt-resource`)

**Decision:** Use `from azure.mgmt.subscription import SubscriptionClient` from the
`azure-mgmt-subscription` package.

**Rationale:** The `azure-mgmt-resource` v25.0+ package no longer exports
`SubscriptionClient`. The subscription enumeration client lives in a separate package
`azure-mgmt-subscription>=3.0`.

### 3. Graceful Error Handling

**Decision:** Wrap subscription enumeration, account listing, and deployment listing
in broad `except Exception` blocks that log warnings and `continue`.

**Rationale:** In multi-subscription environments, the caller may have RBAC access to
some subscriptions/resources but not others. Failing hard on the first 403 would
prevent discovery of all accessible resources. The caller gets all configs they have
permission for, and warnings are logged for anything skipped.

### 4. `subscription_id` Filter

**Decision:** When `subscription_id` is provided, skip `SubscriptionClient.list()`
entirely and only scan that single subscription.

**Rationale:** Avoids unnecessary Azure management API calls. Users who already know
their subscription ID get faster results without needing list-subscription RBAC.

### 5. Test Isolation for `TestDiscoverMissingSDK` (TC-04)

**Decision:** Test the missing-SDK scenario by patching `_sdk_loaded = False` and
`sys.modules["azure.mgmt.cognitiveservices"] = None`, then calling
`_ensure_azure_sdk()` directly.

**Rationale:** Original approach deleted `sys.modules["llm_extender.discovery"]` and
re-imported the module, which corrupted module state for subsequent tests. The new
approach uses `patch.object` and `patch.dict` which restore cleanly after the test.

## Files Changed

| File | Change |
|------|--------|
| `llm_extender/discovery.py` | **New** — `discover_azure_configs()`, `_ensure_azure_sdk()`, `_resource_group_from_id()` |
| `llm_extender/client.py` | Added `LLMClient.discover()` static method |
| `llm_extender/__init__.py` | Added `discover_azure_configs` to public API |
| `pyproject.toml` | Added `[azure-discover]` optional dependency group |
| `tests/test_discovery.py` | **New** — 13 test cases (12 non-live, 1 live) |

## Test Results

- **12 non-live tests:** All pass (0.55s)
- **1 live test:** Deselected (requires `az login` + real Azure resources)
- **Full suite:** 193 passed, 7 deselected, 0 failures (16.67s) — no regressions

## Dependencies Added

| Package | Version | Purpose |
|---------|---------|---------|
| `azure-identity` | >=1.14 | `AzureCliCredential` for auth |
| `azure-mgmt-cognitiveservices` | >=13.5 | List OpenAI resources & deployments |
| `azure-mgmt-subscription` | >=3.0 | Enumerate accessible subscriptions |

These are in the `[azure-discover]` optional dependency group to avoid bloating
the base install.
