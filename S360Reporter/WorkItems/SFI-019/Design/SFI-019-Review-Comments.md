# SFI-019 Review Comments

## Design Critique

### RC-1: Payload Format — CRITICAL

**Finding**: The design correctly identifies that `accia-s360`'s current `save_etas()` wraps payloads in `{ "items": [...] }`, but the Sauron reference (which works in production) uses `{ "ETADate": ..., "KpiId": ..., "ActionItems": [...] }`. These are incompatible.

**Recommendation**: The `EtaUpdate` model and `ActionItemsEndpoint.save_etas()` must be updated to match the Sauron format. The current `EtaUpdate.to_api_payload()` produces per-item dicts; the API expects a top-level wrapper with `ETADate`, `UserStatus`, `KpiId`, and an `ActionItems` array. This means `save_etas` should accept a single ETA date + status that applies to one or more action items sharing the same KPI — or (more commonly) be called once per item.

**Severity**: Blocker — nothing works without this fix.

### RC-2: AssignedTo Field Source

**Finding**: The Sauron payload includes `"AssignedTo": alias` in each ActionItem. The design doesn't specify where this comes from in the S360Reporter context.

**Recommendation**: Use the `ActionOwnerAlias` field from `detailed_items` (the person currently assigned), falling back to the logged-in user's alias. The architect should bind this decision.

### RC-3: SLAType Mapping

**Finding**: The items in `detailed_items` have `SlaType` as a string like `"OutOfSla"`, `"InSla"`, `"ApproachingSla"`. The Sauron payload uses `SLAState` from Kusto data. Need to confirm the API field name is `SLAType` and accepts these string values.

**Recommendation**: Map directly from `item['SlaType']` with fallback to `"InSla"`.

### RC-4: Date Validation in Manual/Single Edit

**Finding**: User can type a custom date. No validation mentioned.

**Recommendation**: Validate format (YYYY-MM-DD), ensure date is not in the past, show inline error. Also reject dates more than 1 year out as a sanity check.

### RC-5: Empty State for "No Invalid ETAs"

**Finding**: If all ETAs are valid, what happens when user clicks "Update All Invalid ETAs"?

**Recommendation**: Show a message box: "All ETAs are current — no items need updating."

### RC-6: Post-Save Field Names

**Finding**: The design says "mutate `EtaDate` and `EtaStatus` in `detailed_items`". Need to confirm these are the exact field names in the cached data.

**Recommendation**: Verify from existing `detailed_items` structure. `EtaDate` is confirmed in the treeview mapping. `EtaStatus` is used in `COLUMN_DISPLAY_NAMES`. Both are correct.

---

## Architect Notes

### Binding Decision BD-1: Payload Format (resolves RC-1)

The S360 `POST /ActionItems/SaveETAsByIds` API expects:

```json
{
  "ETADate": "2026-02-28",
  "UserStatus": "Working on remediation",
  "KpiId": "guid",
  "ActionItems": [{
    "ServiceId": "guid",
    "ActionItemId": "id",
    "AssignedTo": "alias",
    "SLAType": "InSla"
  }]
}
```

**Changes required in `accia-s360`**:

1. **`EtaUpdate` model** — add `assigned_to: str` field. Rename `to_api_payload()` to produce the top-level wrapper format (not per-item). The `ETADate` and `UserStatus` are top-level; `ActionItems` is an array of `{ServiceId, ActionItemId, AssignedTo, SLAType}`.

2. **`ActionItemsEndpoint.save_etas()`** — post each `EtaUpdate` as its own API call (one request per item), not wrapped in `{"items": [...]}`. Each call sends the full payload above.

3. **`S360Client.save_eta()` convenience method** — update to pass `assigned_to`.

**Rationale**: The Sauron reference has been running in production successfully. Our speculative `{"items": [...]}` wrapper was never tested against the real API.

### Binding Decision BD-2: AssignedTo Source (resolves RC-2)

Use `item.get('ActionOwnerAlias')` or `item.get('S360_AssignedTo')` from the detailed item data, falling back to the logged-in user's alias (from `get_current_user_alias()`).

Priority order: `ActionOwnerAlias` → `S360_AssignedTo` → `assignedTo` → current user alias.

### Binding Decision BD-3: SLAType Mapping (resolves RC-3)

Map directly from `item['SlaType']`. The API field name in the payload is `"SLAType"`.

Valid values from the API: `"InSla"`, `"ApproachingSla"`, `"OutOfSla"`. Default fallback: `"InSla"`.

### Binding Decision BD-4: New Module Location

`eta_logic.py` goes in `GUI/src/sfi_reporter/eta_logic.py` — it is UI-layer logic (ETA proposal, item filtering) not a client-library concern.

### Binding Decision BD-5: No Changes to `s360_client` Package

Only `accia-s360` is modified (the package S360Reporter actually imports). The parallel `src/s360_client/` package is not touched — it's a separate project with its own tests.

### Binding Decision BD-6: Date Validation (resolves RC-4)

- Format: YYYY-MM-DD, validated with `datetime.strptime`
- Must be today or later (not strictly future — today is acceptable for same-day fixes)
- Max 1 year from today as sanity upper bound
- Validation runs on Save click, not on keystroke

### Security Review

- **Token scope**: ETA saves use the same S360 bearer token as reads. No additional permissions needed.
- **Data sensitivity**: No PII in ETA payloads. KPI IDs, service IDs, and aliases are organizational identifiers.
- **CSRF/injection**: Not applicable — desktop app making direct HTTPS API calls.
- **Rate limiting**: Sequential calls mitigate this. No retry loop on 429 (fail and report to user instead).
