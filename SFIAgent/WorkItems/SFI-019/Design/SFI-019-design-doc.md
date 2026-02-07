# SFI-019 Design Document — Set ETAs / Statuses

## Summary

Add the ability to update ETA dates and user statuses for SFI action items directly from the SFI Reporter tkinter app. Two entry points: (1) a main-screen button for bulk updates of all invalid-ETA items, and (2) an individual "Update ETA" button in the detail view.

## Problem Statement

Users currently must open the S360 web portal or run a separate Sauron script to update ETAs. This is friction-heavy: the portal requires navigating to each item individually, and the Sauron script is a separate tool with its own auth flow. SFI Reporter already displays all the data needed — it just can't write back.

## Business Case

- **Why now**: SFI Reporter is the daily tool for SFI triage; adding write-back closes the loop in a single app
- **Impact**: Reduces ETA-update workflow from ~2 min/item (portal) to ~5 sec/item (app)
- **KPIs**: Number of invalid-ETA items should decrease; users spend less time context-switching

## Stakeholders

- **End users**: Engineers and managers who own SFI action items
- **SFI Reporter maintainer**: Brent (sole developer)
- **Upstream dependency**: S360 API team (owns `SaveETAsByIds` endpoint)

## Functional Requirements

### FR-1: Main Screen — "Update All Invalid ETAs" Button
- New button in the controls frame next to Filter
- On click, opens a dialog with two choices: **Manual** or **Bulk**
- Button is disabled when no data is loaded

### FR-2: Manual Mode
- Iterates through items where `is_invalid_eta(EtaDate)` is True
- For each item, shows a modal with:
  - Item title, service, KPI, current ETA, due date
  - Proposed ETA (calculated via end-of-month logic)
  - Editable ETA date field (pre-filled with proposed date)
  - Editable status/notes field
  - Accept / Skip / Cancel buttons
- On Accept: calls S360 `SaveETAsByIds`, moves to next item
- On Skip: moves to next item without saving
- On Cancel: aborts remaining items
- Shows summary at end (saved, skipped, failed)

### FR-3: Bulk Mode
- Shows count of invalid-ETA items and asks for confirmation
- On confirm: auto-applies proposed ETA date to all items sequentially
- Progress bar or counter shown during processing
- Shows summary at end (saved, failed)

### FR-4: Detail View — Individual Update
- New "Update ETA" button in `ItemDetailsModal` button bar
- Opens a small dialog with:
  - Current ETA (read-only)
  - New ETA date field (pre-filled with proposed date)
  - Status/notes field
  - Save / Cancel buttons
- On Save: calls S360 `SaveETAsByIds` for that single item

### FR-5: Cache Refresh After Save
- After any successful save, update `EtaDate` and `EtaStatus` in `detailed_items` for the affected item(s)
- Recompute `invalid_eta` counts in service/kpi/program stats
- Re-render tables without a full API refresh

## Non-Functional Requirements

- All S360 API calls on background threads (UI stays responsive)
- Sequential saves in bulk mode (no parallel POST requests) to avoid rate limiting
- No new pip dependencies

## Proposed Approach

### Layer 1: ETA Proposal Logic (new module)

Create `SFIReporter/src/sfi_reporter/eta_logic.py`:
- `propose_eta(due_date: str | None) -> str` — end of month, at least 2 weeks from now or due date (whichever later). Ported from Sauron's `ETAProcessor.propose_eta_date()`.
- `get_items_needing_eta_update(items: list[dict]) -> list[dict]` — filters to items where `is_invalid_eta()` returns True.

### Layer 2: S360 Save Integration (modify accia-s360)

**Critical**: The existing `accia-s360` `save_etas()` uses a payload format `{ items: [...] }` that may not match the actual S360 API. The Sauron reference uses:
```json
{
  "ETADate": "2026-02-28",
  "UserStatus": "status text",
  "KpiId": "guid",
  "ActionItems": [{
    "ServiceId": "guid",
    "ActionItemId": "id",
    "AssignedTo": "alias",
    "SLAType": "InSla"
  }]
}
```

**Decision**: Update `EtaUpdate.to_api_payload()` and `ActionItemsEndpoint.save_etas()` to match the Sauron format. The `save_eta()` convenience method on `S360Client` stays unchanged (just passes through).

### Layer 3: UI Components (modify tk_app.py)

1. **`EtaUpdateDialog`** — tkinter `Toplevel` for Manual/Bulk mode selection
2. **`ManualEtaReviewDialog`** — steps through items one at a time
3. **`BulkEtaProgressDialog`** — shows progress bar during bulk update
4. **`SingleEtaEditDialog`** — small form for individual item update from detail view
5. Wire "Update All Invalid ETAs" button into `SFIReporterApp._build_ui()`
6. Wire "Update ETA" button into `ItemDetailsModal._build_content()`

### Layer 4: Post-Save Cache Update

After successful save(s):
- Mutate `detailed_items` in `current_data` (update EtaDate, EtaStatus)
- Call `_update_tables(current_data)` to re-render
- Write updated data back to disk cache

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Use `ChainedTokenCredential` for save auth | Same auth as reads — already handled by SFI-018 |
| Parallel bulk saves | Risk of S360 rate-limiting; sequential is safer |
| Date picker widget | tkinter's built-in date entry is adequate; `tkcalendar` would add a dependency |
| Separate "Set Status" feature | Status and ETA are submitted together in one API call; splitting would be confusing |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `SaveETAsByIds` payload format mismatch | Medium | High | Test with a single real item first; compare with Sauron's working payload |
| User accidentally bulk-updates wrong items | Low | Medium | Confirmation dialog shows item count; Manual mode is the default |
| S360 API rate limiting on bulk | Low | Medium | Sequential calls with no parallelism |

## Open Questions

1. Does `SaveETAsByIds` accept `AssignedTo` as the user's alias, or does it use the caller's identity from the bearer token? (Test empirically)
2. Should the proposed ETA also consider `SlaType` to prioritize out-of-SLA items? (Defer to future work item)

## Dependencies

- `accia-s360` package (already installed, auth chain from SFI-018)
- S360 API `POST /ActionItems/SaveETAsByIds` endpoint
- Existing `is_invalid_eta()` in `sfi_reporter/data.py`

## Test Strategy

- Unit tests for `eta_logic.py` (propose_eta, get_items_needing_eta_update)
- Unit tests for updated `EtaUpdate.to_api_payload()` format
- Mock-based integration tests for save flow (mock S360 API, verify payload)
- Manual smoke test: update one real item, verify in S360 portal
