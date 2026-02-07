"""Environment variable authentication strategy.

Resolves credentials from a named environment variable.
"""

from __future__ import annotations

import os

from llm_extender.auth.base import AuthStrategy
from llm_extender.exceptions import AuthenticationError


class EnvVarAuth(AuthStrategy):
    """Resolve an API key from a named environment variable.

    Args:
        env_var: The name of the environment variable containing
            the credential.
    """

    def __init__(self, env_var: str) -> None:
        self._env_var = env_var

    def resolve(self) -> str:
        """Read the credential from the environment variable.

        Returns:
            The credential string.

        Raises:
            AuthenticationError: If the variable is not set or empty.
        """
        value = os.environ.get(self._env_var)
        if not value:
            raise AuthenticationError(
                f"Environment variable '{self._env_var}' is not set or empty"
            )
        return value

    async def aresolve(self) -> str:
        """Async version — delegates to sync resolve (env lookup is non-blocking)."""
        return self.resolve()

    def __repr__(self) -> str:
        return f"EnvVarAuth(env_var='{self._env_var}')"
