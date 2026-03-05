"""Roles module for Golazo Copilot."""

from .loader import has_local_role_override, load_default_role, load_role_instructions

__all__ = [
    "load_role_instructions",
    "load_default_role",
    "has_local_role_override",
]
