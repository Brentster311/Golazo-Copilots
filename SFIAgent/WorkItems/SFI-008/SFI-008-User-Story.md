# SFI-008: Full S360 Data Parity with Clickable Hyperlinks

**Status**: IMPLEMENTED

## User Story

- **Title**: Full S360 Data Parity with Clickable Hyperlinks
- **As a**: Security engineer using the SFI Reporter
- **I want**: To see all available action item fields matching S360 portal, with clickable hyperlinks
- **So that**: I have feature parity with the S360 web portal and can access linked resources directly

## Out of Scope

- Editing action items from SFI Reporter
- Displaying the full HTML Description tab content (we show raw data)
- Opening hyperlinks in embedded browser (uses system default browser)

## Assumptions

- **Assumption (explicit)**: Tkinter desktop application (existing UI)
- **Assumption (explicit)**: System default browser for hyperlink opening
- **Assumption (explicit)**: All additional fields are fetched during existing refresh operation

## Acceptance Criteria

- [ ] Item details view shows all available fields from S360 API including: Details, ResourceURIs, url, TenantName, SubscriptionId, SubscriptionName, S360_AssignedToName, S360_ServiceTreeServiceName, Admins
- [ ] URLs in any field are rendered as clickable hyperlinks (blue, underlined)
- [ ] Clicking a hyperlink opens it in the system default browser
- [ ] HTML anchor tags in title field are parsed to extract and display the URL
- [ ] ResourceURIs array is rendered as a list of clickable links
- [ ] All existing tests continue to pass

## Non-functional Requirements

- No additional API calls required (fetch all columns in existing grid call)
- Hyperlinks should be accessible via keyboard (Tab navigation)

## Telemetry / Metrics Expected

- None required for this feature

## Rollout / Rollback Notes

- Feature is additive, no breaking changes
- Cache will be refreshed to include new fields on first use
