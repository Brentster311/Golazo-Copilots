# SFI-019 Program Manager Notes

## Key Decisions

1. **Single module for ETA logic** (`eta_logic.py`) — keeps proposal/filtering logic separate from UI and API code
2. **Fix payload format in accia-s360** — the current `to_api_payload()` doesn't match the Sauron reference that works in production. This is a critical path item.
3. **No date picker dependency** — tkinter Entry with YYYY-MM-DD format validation is sufficient; avoids `tkcalendar` dependency
4. **Sequential bulk saves** — one API call per item to avoid rate limiting. Progress reporting via dialog counter.
5. **Post-save in-memory update** — mutate the local cache rather than doing a full refresh. A full refresh would take 30+ seconds; local update is instant.

## Sequencing

1. Fix `EtaUpdate.to_api_payload()` format (prerequisite — must work before any UI)
2. Create `eta_logic.py` (pure functions, easy to test)
3. Build UI dialogs (Manual, Bulk, Single)
4. Wire into main app + detail view
5. Add cache refresh logic

## Open Risk: Payload Format

The accia-s360 `save_etas()` wraps updates in `{ "items": [...] }`. The Sauron reference posts each batch as `{ "ETADate": ..., "KpiId": ..., "ActionItems": [...] }`. These are fundamentally different shapes. The developer MUST validate with a real API call early in the sprint.
