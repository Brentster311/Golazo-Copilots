"""Roles module for Golazo Copilot."""

from .loader import load_role_instructions, load_default_role, has_local_role_override

__all__ = [
    "load_role_instructions",
    "load_default_role",
    "has_local_role_override",
]
