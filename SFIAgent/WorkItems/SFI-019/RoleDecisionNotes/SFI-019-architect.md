# SFI-019 Architect Notes

## Binding Decisions Summary

| ID | Decision | Scope |
|----|----------|-------|
| BD-1 | Payload format matches Sauron reference; `EtaUpdate` gains `assigned_to` field; `save_etas()` sends one request per update (not batched) | `accia-s360/models.py`, `accia-s360/endpoints/action_items.py` |
| BD-2 | `AssignedTo` sourced from item's `ActionOwnerAlias` → `S360_AssignedTo` → `assignedTo` → current user alias | `sfi_reporter/eta_logic.py` |
| BD-3 | `SLAType` mapped directly from `item['SlaType']`, default `"InSla"` | `sfi_reporter/eta_logic.py` |
| BD-4 | `eta_logic.py` in SFI Reporter package, not in `accia-s360` | `SFIReporter/src/sfi_reporter/` |
| BD-5 | Only `accia-s360` modified, not `src/s360_client/` | — |
| BD-6 | Date validation: YYYY-MM-DD, ≥ today, ≤ 1 year out | UI dialogs |

## File Change Map

| File | Change Type | Description |
|------|-------------|-------------|
| `accia-s360/src/accia_s360/models.py` | Modify | Add `assigned_to` field to `EtaUpdate`; rewrite `to_api_payload()` to produce Sauron-format payload |
| `accia-s360/src/accia_s360/endpoints/action_items.py` | Modify | Change `save_etas()` to send one POST per update with correct payload shape |
| `accia-s360/src/accia_s360/client.py` | Modify | Update `save_eta()` convenience method to pass `assigned_to` |
| `SFIReporter/src/sfi_reporter/eta_logic.py` | New | `propose_eta()`, `get_items_needing_eta_update()`, `build_eta_update()` |
| `SFIReporter/src/sfi_reporter/tk_app.py` | Modify | Add button, dialog classes, wire into `ItemDetailsModal` |
| `accia-s360/tests/test_eta_payload.py` | New | Tests for updated payload format (TC-06, TC-07, TC-08) |
| `SFIReporter/tests/test_eta_logic.py` | New | Tests for eta_logic functions (TC-01 through TC-05) |
| `SFIReporter/tests/test_eta_ui.py` | New | Tests for UI flow/validation (TC-09 through TC-15) |

## Architectural Concerns

None blocking. The change is well-contained:
- `accia-s360` payload fix affects only ETA writes (no reads impacted)
- New `eta_logic.py` is pure functions with no side effects
- UI dialogs follow the existing modal pattern (`DetailModal`, `ItemDetailsModal`)
