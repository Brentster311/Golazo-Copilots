"""Auto-discover Azure OpenAI configurations from Azure CLI credentials.

Scans all accessible subscriptions for Azure OpenAI resources the caller
has RBAC permission on, lists their deployments, and returns ready-to-use
``LLMConfig`` objects.

Requires ``azure-identity``, ``azure-mgmt-cognitiveservices``, and
``azure-mgmt-subscription``.  Install with::

    pip install llm-extender[azure-discover]

Usage::

    from llm_extender import LLMClient, AzureChainedAuth
    from llm_extender.discovery import discover_azure_configs

    configs = discover_azure_configs()
    with LLMClient(configs[0], auth=AzureChainedAuth()) as client:
        print(client.complete("Hello!"))
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llm_extender.config import LLMConfig

if TYPE_CHECKING:
    pass

logger = logging.getLogger("llm_extender.discovery")

_DEFAULT_API_VERSION = "2024-12-01-preview"

_INSTALL_MSG = (
    "Auto-discovery requires azure-identity, azure-mgmt-cognitiveservices, "
    "and azure-mgmt-subscription. Install with: "
    "pip install llm-extender[azure-discover]"
)

# These are populated lazily by _ensure_azure_sdk() on first call.
# They are module-level so tests can patch them via patch.object().
AzureCliCredential: type | None = None
CognitiveServicesManagementClient: type | None = None
SubscriptionClient: type | None = None
_sdk_loaded = False


def _ensure_azure_sdk() -> None:
    """Import Azure SDK classes, raising ImportError if missing."""
    global AzureCliCredential, CognitiveServicesManagementClient, SubscriptionClient, _sdk_loaded  # noqa: PLW0603
    if _sdk_loaded:
        return
    try:
        from azure.identity import AzureCliCredential as _Cred
        from azure.mgmt.cognitiveservices import (
            CognitiveServicesManagementClient as _CS,
        )
        from azure.mgmt.subscription import SubscriptionClient as _Sub

        AzureCliCredential = _Cred
        CognitiveServicesManagementClient = _CS
        SubscriptionClient = _Sub
        _sdk_loaded = True
    except ImportError as exc:
        raise ImportError(_INSTALL_MSG) from exc


def discover_azure_configs(
    *,
    subscription_id: str | None = None,
    api_version: str | None = None,
) -> list[LLMConfig]:
    """Discover Azure OpenAI resources and return ready-to-use configs.

    Uses ``AzureCliCredential`` (from ``az login``) to enumerate accessible
    resources and deployments.

    Args:
        subscription_id: If provided, only scan this subscription instead
            of enumerating all accessible subscriptions.
        api_version: Override the default Azure OpenAI API version used in
            the returned configs.  Defaults to ``2024-12-01-preview``.

    Returns:
        A list of ``LLMConfig`` objects, one per accessible deployment.
        Empty list if no resources or deployments are found.

    Raises:
        ImportError: If the required Azure SDK packages are not installed.
    """
    _ensure_azure_sdk()
    effective_api_version = api_version or _DEFAULT_API_VERSION
    credential = AzureCliCredential()
    configs: list[LLMConfig] = []

    # Determine subscriptions to scan
    if subscription_id is not None:
        sub_ids = [subscription_id]
        logger.info("Scanning single subscription: %s", subscription_id)
    else:
        sub_client = SubscriptionClient(credential)
        try:
            subs = list(sub_client.subscriptions.list())
        except Exception:
            logger.warning("Failed to enumerate subscriptions", exc_info=True)
            return []
        sub_ids = [s.subscription_id for s in subs]
        logger.info("Found %d subscription(s) to scan", len(sub_ids))

    # Scan each subscription
    for sid in sub_ids:
        try:
            cs_client = CognitiveServicesManagementClient(credential, sid)
            accounts = list(cs_client.accounts.list())
        except Exception:
            logger.warning(
                "Failed to list Cognitive Services accounts in subscription %s",
                sid,
                exc_info=True,
            )
            continue

        # Filter to OpenAI-kind resources
        openai_accounts = [a for a in accounts if getattr(a, "kind", "") == "OpenAI"]
        logger.debug(
            "Subscription %s: %d Cognitive Services account(s), %d OpenAI",
            sid, len(accounts), len(openai_accounts),
        )

        for account in openai_accounts:
            endpoint = account.properties.endpoint
            resource_group = _resource_group_from_id(account.id)

            try:
                deployments = list(
                    cs_client.deployments.list(resource_group, account.name)
                )
            except Exception:
                logger.warning(
                    "Cannot list deployments for %s (likely no RBAC access)",
                    account.name,
                    exc_info=True,
                )
                continue

            logger.debug(
                "Resource %s: %d deployment(s)", account.name, len(deployments),
            )

            for dep in deployments:
                config = LLMConfig(
                    provider="azure_openai",
                    model=dep.properties.model.name,
                    base_url=endpoint,
                    deployment=dep.name,
                    api_version=effective_api_version,
                )
                configs.append(config)

    logger.info("Discovery complete: %d config(s) found", len(configs))
    return configs


def _resource_group_from_id(resource_id: str) -> str:
    """Extract the resource group name from an Azure resource ID."""
    parts = resource_id.split("/")
    try:
        idx = [p.lower() for p in parts].index("resourcegroups")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return "unknown"
