"""Abstract base class for LLM providers.

All provider implementations must inherit from LLMProvider and
implement the complete() and acomplete() methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class defining the LLM provider contract.

    Every concrete provider must implement both synchronous and
    asynchronous completion methods, as well as resource cleanup.
    """

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Generate a completion synchronously.

        Args:
            prompt: The user prompt to send to the model.

        Returns:
            The model's response as a string.
        """

    @abstractmethod
    async def acomplete(self, prompt: str) -> str:
        """Generate a completion asynchronously.

        Args:
            prompt: The user prompt to send to the model.

        Returns:
            The model's response as a string.
        """

    @abstractmethod
    def close(self) -> None:
        """Release any resources held by the provider (sync)."""

    @abstractmethod
    async def aclose(self) -> None:
        """Release any resources held by the provider (async)."""
