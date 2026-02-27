# SFI-013: Service Summary Grouped by Owner

**Status**: IMPLEMENTED

## User Story

**Title**: Service Summary Grouped by Owner (Manager View)

**As a**: Manager viewing S360Reporter for my team

**I want**: To see a "Service Summary (by Owner)" section that groups services by the DevOwner (my direct reports or myself)

**So that**: 
- I can quickly see which team members have the most action items
- I can identify team members with SLA issues needing attention
- I can have accountability visibility at the person level, not just service level

## Out of Scope
- Drilling into a specific person's services (future work)
- Showing people who are not direct owners (contributors, admins)
- Hierarchical view beyond one level (directs of directs)
- Persisting owner data to cache (fetch fresh each time for MVP)

## Assumptions
- **Assumption (explicit)**: Interface is existing Tkinter desktop app
- **Assumption (explicit)**: Uses existing S360 API - `search()` API returns `Owners` field for each service
- **Assumption (explicit)**: When user is a manager (has TeamGroup in landing view), show the grouped view
- **Assumption (explicit)**: Owner matching uses first name from Owners list only (e.g., "Brent Jensen" → group all services where Brent Jensen is in Owners)
- **Assumption (explicit)**: If a service has multiple owners, count it under each owner
- **Assumption (explicit)**: "Self" grouping for services owned by the logged-in user

## Acceptance Criteria

- [ ] **AC1**: When user is a manager (TeamGroup in landing view), a new "Service Summary (by Owner)" section appears
- [ ] **AC2**: Services are grouped by owner name, showing aggregated stats (count, SLA, invalid ETA)
- [ ] **AC3**: Each owner row is clickable to drill down and see that owner's services and items
- [ ] **AC4**: Owner names are sorted by action item count descending (busiest first)
- [ ] **AC5**: For non-managers (individual contributors), the section does not appear

## Non-Functional Requirements
- Owner lookup should not significantly increase refresh time (batch lookups if possible)
- Should work with any team size

## Telemetry / Metrics Expected
- None (local desktop app)

## Rollout / Rollback Notes
- Feature is additive, no rollback concerns
- Existing Service Summary and Program Summary remain unchanged
