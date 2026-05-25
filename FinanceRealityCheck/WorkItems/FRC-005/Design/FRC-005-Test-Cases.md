# FRC-005 Test Cases

## AC coverage
- AC1: module startup command works without traceback.
- AC2: `/health` returns 200 and deterministic fields.
- AC3: `/planner/summary` returns 200 and deterministic capability set.
- AC4: README includes startup + verification commands.
- AC5: API tests deterministic and regression tests remain green.

## Negative checks
- Invalid host/port args should fail with clear parser error.
- Endpoints should not expose sensitive account/token details.
