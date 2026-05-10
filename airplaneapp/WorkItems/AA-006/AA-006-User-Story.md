# AA-006: Reservations & Calendar

**Status**: BACKLOG

## User Story

- **Title:** Reservations & Calendar
- **As a:** pilot
- **I want:** to reserve an aircraft on a calendar, see existing reservations, and have conflicts automatically prevented
- **So that:** shared aircraft usage is coordinated and I know when a plane is available

- **Out of scope:**
  - Reservation approval workflows (FCFS per brainstorm)
  - Reservation caps per pilot (none per brainstorm)
  - Recurring/repeating reservations
  - Linking dispatch check-out to a reservation (integration deferred; dispatch works standalone via AA-004)
  - Email/SMS reminders for upcoming reservations

- **Assumptions:**
  - **Assumption (explicit):** Interface type: web. Platform/persistence: same as AA-001.
  - **Assumption (explicit):** Calendar is a weekly/daily view showing all aircraft in the org. Each reservation shows the pilot's name, aircraft, and time block.
  - **Assumption (explicit):** Minimum reservation block is 30 minutes (per brainstorm). Reservations snap to 30-minute boundaries.
  - **Assumption (explicit):** Any org member with pilot or admin role can create and cancel their own reservations. Admins can cancel any reservation.
  - **Assumption (explicit):** FCFS — no approval needed. If a time slot is open, a pilot can book it immediately.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] A pilot can create a reservation by selecting an aircraft, date, start time, and end time (minimum 30-minute block, snapping to 30-minute increments); the reservation is confirmed immediately (FCFS).
  - [ ] The system rejects a reservation that overlaps with an existing reservation for the same aircraft and returns a clear conflict error message.
  - [ ] A calendar view displays all reservations for the selected org's aircraft for the current week, with each reservation showing the pilot name and time block.
  - [ ] A pilot can cancel their own reservation freely; an Admin can cancel any reservation in their org.
  - [ ] The database schema includes a Reservation table with aircraft ID, pilot user ID, start time, end time, and status; a unique constraint prevents overlapping bookings for the same aircraft.

- **Non-functional requirements:**
  - Overlap detection is enforced server-side with a database-level constraint or transaction-safe check (not just UI validation).
  - Reservation times are stored in UTC.
  - API endpoints require authentication and org membership.
  - Calendar view loads within 2 seconds for a week of data with up to 50 reservations.

- **Telemetry / metrics expected:**
  - None for MVP.

- **Rollout / rollback notes:**
  - Depends on AA-003 (aircraft). Independent of AA-004 (Hobbs) and AA-005 (maintenance). New Reservation table + endpoints + calendar UI. No changes to existing models.
