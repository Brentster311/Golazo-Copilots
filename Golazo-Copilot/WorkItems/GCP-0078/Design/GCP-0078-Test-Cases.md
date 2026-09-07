# GCP-0078 Test Cases

## TC-1: Bypass Semantics Are Accurate

- Assert the README retains consent plus `force=True` for missing output gates.
- Assert it does not advertise `skip_role` plus `force=True` as a role-note bypass.
- Expected: public instructions describe only callable MCP behavior.

## TC-2: Roles and Progress Match Source

- Compare the Complete profile count and Planner membership with the README.
- Assert the README identifies Project Owner Assistant as the initial role.
- Expected: Complete progress uses 11 roles and the transition target list includes Planner.

## TC-3: Public Tool Surface Is Complete

- Compare registered Golazo tool names with the README tool-discovery list.
- Assert `golazo_role_context` has a reference section and required inputs.
- Expected: every registered public tool is discoverable and documented.

## TC-4: Operational Boundaries Are Explicit

- Assert configured-interpreter installation guidance replaces the global-environment requirement.
- Assert Git proposal-only behavior, absence of automatic Git operations, resume-by-ID behavior, lack of cancellation/deletion, and finalization without next-item creation are documented.
- Expected: no unsupported automation is implied.

## TC-5: Persistence and Regression Validation

- Assert the feature list has one persistence claim and the Git-isolation caveat remains.
- Run the focused module and full suite with coverage.
- Expected: all tests pass with no package version or runtime source changes.
