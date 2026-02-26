# SFI-041 Architect Role Decision Notes

## Decision Summary
- **Decision:** Approve architecture direction for Action Owner persistence from details dialog, with explicit guardrails.
- **Result:** No architectural scope change required; proceed to implementation with constraints below.
- **Escalation:** Not required at this stage.

## Key Architectural Decisions
1. **Layered boundary enforcement**
   - UI (`dialogs.py`) remains event/presentation only.
   - Orchestration/validation belongs in `sfi_reporter.data` seam.
   - API/auth transport remains exclusively in `accia_s360` client.
2. **Strict API contract preflight**
   - Require: `KpiId`, `ServiceId`, `ActionItemId`, `SLAType`, `ActionOwnerAlias`, `ActionOwnerName`.
   - Reject partial/empty owner values before API call.
3. **Deterministic failure model**
   - Standardize categories: `validation_failure`, `auth_failure`, `network_failure`, `api_failure`, `unknown_failure`.
   - Preserve prior owner UI state on any failure.
4. **Single-flight save control**
   - Disable Save while request is active to prevent duplicate submissions and race conditions.
5. **Rollback-safe feature path**
   - Rollback by disabling owner-write trigger only; keep details dialog read flow intact.

## Security and Privacy Review Outcome
- Existing token-based auth boundary is preserved; no new secrets or auth pathways.
- User-facing errors must remain non-technical and avoid exception leakage.
- Telemetry/logging must exclude tokens and sensitive internals; include only safe identifiers and duration/outcome metadata.

## API Contract and Compatibility Assessment
- No new public APIs required.
- No public API signature changes required for `save_action_owners` in this story.
- Compatibility expectation: additive behavior in reporter layer, with no change to existing read paths.

## Failure Isolation and Operability
- Owner-save failures are isolated from ETA and query-builder functionality.
- On-call operability improves via explicit error categories and attempt/success/failure telemetry.
- If elevated write failures occur, operational fallback is read-only owner display by suppressing write path.

## Assumptions (Explicit)
- Details context reliably contains required IDs for one-item save payload.
- Owner input control can provide valid alias+name pair deterministically.
- `S360Client.save_action_owners(...)` behavior/endpoint remains stable for this release window.
- Windows-only scope remains acceptable and intentional.

## Open Questions Captured for PO
1. Should alias normalization alter only API payload or also persisted/displayed UI formatting?
2. Should success messaging depend solely on API success or additionally require refresh confirmation?
3. On auth-expired errors, should Save remain enabled for immediate retry after re-auth or be gated until session refresh confirmation?

## New User Story Check
- No new user story created.
- Rationale: current scope supports safe implementation without changing system architecture or expanding behavior boundaries.
