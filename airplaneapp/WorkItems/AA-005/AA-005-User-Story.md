# AA-005: Maintenance Scheduling & Alerts

**Status**: BACKLOG

## User Story

- **Title:** Maintenance Scheduling & Alerts
- **As a:** maintenance tech or admin
- **I want:** to see upcoming maintenance items for each aircraft with pre-loaded FAA intervals, editable schedules, and in-app alerts when maintenance is approaching
- **So that:** aircraft stay in compliance and nothing is missed

- **Out of scope:**
  - FAA AD database import (deferred to a future enhancement; ADs are manually entered in this story)
  - Email/SMS/push notifications (in-app only for MVP)
  - Maintenance record document/photo uploads (deferred to AA-005b or future enhancement)
  - Generating FAA-formatted maintenance reports

- **Assumptions:**
  - **Assumption (explicit):** Interface type: web. Platform/persistence: same as AA-001.
  - **Assumption (explicit):** Each aircraft is automatically provisioned with the standard FAA maintenance intervals when created (annual, 100-hr, oil change, transponder, ELT, pitot-static). Admins can edit default intervals per aircraft.
  - **Assumption (explicit):** Alerts fire at 10% remaining of the interval (per brainstorm): 10 hours before a 100-hr inspection, ~36 days before an annual, etc.
  - **Assumption (explicit):** Only the Maintenance Tech role can mark a maintenance item as completed. Completing an item resets its countdown from the completion date/Hobbs value.
  - **Assumption (explicit):** In-app alerts appear as notifications on the dashboard for all org members when maintenance is approaching for any aircraft in their org.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] When an aircraft is created (or migrated), it is automatically provisioned with default FAA maintenance schedule items (annual, 100-hr, oil change, transponder, ELT, pitot-static) with their default intervals.
  - [ ] An Admin can edit the interval values for any maintenance item on any aircraft (e.g., change oil change from 50 to 25 hours); an Admin can add custom maintenance items.
  - [ ] A Maintenance Tech can mark a maintenance item as completed, recording the completion date and current Hobbs; the item's next-due calculation resets based on the new baseline.
  - [ ] The aircraft detail page shows a maintenance status panel listing all maintenance items with their status (OK, approaching, overdue) and remaining hours/days.
  - [ ] In-app alerts are displayed (dashboard notification area) when any maintenance item reaches the 10% remaining threshold (by Hobbs hours or calendar days).

- **Non-functional requirements:**
  - Maintenance status is recalculated on each aircraft view (not cached) to ensure accuracy against latest Hobbs values.
  - Maintenance completion records are append-only (audit trail).
  - Role enforcement: only Tech can complete; only Admin can edit intervals.
  - Alert threshold is configurable per maintenance item (default 10%).

- **Telemetry / metrics expected:**
  - None for MVP.

- **Rollout / rollback notes:**
  - Depends on AA-003 (aircraft) and AA-004 (Hobbs tracking, for hours-based items). New MaintenanceItem and MaintenanceLog tables. No changes to existing models beyond adding relations.
