# SFI-019 Developer Notes

## TDD Approach
- **Red phase**: Created 3 test files with 17 tests total (5 logic, 3 payload, 9 UI). Confirmed all fail initially.
- **Green phase**: Implemented production code across 4 modules to make all 17 tests pass.

## Files Changed

### New Files
| File | Purpose |
|------|---------|
| `GUI/src/sfi_reporter/eta_logic.py` | Pure functions: `propose_eta()`, `get_items_needing_eta_update()`, `validate_eta_date()`, `build_eta_update()` |
| `GUI/tests/test_eta_logic.py` | 5 tests (TC-01 through TC-05) |
| `GUI/tests/test_eta_ui.py` | 9 tests (TC-09 through TC-15 + 2 bonus) |
| `accia-s360/tests/test_eta_payload.py` | 3 tests (TC-06 through TC-08) |

### Modified Files
| File | Change |
|------|--------|
| `accia-s360/src/accia_s360/models.py` | `EtaUpdate.to_api_payload()` rewritten to Sauron format; added `assigned_to` field |
| `accia-s360/src/accia_s360/endpoints/action_items.py` | `save_etas()` sends one POST per update |
| `accia-s360/src/accia_s360/client.py` | `save_eta()` accepts `assigned_to` parameter |
| `GUI/src/sfi_reporter/tk_app.py` | 4 dialog classes + 2 buttons + post-save cache refresh |

## UI Dialog Classes Added to tk_app.py
1. **`SingleEtaEditDialog`** — edit one item's ETA from detail view (AC-4)
2. **`EtaModeDialog`** — Manual/Bulk mode chooser (AC-1)
3. **`ManualEtaReviewDialog`** — step through items one-at-a-time (AC-2)
4. **`BulkEtaProgressDialog`** — auto-apply with progress bar (AC-3)

## Wiring Points in SFIReporterApp
- `📋 Update ETAs` button in controls_frame (disabled until data loads)
- `_on_update_etas()` — filters for invalid ETAs, opens mode dialog
- `_on_eta_update_complete()` — mutates in-memory items, recomputes stats, re-renders tables, writes cache
- `📅 Update ETA` button in `ItemDetailsModal` button bar

## Key Design Decisions Followed
- BD-1: Payload format matches Sauron (`ETADate`, `UserStatus`, `KpiId`, `ActionItems` array)
- BD-2: AssignedTo priority chain: `ActionOwnerAlias` → `S360_AssignedTo` → `assignedTo` → fallback
- BD-4: `eta_logic.py` in S360Reporter package
- BD-5: Only accia-s360 modified (not `src/s360_client/`)
- BD-6: Date validation: YYYY-MM-DD, ≥ today, ≤ 1 year

## Test Results
- S360Reporter: **147 passed** (including 17 new ETA tests)
- accia-s360: **29 passed** (including 3 new payload tests)
- Total: **176 tests all green**
