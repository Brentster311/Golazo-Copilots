# GCP-0070 QA Test Cases

## Traceability Matrix
- AC1 tool removal from advertised/dispatch surfaces: TC-001, TC-002, TC-003
- AC2 spine install guidance present: TC-004, TC-005
- AC3 README/install documentation updated: TC-006
- AC4 automated tests cover removal and replacement guidance: enforced by running the focused suite

## Functional Tests

### TC-001 Registry no longer advertises golazo_update
- **Type**: Unit
- **Covers**: AC1
- **Steps**:
  1. Load tool definitions from the modular registry.
  2. Assert `golazo_update` is absent.
- **Expected Outcome**:
  - `golazo_update` is not present in the advertised tool list.
- **Failure Message**:
  - `AC1_FAIL_TOOL_STILL_REGISTERED: golazo_update is still advertised in tool definitions.`

### TC-002 Modular dispatch no longer routes golazo_update
- **Type**: Unit
- **Covers**: AC1
- **Steps**:
  1. Invoke modular dispatch/handler behavior for known tools.
  2. Assert there is no `golazo_update` branch requirement and no self-check expectation for it.
- **Expected Outcome**:
  - Dispatch/tests do not require `golazo_update`.
- **Failure Message**:
  - `AC1_FAIL_MODULAR_DISPATCH_REFERENCE: Modular dispatch still expects golazo_update.`

### TC-003 Legacy server no longer imports or formats golazo_update
- **Type**: Unit
- **Covers**: AC1
- **Steps**:
  1. Exercise legacy server coverage/self-check expectations.
  2. Assert legacy output no longer references `golazo_update` as a supported tool path.
- **Expected Outcome**:
  - No live legacy path requires the removed tool.
- **Failure Message**:
  - `AC1_FAIL_LEGACY_REFERENCE: Legacy server still exposes golazo_update behavior.`

### TC-004 Bootstrap spine includes pip install guidance
- **Type**: Unit
- **Covers**: AC2
- **Steps**:
  1. Run `golazo_bootstrap` into a temporary workspace.
  2. Read generated `.github/agents/Golazo-Copilot.md`.
  3. Assert the content includes `pip install` guidance for `golazo-copilot` from the correct feed/location.
- **Expected Outcome**:
  - Generated orchestrator instructions contain the new install guidance.
- **Failure Message**:
  - `AC2_FAIL_SPINE_INSTALL_GUIDANCE: Bootstrap-generated spine is missing correct pip install guidance.`

### TC-005 Removed update guidance no longer appears in bootstrap/server text
- **Type**: Unit
- **Covers**: AC1, AC2
- **Steps**:
  1. Inspect formatter/bootstrap/server output paths touched by this change.
  2. Assert `golazo_update(` usage guidance is absent where replaced by install guidance.
- **Expected Outcome**:
  - Removed tool guidance is gone from active output paths.
- **Failure Message**:
  - `AC2_FAIL_STALE_UPDATE_GUIDANCE: Active output still points users to golazo_update.`

### TC-006 README no longer describes golazo_update as a supported tool
- **Type**: Documentation verification
- **Covers**: AC3
- **Steps**:
  1. Inspect README sections for supported tools and installation/update guidance.
  2. Assert README no longer documents `golazo_update` as available and instead points users to `pip install`/`pip install --upgrade` guidance.
- **Expected Outcome**:
  - README matches the removed tool surface.
- **Failure Message**:
  - `AC3_FAIL_README_STALE: README still documents golazo_update or lacks replacement install guidance.`

## Execution Guidance
- Run focused tests covering bootstrap, registry, dispatch, server formatter behavior, and any former `golazo_update` assumptions.
- Remove or rewrite dedicated `golazo_update` tests so the suite validates absence rather than obsolete behavior.
