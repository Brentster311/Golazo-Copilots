"""Custom exceptions for the Expert System."""


class IncidentLoadError(Exception):
    """Raised when an incident file cannot be loaded."""
    pass


class LLMError(Exception):
    """Raised when LLM API call fails or returns unparseable output."""
    pass


class ConfigError(Exception):
    """Raised when required configuration is missing."""
    pass
