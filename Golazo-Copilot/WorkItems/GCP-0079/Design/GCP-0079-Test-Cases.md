# GCP-0079 Test Cases

## TC-1: First Complete Item Starts in Planner

- Create an empty `WorkItems` directory and call creation with `profile="complete"`, `initial_role="planner"`.
- Expected: success, current role Planner, Planner instructions returned, and role history begins with Planner.

## TC-2: Default Remains POA

- Create work items for all profiles without `initial_role` and with explicit POA.
- Expected: all initialize at Project Owner Assistant as before.

## TC-3: Planner Eligibility Is Enforced

- Request Planner for Express and Spike.
- Create one existing work-item state, then request another Complete item in Planner.
- Pass an unsupported direct-tool initial role.
- Expected: actionable failures and no requested-item state written.

## TC-4: Non-State Files Do Not Block Planner

- Place `capabilities.yaml`, `global_state.json`, and a child directory without `state.json` in the workspace.
- Expected: first Complete item may still initialize in Planner.

## TC-5: Public Wiring Forwards Initial Role

- Inspect the registered MCP schema.
- Exercise modular and compatibility dispatch with fakes capturing arguments.
- Expected: enum contains POA and Planner, default is POA, and both dispatch paths forward the requested value.

## TC-6: Offer and Documentation Are Deployed

- Inspect packaged bootstrap instructions, forced bootstrap output, fallback text, and README.
- Expected: each tells the orchestrator to offer Planner before first creation, shows the Planner creation call, and explains restrictions.

## TC-7: Regression Validation

- Run focused tests, relevant existing creation/bootstrap/dispatch tests, Ruff, and full suite with coverage.
- Expected: all pass, with strict timing tests run outside coverage instrumentation if necessary.
