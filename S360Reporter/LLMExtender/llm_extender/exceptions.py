"""Exception hierarchy for LLM Extender.

All library exceptions inherit from LLMExtenderError, giving callers
a single base class to catch.
"""


class LLMExtenderError(Exception):
    """Base exception for all LLM Extender errors."""


class UnsupportedProviderError(LLMExtenderError):
    """Raised when a provider name is not found in the provider registry."""


class ProviderError(LLMExtenderError):
    """Raised when the LLM provider returns an error (HTTP or API-level)."""


class AuthenticationError(LLMExtenderError):
    """Raised when credential resolution fails."""
