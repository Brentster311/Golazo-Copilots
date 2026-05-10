# Agent Loop

A basic, reusable Python package that runs a deterministic plan -> execute -> evaluate loop with a pluggable state store.

## Requirements
- Python 3.11+

## Install for Local Development
- Create/activate your environment
- Install test dependencies:

```bash
python -m pip install pytest pytest-cov
```

## Quick Usage

```python
from agent_loop import AgentLoop


def planner(state):
    return {"next_counter": state.get("counter", 0) + 1}


def executor(state, action):
    state["counter"] = action["next_counter"]
    return {"counter": state["counter"]}


def evaluator(state, action, outcome, step_index):
    _ = (action, step_index)
    return outcome["counter"] >= state.get("target", 3)


loop = AgentLoop(planner=planner, executor=executor, evaluator=evaluator)
result = loop.run(initial_state={"target": 2}, max_steps=10)

print(result.termination_reason)
print(result.total_steps)
```

## Public API
- AgentLoop
- InMemoryStateStore
- StateStore
- StepResult
- LoopRunResult

## Testing

```bash
python -m pytest
python -m pytest --cov=agent_loop --cov-report=term-missing
```

## Changelog

### [0.1.0] - 2026-05-10
- Added initial Agent Loop package with deterministic run cycle.
- Added pluggable state store abstraction and in-memory implementation.
- Added structured run and step result models.
- Added unit tests and coverage configuration.
