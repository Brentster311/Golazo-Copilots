# LLM-0012: Auto-Discover Azure OpenAI Configurations

**Status**: IMPLEMENTED

## User Story

- **Title**: Auto-discover viable Azure OpenAI configurations from CLI credentials
- **As a**: Developer using LLM Extender
- **I want**: A static/class method (e.g., `LLMClient.discover()`) that uses my Azure CLI credentials to enumerate all Azure OpenAI resources I have RBAC access to, along with their deployments, and returns a list of ready-to-use `LLMConfig` objects
- **So that**: I can connect to Azure OpenAI without manually looking up endpoints, deployment names, API versions, or managing API keys — zero-config setup for anyone logged in via `az login`

- **Out of scope**:
  - Non-Azure OpenAI providers (plain OpenAI, etc.)
  - Managed Identity discovery (only Azure CLI credentials)
  - Persisting discovered configs to disk / env files
  - Removing the `api_key` field from `LLMConfig` (separate work item)
  - Multi-tenant discovery (uses the current `az` tenant only)
  - Async variant of discover (sync-only in this story)

- **Assumptions**:
  - **Assumption (explicit)**: `azure-identity` and `azure-mgmt-cognitiveservices` (or equivalent Azure SDK) are available as optional dependencies. The method raises `ImportError` with a clear message if missing.
  - **Assumption (explicit)**: Discovery uses `AzureCliCredential` only — not MSI, not service principal. This is a developer-experience feature.
  - **Assumption (explicit)**: The method enumerates all subscriptions the CLI credential has access to, then filters for Cognitive Services accounts of kind `OpenAI` where the user has a role that permits inference (e.g., `Cognitive Services OpenAI User` or `Contributor`).
  - **Assumption (explicit)**: Each deployment on each accessible resource becomes one `LLMConfig` entry in the returned list.
  - **Assumption (explicit)**: The returned `LLMConfig` objects use `provider="azure_openai"` and are pre-populated with `base_url`, `deployment`, `model`, and `api_version`. The `api_key` field is left empty — callers pass `AzureChainedAuth()` to `LLMClient`.

- **Acceptance Criteria** (bulleted, testable):
  - [ ] A static or class method `LLMClient.discover()` (or module-level `discover_azure_configs()`) exists and is importable from `llm_extender`
  - [ ] When called with valid Azure CLI credentials, it returns a `list[LLMConfig]` containing one entry per accessible deployment across all subscriptions
  - [ ] Each returned `LLMConfig` has `provider="azure_openai"`, `base_url` set to the resource endpoint, `deployment` set to the deployment name, `model` set to the underlying model name, and `api_version` set to the latest stable version
  - [ ] If no Azure OpenAI resources are found or the user has no RBAC access, the method returns an empty list (does not raise)
  - [ ] If `azure-identity` or required Azure SDK packages are not installed, the method raises `ImportError` with installation instructions
  - [ ] The returned configs can be directly passed to `LLMClient(config, auth=AzureChainedAuth())` and produce a working client
  - [ ] Unit tests mock the Azure SDK calls and verify correct config assembly; no live Azure calls in CI

- **Non-functional requirements**:
  - Discovery should complete within 30 seconds for a typical developer with 1–5 subscriptions
  - No credentials or tokens are persisted, logged, or included in returned objects
  - Method is idempotent and safe to call multiple times

- **Telemetry / metrics expected**:
  - Count of subscriptions scanned
  - Count of resources found vs. accessible (RBAC-permitted)
  - Count of deployments returned
  - Timing of discovery operation

- **Rollout / rollback notes**:
  - This is additive — no breaking changes to existing API
  - New optional dependency (`azure-mgmt-cognitiveservices`) should be added under an `[azure-discover]` extra or bundled with existing `azure-identity` dependency
