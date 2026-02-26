# SFI-041 Design Doc

## Summary
Enable non-technical users to update an action item’s Action Owner directly from the Windows SFIReporter details experience and persist the change through the existing `accia_s360` client path to S360 (`save_action_owners`).

## Problem Statement
Today, SFIReporter shows Action Owner fields but does not provide a GUI persistence path for owner edits. Users who need ownership corrections must use non-GUI/manual backend workflows, which is slow, error-prone, and inaccessible for non-technical operators.

## Business Case
- Why now: Ownership drift blocks remediation execution and creates ambiguity in accountability.
- User impact: Non-technical users can complete ownership maintenance in one GUI flow without scripts.
- Operational impact: Fewer stale owner assignments and fewer manual handoffs to technical staff.
- KPIs:
  - Action Owner save success rate (target: >= 95% in normal network/auth conditions).
  - Median Action Owner save API latency (ms) from click to response.
  - Count of successful Action Owner updates per app session.
  - Failure rate by category (auth, validation, transport/API).

## Stakeholders
- Primary: SFIReporter end users (ICs/managers) maintaining action items.
- Secondary: SFIReporter maintainers and on-call responders.
- Dependency owners: `accia_s360` package maintainers and S360 API owners.

## Functional Requirements
1. In Windows SFIReporter details flow, provide a clear Action Owner input/control for an individual action item.
2. On Save, invoke S360 persistence through the existing package client path (no direct raw HTTP in GUI code):
   - GUI layer (`dialogs.py`) triggers a save action.
   - Application/data layer (`sfi_reporter.data.get_client()`) obtains shared `accia_s360.S360Client`.
   - `S360Client.save_action_owners(...)` persists via S360 endpoint `/ActionItems/SaveActionOwnersByIds`.
3. Required save payload data must come from existing item context (at minimum: `KpiId`, `ServiceId`, `ActionItemId`, `SlaType`, `ActionOwnerAlias`, `ActionOwnerName`).
4. On successful save:
   - Show explicit success feedback.
   - Update in-memory item fields (`ActionOwnerName`, `ActionOwnerAlias`) in the modal/table context.
   - Ensure refreshed/reopened details show updated owner.
5. On failure (API/auth/validation/network):
   - Show a user-friendly error dialog/message.
   - Do not show success state.
   - Preserve previous owner value in UI until a confirmed success occurs.
6. Keep flow fully GUI-driven (no CLI/script dependency).

## Non-Functional Requirements
- Windows-only scope; no Mac/Linux behavior commitments in this story.
- Preserve current authentication/security posture through existing token-based client flow.
- Maintain simple, familiar dialog interaction patterns used by current ETA save experiences.
- Keep changes localized and low risk: dialog + app/data integration + targeted tests.

## Proposed Approach (High Level)
1. UX placement
   - Add Action Owner edit control and Save action in the existing details dialog path (single-item context), reusing established modal button patterns.
2. Data/persistence path
   - Add a small orchestration function in SFIReporter layer that:
     - Validates required IDs and owner input.
     - Builds `action_items=[{"ServiceId": ..., "ActionItemId": ..., "SLAType": ...}]`.
     - Calls `client.save_action_owners(kpi_id, action_owner_alias, action_owner_name, action_items)`.
3. Success path handling
   - Update local item object fields and trigger detail list refresh logic similarly to ETA update completion behavior.
4. Error handling (Windows GUI)
   - Map exceptions/result failures to user-friendly message dialogs (e.g., auth expired, invalid owner, transient API/network failure).
   - Keep dialogs responsive and deterministic (no false-positive success).
5. Telemetry/logging
   - Log one event per attempt: item identity (safe keys), outcome, failure category, elapsed ms.
   - Maintain per-session successful update counter in app state/log output.

## Alternatives Considered
- Direct HTTP call from GUI to S360 endpoint.
  - Rejected: duplicates auth/request/error logic already encapsulated in `accia_s360`.
- Bulk-edit owner in list dialog for multiple items.
  - Rejected for this story: expands scope beyond single-item details flow and increases validation complexity.
- Auto-refresh from server after save only (without optimistic local update).
  - Rejected: slower perceived UX and more moving parts; local update + normal refresh gives simpler behavior.

## Risks, Mitigations, Open Questions
- Risk: API call succeeds but UI cache/state not refreshed consistently.
  - Mitigation: explicit local item mutation + existing refresh method invocation + regression tests.
- Risk: Owner identity ambiguity (name vs alias mismatch).
  - Mitigation: require normalized alias/name pair from selected input and validate before submit.
- Risk: Auth/session expiration causes repeated user failures.
  - Mitigation: clear error messaging and guidance to re-auth/refresh session; log failure type.
- Risk: Partial/invalid item context missing IDs in some rows.
  - Mitigation: preflight validation with blocking error before API call.
- Open question: exact owner picker source (free text vs searched selection) within existing dialog constraints.
  - Assumption for this story: use the simplest existing control pattern that yields both alias and display name reliably.

## Dependencies
- `accia_s360` package availability in runtime environment.
- Existing `S360Client.save_action_owners(...)` API contract and endpoint stability.
- Existing detailed action item fields containing required IDs.
- Tkinter dialog/message primitives already used in SFIReporter.

## Migration / Rollout / Rollback Plan
- Migration: none (no schema/config migration).
- Rollout: include in standard Windows SFIReporter release.
- Rollback: disable/remove Action Owner save trigger in dialog and revert S360 owner-write invocation.
- Safe fallback behavior: retain read-only owner display if save path is disabled.

## Observability Plan
- Add structured logs for:
  - `action_owner_save_attempt`
  - `action_owner_save_success`
  - `action_owner_save_failure`
- Log dimensions: `kpi_id`, `action_item_id`, `service_id`, `duration_ms`, `failure_category`.
- Session metric: successful owner updates count per run/session.
- Ensure logs avoid sensitive token/PII leakage beyond already-visible owner identifiers.

## Test Strategy Summary
- Unit tests:
  - Save payload builder includes required IDs/owner fields.
  - Validation failures prevent API invocation.
  - Success callback mutates in-memory item owner fields correctly.
- GUI behavior tests (Windows scope):
  - Save success shows success feedback and updated owner on refresh/reopen.
  - API failure shows user-friendly error and no false success.
- Integration seam tests:
  - Mock `get_client().save_action_owners(...)` success/failure/auth exception paths.
- Regression:
  - Confirm ETA update and existing detail dialog behaviors remain unchanged.

## Sequencing / Delivery Plan
1. Implement owner save orchestration and validation seam in SFIReporter layer.
2. Add/adjust detail dialog controls and callbacks for Action Owner save.
3. Add success/failure UI handling and refresh wiring.
4. Add telemetry/logging and session counter updates.
5. Complete targeted tests and run existing dialog/ETA regression suite.

## Assumptions (Documented)
- Existing item context includes enough identifiers for `save_action_owners` payload construction.
- Existing auth flow and client construction (`get_client`) remain unchanged.
- Windows-only release path is acceptable; cross-platform parity is explicitly out of scope.
