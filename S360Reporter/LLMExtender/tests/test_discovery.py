"""Tests for llm_extender.discovery — auto-discover Azure OpenAI configs.

Covers TC-01 through TC-13 from LLM-0012-Test-Cases.md.
All Azure SDK calls are mocked — no real Azure calls in CI.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from llm_extender.config import LLMConfig


# ---------------------------------------------------------------------------
# Helpers — build mock Azure SDK objects
# ---------------------------------------------------------------------------

def _make_subscription(sub_id: str = "sub-1", display_name: str = "Test Sub"):
    """Create a mock Subscription object."""
    sub = SimpleNamespace()
    sub.subscription_id = sub_id
    sub.display_name = display_name
    return sub


def _make_account(
    name: str = "my-openai",
    endpoint: str = "https://my-openai.openai.azure.com/",
    kind: str = "OpenAI",
    resource_group: str = "rg-test",
    account_id: str = "/subscriptions/sub-1/resourceGroups/rg-test/providers/Microsoft.CognitiveServices/accounts/my-openai",
):
    """Create a mock CognitiveServicesAccount."""
    props = SimpleNamespace()
    props.endpoint = endpoint
    acct = SimpleNamespace()
    acct.name = name
    acct.kind = kind
    acct.id = account_id
    acct.properties = props
    # Extract resource group from id
    return acct


def _make_deployment(
    deployment_name: str = "gpt-4",
    model_name: str = "gpt-4o",
    model_version: str = "2024-11-20",
):
    """Create a mock Deployment object."""
    model = SimpleNamespace()
    model.name = model_name
    model.version = model_version
    props = SimpleNamespace()
    props.model = model
    dep = SimpleNamespace()
    dep.name = deployment_name
    dep.properties = props
    return dep


def _resource_group_from_id(resource_id: str) -> str:
    """Extract resource group name from an Azure resource id."""
    parts = resource_id.split("/")
    try:
        idx = [p.lower() for p in parts].index("resourcegroups")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return "unknown"


# ---------------------------------------------------------------------------
# Fixtures — mock Azure SDK clients
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_azure_sdk():
    """Patch Azure SDK imports and return mock client factories."""
    import llm_extender.discovery as disc_mod

    mock_credential = MagicMock()

    # SubscriptionClient mock
    mock_sub_client_cls = MagicMock()
    mock_sub_client = MagicMock()
    mock_sub_client_cls.return_value = mock_sub_client

    # CognitiveServicesManagementClient mock
    mock_cs_client_cls = MagicMock()
    mock_cs_client = MagicMock()
    mock_cs_client_cls.return_value = mock_cs_client

    # Patch the module-level globals that _ensure_azure_sdk populates
    with (
        patch.object(disc_mod, "AzureCliCredential", return_value=mock_credential, create=True),
        patch.object(disc_mod, "SubscriptionClient", mock_sub_client_cls, create=True),
        patch.object(disc_mod, "CognitiveServicesManagementClient", mock_cs_client_cls, create=True),
        patch.object(disc_mod, "_sdk_loaded", True),
    ):
        yield SimpleNamespace(
            credential=mock_credential,
            sub_client_cls=mock_sub_client_cls,
            sub_client=mock_sub_client,
            cs_client_cls=mock_cs_client_cls,
            cs_client=mock_cs_client,
        )


# ---------------------------------------------------------------------------
# TC-01: Happy path — returns configs for accessible resources
# ---------------------------------------------------------------------------

class TestDiscoverHappyPath:
    def test_returns_configs_for_accessible_deployments(self, mock_azure_sdk):
        """TC-01: Single resource with 2 deployments → 2 LLMConfig objects."""
        from llm_extender.discovery import discover_azure_configs

        # Setup: 1 subscription, 1 resource, 2 deployments
        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
        ]
        mock_azure_sdk.cs_client.accounts.list.return_value = [
            _make_account("my-openai", "https://my-openai.openai.azure.com/"),
        ]
        mock_azure_sdk.cs_client.deployments.list.return_value = [
            _make_deployment("gpt-4", "gpt-4o", "2024-11-20"),
            _make_deployment("gpt-5.2", "gpt-5.2", "2025-12-11"),
        ]

        configs = discover_azure_configs()

        assert len(configs) == 2, "Expected 2 LLMConfig objects with correct field mapping"
        assert all(isinstance(c, LLMConfig) for c in configs)

        # First config
        assert configs[0].provider == "azure_openai"
        assert configs[0].base_url == "https://my-openai.openai.azure.com/"
        assert configs[0].deployment == "gpt-4"
        assert configs[0].model == "gpt-4o"
        assert configs[0].api_version is not None

        # Second config
        assert configs[1].deployment == "gpt-5.2"
        assert configs[1].model == "gpt-5.2"


# ---------------------------------------------------------------------------
# TC-02: No accessible resources — returns empty list
# ---------------------------------------------------------------------------

class TestDiscoverNoResources:
    def test_returns_empty_list_when_no_resources(self, mock_azure_sdk):
        """TC-02: No OpenAI resources found → empty list, no exception."""
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
        ]
        mock_azure_sdk.cs_client.accounts.list.return_value = []

        result = discover_azure_configs()

        assert result == [], "Expected empty list when no OpenAI resources found"


# ---------------------------------------------------------------------------
# TC-03: 403 on deployment list — skips resource
# ---------------------------------------------------------------------------

class TestDiscover403Handling:
    def test_skips_resource_on_403(self, mock_azure_sdk):
        """TC-03: 403 on deployment list → empty list, no exception."""
        from azure.core.exceptions import HttpResponseError
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
        ]
        mock_azure_sdk.cs_client.accounts.list.return_value = [
            _make_account("no-access"),
        ]
        error = HttpResponseError(message="Forbidden")
        error.status_code = 403
        mock_azure_sdk.cs_client.deployments.list.side_effect = error

        result = discover_azure_configs()

        assert result == [], "Expected empty list when user lacks RBAC on resource"


# ---------------------------------------------------------------------------
# TC-04: Missing Azure SDK — raises ImportError
# ---------------------------------------------------------------------------

class TestDiscoverMissingSDK:
    def test_raises_import_error_with_instructions(self):
        """TC-04: Missing azure SDK → ImportError with install instructions."""
        import llm_extender.discovery as disc_mod

        # Force _ensure_azure_sdk to re-check imports by setting _sdk_loaded=False,
        # then hide a required package so the import fails.
        with (
            patch.object(disc_mod, "_sdk_loaded", False),
            patch.dict("sys.modules", {"azure.mgmt.cognitiveservices": None}),
        ):
            with pytest.raises(ImportError, match="pip install"):
                disc_mod._ensure_azure_sdk()


# ---------------------------------------------------------------------------
# TC-05: Multiple subscriptions — aggregates configs
# ---------------------------------------------------------------------------

class TestDiscoverMultipleSubs:
    def test_aggregates_configs_from_multiple_subscriptions(self, mock_azure_sdk):
        """TC-05: 2 subscriptions, each with 1 resource/deployment → 2 configs."""
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
            _make_subscription("sub-2"),
        ]

        # Different client per subscription — use side_effect on constructor
        client_1 = MagicMock()
        client_1.accounts.list.return_value = [
            _make_account("res-1", "https://res-1.openai.azure.com/"),
        ]
        client_1.deployments.list.return_value = [
            _make_deployment("dep-1", "gpt-4o"),
        ]
        client_2 = MagicMock()
        client_2.accounts.list.return_value = [
            _make_account("res-2", "https://res-2.openai.azure.com/"),
        ]
        client_2.deployments.list.return_value = [
            _make_deployment("dep-2", "gpt-5.2"),
        ]
        mock_azure_sdk.cs_client_cls.side_effect = [client_1, client_2]

        configs = discover_azure_configs()

        assert len(configs) == 2, "Expected configs from all accessible subscriptions"
        endpoints = {c.base_url for c in configs}
        assert "https://res-1.openai.azure.com/" in endpoints
        assert "https://res-2.openai.azure.com/" in endpoints


# ---------------------------------------------------------------------------
# TC-06: subscription_id filter — only scans one sub
# ---------------------------------------------------------------------------

class TestDiscoverSubFilter:
    def test_subscription_id_filter_skips_enumeration(self, mock_azure_sdk):
        """TC-06: subscription_id filter → only that sub, no list() call."""
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.cs_client.accounts.list.return_value = [
            _make_account("res-1", "https://res-1.openai.azure.com/"),
        ]
        mock_azure_sdk.cs_client.deployments.list.return_value = [
            _make_deployment("dep-1", "gpt-4o"),
        ]

        configs = discover_azure_configs(subscription_id="sub-1")

        assert len(configs) == 1, "Expected subscription_id filter to skip enumeration"
        # Subscription list should NOT have been called
        mock_azure_sdk.sub_client.subscriptions.list.assert_not_called()


# ---------------------------------------------------------------------------
# TC-07: Non-OpenAI Cognitive Services resources — skipped
# ---------------------------------------------------------------------------

class TestDiscoverFiltersNonOpenAI:
    def test_skips_non_openai_resources(self, mock_azure_sdk):
        """TC-07: Mixed resource kinds → only OpenAI resources produce configs."""
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
        ]
        mock_azure_sdk.cs_client.accounts.list.return_value = [
            _make_account("my-openai", "https://my-openai.openai.azure.com/", kind="OpenAI"),
            _make_account("my-ta", "https://my-ta.cognitiveservices.azure.com/", kind="TextAnalytics"),
        ]
        mock_azure_sdk.cs_client.deployments.list.return_value = [
            _make_deployment("dep-1", "gpt-4o"),
        ]

        configs = discover_azure_configs()

        assert len(configs) == 1, "Expected non-OpenAI resources to be filtered out"
        assert configs[0].base_url == "https://my-openai.openai.azure.com/"


# ---------------------------------------------------------------------------
# TC-08: api_version override
# ---------------------------------------------------------------------------

class TestDiscoverApiVersionOverride:
    def test_api_version_override_applied(self, mock_azure_sdk):
        """TC-08: api_version param overrides the default."""
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
        ]
        mock_azure_sdk.cs_client.accounts.list.return_value = [
            _make_account("res-1", "https://res-1.openai.azure.com/"),
        ]
        mock_azure_sdk.cs_client.deployments.list.return_value = [
            _make_deployment("dep-1", "gpt-4o"),
        ]

        configs = discover_azure_configs(api_version="2025-01-01")

        assert configs[0].api_version == "2025-01-01", "Expected api_version override to be applied"


# ---------------------------------------------------------------------------
# TC-09: LLMClient.discover() delegates correctly
# ---------------------------------------------------------------------------

class TestLLMClientDiscover:
    def test_discover_delegates_to_module_function(self):
        """TC-09: LLMClient.discover() delegates to discover_azure_configs."""
        from llm_extender.client import LLMClient

        expected = [LLMConfig(provider="azure_openai", model="gpt-4o")]
        with patch("llm_extender.discovery.discover_azure_configs", return_value=expected) as mock_fn:
            result = LLMClient.discover()

        assert result == expected, "Expected LLMClient.discover() to delegate to discover_azure_configs"
        mock_fn.assert_called_once()


# ---------------------------------------------------------------------------
# TC-10: Returned config works with LLMClient + AzureChainedAuth
# ---------------------------------------------------------------------------

class TestDiscoveredConfigWorks:
    def test_config_produces_working_client(self, mock_azure_sdk):
        """TC-10: Config from discovery → LLMClient → working completion."""
        import respx
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
        ]
        mock_azure_sdk.cs_client.accounts.list.return_value = [
            _make_account("res-1", "https://res-1.openai.azure.com/"),
        ]
        mock_azure_sdk.cs_client.deployments.list.return_value = [
            _make_deployment("gpt-4", "gpt-4o"),
        ]

        configs = discover_azure_configs()
        config = configs[0]

        # Verify the config can be used to create LLMClient
        from llm_extender.client import LLMClient
        from llm_extender.auth.callback import CallbackAuth

        auth = CallbackAuth(lambda: "fake-token")

        mock_response = {
            "choices": [{"message": {"content": "Hello!"}, "finish_reason": "stop"}],
        }
        with respx.mock:
            respx.post(
                url__startswith="https://res-1.openai.azure.com/"
            ).respond(json=mock_response)

            with LLMClient(config, auth=auth) as client:
                result = client.complete("test")

        assert result == "Hello!", "Expected discovered config to produce working LLMClient"


# ---------------------------------------------------------------------------
# TC-11: Live integration test (skipped in CI)
# ---------------------------------------------------------------------------

@pytest.mark.live
class TestDiscoverLive:
    def test_live_discovery_returns_configs(self):
        """TC-11: Real az login → at least one config returned."""
        from llm_extender.discovery import discover_azure_configs

        configs = discover_azure_configs()

        assert len(configs) > 0, "Expected live discovery to return at least one config"
        for c in configs:
            assert c.provider == "azure_openai"
            assert c.base_url
            assert c.deployment
            assert c.model
            assert c.api_version


# ---------------------------------------------------------------------------
# TC-12: Resource with zero deployments — skipped
# ---------------------------------------------------------------------------

class TestDiscoverZeroDeployments:
    def test_skips_resource_with_no_deployments(self, mock_azure_sdk):
        """TC-12: Resource exists but has 0 deployments → empty list."""
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-1"),
        ]
        mock_azure_sdk.cs_client.accounts.list.return_value = [
            _make_account("empty-res", "https://empty.openai.azure.com/"),
        ]
        mock_azure_sdk.cs_client.deployments.list.return_value = []

        result = discover_azure_configs()

        assert result == [], "Expected empty list for resource with no deployments"


# ---------------------------------------------------------------------------
# TC-13: Subscription access error — skipped gracefully
# ---------------------------------------------------------------------------

class TestDiscoverSubError:
    def test_skips_inaccessible_subscription(self, mock_azure_sdk):
        """TC-13: One sub fails → still returns configs from other sub."""
        from azure.core.exceptions import HttpResponseError
        from llm_extender.discovery import discover_azure_configs

        mock_azure_sdk.sub_client.subscriptions.list.return_value = [
            _make_subscription("sub-ok"),
            _make_subscription("sub-fail"),
        ]

        client_ok = MagicMock()
        client_ok.accounts.list.return_value = [
            _make_account("res-ok", "https://res-ok.openai.azure.com/"),
        ]
        client_ok.deployments.list.return_value = [
            _make_deployment("dep-1", "gpt-4o"),
        ]

        client_fail = MagicMock()
        client_fail.accounts.list.side_effect = HttpResponseError(message="Access denied")

        mock_azure_sdk.cs_client_cls.side_effect = [client_ok, client_fail]

        configs = discover_azure_configs()

        assert len(configs) == 1, "Expected graceful skip of inaccessible subscriptions"
        assert configs[0].base_url == "https://res-ok.openai.azure.com/"
