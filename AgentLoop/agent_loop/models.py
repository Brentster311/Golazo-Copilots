from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol


class Planner(Protocol):
    def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        ...


class Executor(Protocol):
    def __call__(self, state: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
        ...


class Evaluator(Protocol):
    def __call__(
        self,
        state: dict[str, Any],
        action: dict[str, Any],
        outcome: dict[str, Any],
        step_index: int,
    ) -> bool:
        ...


@dataclass(frozen=True)
class StepResult:
    step_index: int
    action_summary: str
    outcome: dict[str, Any]
    should_terminate: bool


@dataclass(frozen=True)
class LoopRunResult:
    steps: list[StepResult]
    total_steps: int
    termination_reason: Literal["success", "max_steps"]
    runtime_ms: float
