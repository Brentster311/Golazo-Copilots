# SFI-004: S360Reporter - Convert to Flet Desktop App

**Status**: IMPLEMENTED

## User Story

- **Title:** S360Reporter - Convert to Flet Desktop App
- **As a:** Service owner
- **I want:** A native Windows desktop application instead of a web app
- **So that:** I can run the reporter without a browser and have a more responsive experience

## Out of Scope
- macOS/Linux builds (future iteration)
- Packaging as .exe installer (future iteration)
- System tray integration
- Auto-start at login
- New features beyond existing SFI-003 functionality

## Assumptions
- **Assumption (explicit):** Uses Flet framework for UI
- **Assumption (explicit):** Reuses existing cache.py and data.py modules from SFI-003
- **Assumption (explicit):** Same authentication via Azure CLI credentials
- **Assumption (explicit):** Same 1-hour cache expiration behavior

## Acceptance Criteria
- [ ] Application launches as native window (not browser)
- [ ] User alias is auto-detected and shown in editable text field
- [ ] Refresh button fetches fresh data from S360
- [ ] Services displayed in a table/list
- [ ] Action items displayed in a table/list with counts
- [ ] Cache age displayed with visual indicator when > 30 min old
- [ ] Clear cache button works

## Non-Functional Requirements
- Window is resizable
- Initial load < 3 seconds (with cache)
- Responsive UI during data fetch (loading indicator)

## Telemetry / Metrics Expected
- None for first iteration

## Rollout / Rollback Notes
- Replace Streamlit app.py with Flet app.py
- Update pyproject.toml dependencies (remove streamlit, add flet)
- Users run via `python -m sfi_reporter` or entry point
