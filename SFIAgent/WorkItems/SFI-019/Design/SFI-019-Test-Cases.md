# SFI-019 Test Cases

## Test Matrix

Maps to Acceptance Criteria AC-1 through AC-6.

---

### TC-01: `propose_eta()` — basic (AC-1, AC-2, AC-3)

**Given** today is 2026-02-06 and no due date  
**When** `propose_eta(None)` is called  
**Then** returns `"2026-02-28"` (end of Feb, ≥2 weeks from now)

### TC-02: `propose_eta()` — due date in future (AC-2)

**Given** today is 2026-02-06 and due date is `"2026-04-15"`  
**When** `propose_eta("2026-04-15")` is called  
**Then** returns `"2026-04-30"` (end of April, since due date is later than 2 weeks)

### TC-03: `propose_eta()` — due date in past (AC-2)

**Given** today is 2026-02-06 and due date is `"2025-12-01"`  
**When** `propose_eta("2025-12-01")` is called  
**Then** returns `"2026-02-28"` (ignores past due date, uses 2 weeks from now)

### TC-04: `propose_eta()` — December edge case (AC-2)

**Given** today is 2026-12-20  
**When** `propose_eta(None)` is called  
**Then** returns `"2027-01-31"` (2 weeks → Jan, end of Jan)

### TC-05: `get_items_needing_eta_update()` — filters correctly (AC-1)

**Given** 3 items: one with valid future ETA, one with past ETA, one with None ETA  
**When** `get_items_needing_eta_update(items)` is called  
**Then** returns only the 2 invalid items

### TC-06: `EtaUpdate.to_api_payload()` — matches Sauron format (AC-1, RC-1)

**Given** an `EtaUpdate` with kpi_id, service_id, action_item_id, new_eta, notes, assigned_to, sla_type  
**When** `to_api_payload()` is called  
**Then** returns:
```json
{
  "ETADate": "2026-02-28",
  "UserStatus": "Working on remediation",
  "KpiId": "kpi-guid",
  "ActionItems": [{
    "ServiceId": "svc-guid",
    "ActionItemId": "item-id",
    "AssignedTo": "brentj",
    "SLAType": "InSla"
  }]
}
```

### TC-07: `save_etas()` — successful save (AC-5)

**Given** a mocked S360 API that returns 200  
**When** `save_etas([update])` is called  
**Then** returns `SaveResult(success=True)` and cache is invalidated

### TC-08: `save_etas()` — API error (AC-6)

**Given** a mocked S360 API that returns 400  
**When** `save_etas([update])` is called  
**Then** returns `SaveResult(success=False, error_message=...)` containing status code

### TC-09: Bulk mode — all items updated (AC-3)

**Given** 3 items with invalid ETAs and mock API returning 200  
**When** bulk update is executed  
**Then** all 3 are saved, summary shows "3 saved, 0 failed"

### TC-10: Bulk mode — partial failure (AC-3, AC-6)

**Given** 3 items, mock API returns 200 for first 2, 500 for third  
**When** bulk update is executed  
**Then** summary shows "2 saved, 1 failed" and error detail for the failed item is logged

### TC-11: Manual mode — skip item (AC-2)

**Given** 2 items with invalid ETAs  
**When** user clicks Skip on item 1, Accept on item 2  
**Then** only item 2 is saved, summary shows "1 saved, 1 skipped"

### TC-12: Single item update from detail view (AC-4)

**Given** a single item dict with `_kpi_id`, `S360_ServiceId`, `id`, valid `SlaType`  
**When** user edits ETA to "2026-03-31" and clicks Save  
**Then** `save_eta()` is called with correct payload, item's `EtaDate` is updated in cache

### TC-13: No invalid items — empty state (AC-1, RC-5)

**Given** all items have valid future ETAs  
**When** "Update All Invalid ETAs" button is clicked  
**Then** dialog shows "All ETAs are current" message, no API calls made

### TC-14: Date validation — past date rejected (RC-4)

**Given** user enters "2025-01-01" as new ETA  
**When** Save is clicked  
**Then** error shown: "ETA date must be in the future"

### TC-15: Date validation — invalid format rejected (RC-4)

**Given** user enters "not-a-date"  
**When** Save is clicked  
**Then** error shown: "Invalid date format. Use YYYY-MM-DD"

---

## Coverage Summary

| AC | Test Cases |
|----|-----------|
| AC-1 | TC-01, TC-05, TC-06, TC-13 |
| AC-2 | TC-02, TC-03, TC-04, TC-11 |
| AC-3 | TC-09, TC-10 |
| AC-4 | TC-12 |
| AC-5 | TC-07, TC-12 |
| AC-6 | TC-08, TC-10 |
| RC-4 | TC-14, TC-15 |
| RC-5 | TC-13 |
