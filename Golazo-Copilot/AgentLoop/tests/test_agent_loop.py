from __future__ import annotations

from typing import Any

import pytest

from agent_loop import AgentLoop, InMemoryStateStore


def _planner(state: dict[str, Any]) -> dict[str, Any]:
    next_value = state.get("counter", 0) + 1
    return {"next_counter": next_value}


def _executor(state: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    state["counter"] = action["next_counter"]
    return {"counter": state["counter"]}


def _evaluator(
    state: dict[str, Any],
    action: dict[str, Any],
    outcome: dict[str, Any],
    step_index: int,
) -> bool:
    _ = (action, step_index)
    return outcome["counter"] >= state.get("target", 3)


def _never_success(
    state: dict[str, Any],
    action: dict[str, Any],
    outcome: dict[str, Any],
    step_index: int,
) -> bool:
    _ = (state, action, outcome, step_index)
    return False


def test_public_api_and_run_signature() -> None:
    loop = AgentLoop(planner=_planner, executor=_executor, evaluator=_evaluator)
    result = loop.run(initial_state={"target": 2}, max_steps=5)

    assert result.termination_reason in {"success", "max_steps"}
    assert isinstance(loop.store, InMemoryStateStore)


def test_success_termination() -> None:
    loop = AgentLoop(planner=_planner, executor=_executor, evaluator=_evaluator)
    result = loop.run(initial_state={"target": 2}, max_steps=10)

    assert result.termination_reason == "success"
    assert result.total_steps == 2


def test_max_step_termination() -> None:
    loop = AgentLoop(planner=_planner, executor=_executor, evaluator=_never_success)
    result = loop.run(initial_state={"target": 2}, max_steps=3)

    assert result.termination_reason == "max_steps"
    assert result.total_steps == 3


def test_step_record_integrity() -> None:
    loop = AgentLoop(planner=_planner, executor=_executor, evaluator=_never_success)
    result = loop.run(initial_state={"target": 999}, max_steps=4)

    assert len(result.steps) == 4
    indexes = [step.step_index for step in result.steps]
    assert indexes == [1, 2, 3, 4]
    for step in result.steps:
        assert isinstance(step.action_summary, str)
        assert isinstance(step.outcome, dict)
        assert isinstance(step.should_terminate, bool)


def test_non_positive_max_steps_rejected() -> None:
    loop = AgentLoop(planner=_planner, executor=_executor, evaluator=_never_success)

    with pytest.raises(ValueError, match="max_steps must be greater than 0"):
        loop.run(initial_state={}, max_steps=0)
