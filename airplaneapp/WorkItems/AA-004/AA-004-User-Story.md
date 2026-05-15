# AA-004: Hobbs & Tach Entry with Dispatch Flow

**Status**: BACKLOG

## User Story

- **Title:** Hobbs & Tach Entry with Dispatch Flow
- **As a:** pilot
- **I want:** to record ending Hobbs and Tach values after each flight through a dispatch check-out/check-in flow
- **So that:** the aircraft's running totals are accurately tracked and flight time deltas are automatically calculated

- **Out of scope:**
  - Maintenance alert triggers based on Hobbs hours — AA-005
  - Reservation creation (dispatch links to an existing reservation) — AA-006
  - GPS/avionics integration for automatic Hobbs capture
  - Detailed flight log entries (optional log is deferred to a future enhancement)
  - Editing or deleting past Hobbs entries (audit integrity)

- **Assumptions:**
  - **Assumption (explicit):** Interface type: web. Platform/persistence: same as AA-001.
  - **Assumption (explicit):** The dispatch flow is independent of reservations for now. A pilot can dispatch (check-out → fly → check-in) without a reservation. When AA-006 is implemented, the dispatch flow will optionally link to a reservation.
  - **Assumption (explicit):** Only the ending Hobbs and Tach values are entered (per brainstorm). The delta is calculated as `new_value - previous_value` from the aircraft's last recorded entry.
  - **Assumption (explicit):** Any org member with pilot or admin role can log Hobbs/Tach for aircraft in their org.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] A pilot can check out an aircraft (dispatch), which records the current Hobbs/Tach as the starting snapshot and marks the aircraft as "in use."
  - [ ] A pilot can check in an aircraft by entering the ending Hobbs and Tach values; the system validates that new values are not lower than the starting values and calculates the flight delta.
  - [ ] The aircraft's current Hobbs and Tach running totals are updated after check-in; the aircraft detail page displays the current totals and a history of recent entries.
  - [ ] An aircraft that is currently checked out shows an "in use" indicator on the aircraft list, preventing another pilot from checking it out simultaneously.

- **Non-functional requirements:**
  - Hobbs/Tach values are stored as decimal numbers with 1 decimal place precision (e.g., 1234.5).
  - Validation is enforced server-side: ending value >= starting value, and starting value >= last recorded value.
  - Each Hobbs entry records: aircraft ID, pilot user ID, Hobbs start, Hobbs end, Tach start, Tach end, timestamp.
  - API endpoints require authentication and org membership.

- **Telemetry / metrics expected:**
  - None for MVP.

- **Rollout / rollback notes:**
  - Depends on AA-003 (aircraft profiles with initial Hobbs/Tach values). New HobbsEntry table + dispatch state on aircraft. No changes to existing models.
