# SFI-019 — Set ETAs / Statuses

**Status**: IMPLEMENTED

## User Story

- **Title**: Set ETAs and Statuses (Bulk & Individual)
- **As a**: S360Reporter user
- **I want**: to update invalid ETAs and statuses directly from the app — either all at once via a bulk/manual workflow from the main screen, or individually from the detail view
- **So that**: I can keep my SFI action items compliant without switching to the S360 web portal or using a separate script

## Out of Scope

- Updating fields other than ETA and status (e.g., action owner, service mapping)
- Kusto-based data retrieval (the Sauron `SFI_Agent` uses Kusto; we use the existing S360 REST API)
- Auto-scheduling or recurring ETA updates
- Undo/revert of submitted ETA changes (S360 API does not support this)

## Assumptions

- **Assumption (explicit)**: The S360 `POST /ActionItems/SaveETAsByIds` endpoint accepts the payload format used by the Sauron `SFI_Agent` reference: `{ ETADate, UserStatus, KpiId, ActionItems: [{ ServiceId, ActionItemId, AssignedTo, SLAType }] }`. The existing `accia-s360` `EtaUpdate.to_api_payload()` may need to be adjusted to match this proven format.
- **Assumption (explicit)**: An item "needs ETA update" if `is_invalid_eta()` returns True (ETA is missing or in the past). This matches the existing `invalid_eta` column in the summary tables.
- **Assumption (explicit)**: The proposed ETA date logic follows the Sauron reference: end of month, at least 2 weeks from now (or due date if later).
- **Assumption (explicit)**: "Status" in this context means the `UserStatus` / `EtaStatus` field — the free-text note that accompanies an ETA submission.
- **Assumption (explicit)**: Each item in `detailed_items` already has `_kpi_id`, `S360_ServiceId`, `id` (action item ID), `SlaType`, `EtaDate`, `EtaStatus`, and `ActionOwnerAlias` — sufficient to build the save payload.

## Acceptance Criteria

- [ ] **AC-1**: Main screen has an "Update All Invalid ETAs" button; clicking it shows a dialog asking "Manual" (review each item) or "Bulk" (auto-apply proposed dates to all)
- [ ] **AC-2**: In Manual mode, each invalid-ETA item is presented one at a time with proposed ETA and status; user can Accept, Edit, or Skip each item
- [ ] **AC-3**: In Bulk mode, all invalid-ETA items get proposed dates auto-applied with a single confirmation prompt; a progress indicator and summary are shown
- [ ] **AC-4**: In the detail view (`ItemDetailsModal`), an "Update ETA" button lets the user set a new ETA date and status for that single item and submit it
- [ ] **AC-5**: After any successful ETA update (single or bulk), the local cache and table display are refreshed to reflect the new ETA values
- [ ] **AC-6**: Errors from the S360 API are shown to the user in a message box with the failing item ID and error detail

## Non-Functional Requirements

- ETA save calls run on a background thread so the UI remains responsive
- Bulk updates are sequential (one API call per item) to avoid rate-limiting; progress is reported
- No new pip dependencies (uses existing `accia-s360` client)

## Telemetry / Metrics Expected

- Log each ETA save attempt (item ID, proposed date, success/fail) at INFO level
- Log bulk summary (total, succeeded, failed, skipped) at INFO level

## Rollout / Rollback Notes

- Feature is additive — new button and dialog; no existing behavior changes
- If S360 API payload format is wrong, the `accia-s360` `save_etas` method is the single change point (same pattern as SFI-018)
