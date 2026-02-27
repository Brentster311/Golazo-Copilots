# LLM-0012 — Test Cases

## Test Matrix

All tests map to acceptance criteria from the user story.

### TC-01: Happy path — returns configs for accessible resources
**Maps to**: AC1, AC2, AC3, AC6
**Type**: Unit (mocked)
- **Setup**: Mock `SubscriptionClient` to return 1 subscription, mock `CognitiveServicesManagementClient` to return 1 OpenAI resource with 2 deployments (gpt-4o deployment named "gpt-4", gpt-5.2 deployment named "gpt-5.2")
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns `list[LLMConfig]` with 2 entries; each has correct `provider`, `base_url`, `deployment`, `model`, `api_version`
- **Failure msg**: "Expected 2 LLMConfig objects with correct field mapping"

### TC-02: No accessible resources — returns empty list
**Maps to**: AC4
**Type**: Unit (mocked)
- **Setup**: Mock `SubscriptionClient` to return 1 subscription, mock `CognitiveServicesManagementClient.accounts.list()` to return empty
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns `[]`, no exception raised
- **Failure msg**: "Expected empty list when no OpenAI resources found"

### TC-03: 403 on deployment list — skips resource
**Maps to**: AC4
**Type**: Unit (mocked)
- **Setup**: Mock `SubscriptionClient` to return 1 subscription, mock `accounts.list()` to return 1 resource, mock `deployments.list()` to raise `HttpResponseError(status_code=403)`
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns `[]`, no exception raised
- **Failure msg**: "Expected empty list when user lacks RBAC on resource"

### TC-04: Missing Azure SDK — raises ImportError
**Maps to**: AC5
**Type**: Unit (monkeypatch)
- **Setup**: Monkeypatch `builtins.__import__` to fail on `azure.mgmt.cognitiveservices`
- **Action**: Call `discover_azure_configs()`
- **Assert**: Raises `ImportError` with message containing install instructions
- **Failure msg**: "Expected ImportError with install instructions when SDK missing"

### TC-05: Multiple subscriptions — aggregates configs
**Maps to**: AC2
**Type**: Unit (mocked)
- **Setup**: Mock 2 subscriptions, each with 1 resource and 1 deployment
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns 2 configs
- **Failure msg**: "Expected configs from all accessible subscriptions"

### TC-06: subscription_id filter — only scans one sub
**Maps to**: AC2
**Type**: Unit (mocked)
- **Setup**: Mock 2 subscriptions, each with resources
- **Action**: Call `discover_azure_configs(subscription_id="sub-1")`
- **Assert**: Only returns configs from sub-1; `SubscriptionClient.subscriptions.list()` not called
- **Failure msg**: "Expected subscription_id filter to skip enumeration"

### TC-07: Non-OpenAI Cognitive Services resources — skipped
**Maps to**: AC2
**Type**: Unit (mocked)
- **Setup**: Mock 1 subscription with 2 resources: one `kind='OpenAI'`, one `kind='TextAnalytics'`
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns configs only from the OpenAI resource
- **Failure msg**: "Expected non-OpenAI resources to be filtered out"

### TC-08: api_version override
**Maps to**: AC3
**Type**: Unit (mocked)
- **Setup**: Mock 1 subscription, 1 resource, 1 deployment
- **Action**: Call `discover_azure_configs(api_version="2025-01-01")`
- **Assert**: Returned config has `api_version="2025-01-01"`
- **Failure msg**: "Expected api_version override to be applied"

### TC-09: LLMClient.discover() delegates correctly
**Maps to**: AC1
**Type**: Unit (mocked)
- **Setup**: Patch `llm_extender.discovery.discover_azure_configs` to return a known list
- **Action**: Call `LLMClient.discover()`
- **Assert**: Returns same list; patched function was called
- **Failure msg**: "Expected LLMClient.discover() to delegate to discover_azure_configs"

### TC-10: Returned config works with LLMClient + AzureChainedAuth
**Maps to**: AC6
**Type**: Unit (mocked)
- **Setup**: Create a config from discovery mock, mock the Azure OpenAI HTTP endpoint via respx
- **Action**: `LLMClient(config, auth=AzureChainedAuth()).complete("test")`
- **Assert**: Returns mocked response string
- **Failure msg**: "Expected discovered config to produce working LLMClient"

### TC-11: Live integration test
**Maps to**: AC2, AC6
**Type**: Integration (`@pytest.mark.live`)
- **Setup**: Real `az login` session
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns non-empty list; first config has all required fields populated
- **Failure msg**: "Expected live discovery to return at least one config"

### TC-12: Resource with zero deployments — skipped
**Maps to**: AC4 (edge case)
**Type**: Unit (mocked)
- **Setup**: 1 resource with empty deployment list
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns `[]`
- **Failure msg**: "Expected empty list for resource with no deployments"

### TC-13: Subscription access error — skipped gracefully
**Maps to**: AC4 (edge case)
**Type**: Unit (mocked)
- **Setup**: 2 subscriptions; second raises `HttpResponseError` on `accounts.list()`
- **Action**: Call `discover_azure_configs()`
- **Assert**: Returns configs from first subscription only; no exception
- **Failure msg**: "Expected graceful skip of inaccessible subscriptions"
