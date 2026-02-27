# SFI-008 Project Owner Assistant Notes

## Work Item
- **ID**: SFI-008
- **Profile**: Express
- **Created**: 2026-02-04

## Request Analysis

User compared S360Reporter ItemDetailsModal with actual S360 portal and identified:

1. **Missing Fields**:
   - `Details` - Remediation command (e.g., `Set-SubscriptionGDPRScan -ServiceTreeId...`)
   - `ResourceURIs` - JSON array of resource URLs
   - `url` - Documentation link
   - `TenantName` - e.g., "AME", "Microsoft"
   - `SubscriptionId` / `SubscriptionName` - Azure subscription info
   - `S360_AssignedToName` - Human-readable name
   - `S360_ServiceTreeServiceName` - Service name
   - `Admins` - Admin aliases

2. **Hyperlinks Not Clickable**:
   - S360 portal has clickable links
   - Current app just shows text

## Technical Findings

API returns 36 columns but we only request `S360_ProgramIds` column filter.

Solution:
1. Remove column filter to get all fields
2. Parse URL fields and HTML anchors
3. Make hyperlinks clickable in Tkinter (using Text widget with tag bindings)

## Decision

- Express workflow appropriate (additive feature, clear requirements)
- Single user story covers both data parity and hyperlinks (cohesive feature)
