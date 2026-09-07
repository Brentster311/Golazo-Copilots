from __future__ import annotations

from typing import Any, Protocol


class StateStore(Protocol):
    def get_state(self) -> dict[str, Any]:
        ...

    def set_state(self, state: dict[str, Any]) -> None:
        ...


class InMemoryStateStore:
    def __init__(self, initial_state: dict[str, Any] | None = None) -> None:
        self._state: dict[str, Any] = dict(initial_state or {})

    def get_state(self) -> dict[str, Any]:
        # Return a mutable copy so stage callables can mutate without aliasing internals.
        return dict(self._state)

    def set_state(self, state: dict[str, Any]) -> None:
        self._state = dict(state)
