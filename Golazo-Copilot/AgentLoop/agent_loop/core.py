from __future__ import annotations

from time import perf_counter
from typing import Any

from .models import Evaluator, Executor, LoopRunResult, Planner, StepResult
from .store import InMemoryStateStore, StateStore


class AgentLoop:
    def __init__(
        self,
        *,
        planner: Planner,
        executor: Executor,
        evaluator: Evaluator,
        store: StateStore | None = None,
    ) -> None:
        self._planner = planner
        self._executor = executor
        self._evaluator = evaluator
        self.store: StateStore = store if store is not None else InMemoryStateStore()

    def run(self, *, initial_state: dict[str, Any], max_steps: int) -> LoopRunResult:
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than 0")

        self.store.set_state(initial_state)
        steps: list[StepResult] = []
        start = perf_counter()

        for step_index in range(1, max_steps + 1):
            state = self.store.get_state()

            action = self._run_stage(
                stage_name="planner",
                step_index=step_index,
                stage_call=lambda: self._planner(state),
            )
            outcome = self._run_stage(
                stage_name="executor",
                step_index=step_index,
                stage_call=lambda: self._executor(state, action),
            )
            should_terminate = self._run_stage(
                stage_name="evaluator",
                step_index=step_index,
                stage_call=lambda: self._evaluator(state, action, outcome, step_index),
            )

            self.store.set_state(state)
            steps.append(
                StepResult(
                    step_index=step_index,
                    action_summary=_summarize_action(action),
                    outcome=outcome,
                    should_terminate=bool(should_terminate),
                )
            )

            # Success takes precedence over max-step checks for the current iteration.
            if should_terminate:
                runtime_ms = (perf_counter() - start) * 1000
                return LoopRunResult(
                    steps=steps,
                    total_steps=len(steps),
                    termination_reason="success",
                    runtime_ms=runtime_ms,
                )

        runtime_ms = (perf_counter() - start) * 1000
        return LoopRunResult(
            steps=steps,
            total_steps=len(steps),
            termination_reason="max_steps",
            runtime_ms=runtime_ms,
        )

    @staticmethod
    def _run_stage(*, stage_name: str, step_index: int, stage_call: Any) -> Any:
        try:
            return stage_call()
        except Exception as exc:  # pragma: no cover - defensive error context.
            raise RuntimeError(
                f"AgentLoop stage '{stage_name}' failed at step {step_index}"
            ) from exc


def _summarize_action(action: dict[str, Any]) -> str:
    if "type" in action:
        return str(action["type"])
    return repr(action)
