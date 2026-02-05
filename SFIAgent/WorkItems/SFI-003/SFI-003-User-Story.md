# SFI-003: SFIReporter - View My SFI/QEI Items

**Status**: IMPLEMENTED

## User Story

- **Title:** SFIReporter - View My SFI/QEI Items
- **As a:** Service owner
- **I want:** A web application that auto-detects my identity and shows all SFI/QEI action items for services I own
- **So that:** I can quickly see my compliance status without navigating the S360 portal

## Out of Scope
- Editing or updating action items
- Creating exceptions or ETAs
- User management / multi-user support
- Exporting to Excel/PDF (future iteration)
- Filtering by specific KPI (future iteration)

## Assumptions
- **Assumption (explicit):** Uses `accia-s360` package (SFI-002 must be completed first)
- **Assumption (explicit):** Authentication via Azure CLI credentials (same as s360_client)
- **Assumption (explicit):** Local cache stored in user's temp directory as JSON
- **Assumption (explicit):** Cache expires after 1 hour

## Acceptance Criteria
- [ ] Application launches via `streamlit run app.py`
- [ ] User's alias is auto-detected and displayed in an editable text box
- [ ] User can change the alias and refresh data
- [ ] All SFI/QEI action items for user's services are displayed in a table
- [ ] Table shows: KPI Name, Service, Due Date, SLA Status, Cloud
- [ ] Data is cached locally and refreshed on demand
- [ ] Loading state is shown while fetching data

## Non-Functional Requirements
- Initial load time < 10 seconds (with cache)
- Works on Windows, Mac, Linux
- Responsive UI (works on 1920x1080 and smaller)

## Telemetry / Metrics Expected
- None for first iteration

## Rollout / Rollback Notes
- Standalone application, no deployment required
- Users run locally via `streamlit run`
