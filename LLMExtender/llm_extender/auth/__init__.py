"""Auth strategy public API.

Provides pluggable authentication strategies for resolving
credentials at runtime without persisting or logging secrets.
"""

from llm_extender.auth.azure_chained import AzureChainedAuth
from llm_extender.auth.base import AuthStrategy
from llm_extender.auth.callback import CallbackAuth
from llm_extender.auth.env_var import EnvVarAuth
from llm_extender.auth.msi import ManagedIdentityAuth

__all__ = [
    "AuthStrategy",
    "AzureChainedAuth",
    "CallbackAuth",
    "EnvVarAuth",
    "ManagedIdentityAuth",
]
