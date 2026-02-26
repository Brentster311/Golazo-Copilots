# SFI-041 Capability Impact

## Scope and Inputs
Architect impact analysis run against design-referenced files:
- `SFIReporter/src/sfi_reporter/dialogs.py`
- `SFIReporter/src/sfi_reporter/data.py`
- `accia-s360/src/accia_s360/client.py`

## Directly Affected Capabilities

### `reporter-data`
- **Why affected:** owns application/data seam that obtains client and orchestrates Action Owner save call path.
- **Contract surface impacted:** internal orchestration contract for owner-save validation, payload construction, error-category mapping, and success/failure state handling.
- **Compatibility assessment:** additive behavior only; no intended breaking change to existing read/query/ETA paths.

### `accia-s360-client`
- **Why affected:** persistence relies on `S360Client.save_action_owners(...)` contract and endpoint behavior.
- **Contract surface impacted:** write-operation invocation semantics, auth/session failure signaling, and response/error mapping expectations at caller seam.
- **Compatibility assessment:** no API signature change proposed; caller enforces stricter preflight validation before invocation.

## Transitively Affected Capabilities

### `reporter-tk-app`
- **Dependency path:** `dialogs.py` -> `reporter-data` orchestration.
- **Impact:** details dialog UX now includes owner save affordance and deterministic save-state behavior.
- **Risk level:** medium (user-facing flow), mitigated by explicit single-flight and failure messaging rules.

### `reporter-tests`
- **Dependency path:** tests cover data/UI seams affected by owner-save flow.
- **Impact:** requires targeted additions for payload validation, save success mutation timing, and failure categories.
- **Risk level:** low (test expansion only).

### `reporter-eta-logic`
- **Dependency path:** shared dialog/data execution surfaces.
- **Impact:** regression-risk only; no contract or behavior changes intended.
- **Risk level:** low with focused regression checks.

### `reporter-query-builder`
- **Dependency path:** shared Tk app shell and session flow.
- **Impact:** regression-risk only; no owner-save coupling intended.
- **Risk level:** low.

### `reporter-llm`
- **Dependency path:** shared app packaging/runtime.
- **Impact:** transitive packaging/runtime risk only; no contract impact.
- **Risk level:** low.

### `reporter-build`
- **Dependency path:** packaging includes modified reporter modules.
- **Impact:** build artifact includes updated dialog/data behavior; no build contract change.
- **Risk level:** low.

### `accia-s360-tests`
- **Dependency path:** client contract confidence for `save_action_owners` behavior.
- **Impact:** no required contract changes, but coverage remains dependency guardrail.
- **Risk level:** low.

## Contract Implications
- **New public interfaces:** none.
- **Changed public interfaces:** none.
- **Removed public interfaces:** none.
- **Behavioral tightening (internal):** stricter preflight validation and stable failure-category mapping before/after `save_action_owners` invocation.

## Security and Privacy Impact
- Auth boundary remains unchanged (`get_client()` + existing token flow).
- No new secret material introduced.
- Logging constraints: include only correlation-safe IDs and outcome metadata; exclude tokens, raw exception payloads, and stack traces in user dialogs.

## Failure Handling and Rollback Impact
- Failure isolation requirement: owner-save failures do not mutate owner state or propagate side effects into ETA/query flows.
- Rollback safety: feature-path rollback by disabling/removing owner-save trigger while preserving read-only owner visibility.
- Operational guardrail: if write failures spike, keep details dialog usable in read mode and suppress write path.

## Architect Conclusion
Capability impact is acceptable for implementation within current scope. The change is additive with bounded blast radius when validation, failure categorization, and feature-path rollback controls are implemented as specified.
