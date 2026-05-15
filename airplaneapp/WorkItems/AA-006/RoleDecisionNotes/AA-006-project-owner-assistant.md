# AA-006 — Project Owner Assistant Decision Notes

## Scope Decision
AA-006 delivers the reservation system with a calendar view, conflict detection, and FCFS booking. This completes the three core features of the app (Hobbs, maintenance, reservations).

## Why This Scope
- Reservations are the third pillar of the app. Pilots sharing aircraft need to coordinate usage.
- The calendar view is essential UX — without visual context, scheduling is painful.
- Dispatch-to-reservation linking was deferred because AA-004 dispatch works standalone. Linking them is a natural integration work item after both features exist.

## Key Design Decisions
- **Server-side overlap detection:** The most critical integrity requirement. Two pilots booking the same plane at the same time must be impossible, even under race conditions. This requires either a database constraint or a serialized transaction check. The architect should decide the specific mechanism.
- **30-minute snapping:** Per brainstorm. UI time selectors use 30-minute increments. Backend validates that start/end times align to :00 or :30.
- **UTC storage:** Reservations stored in UTC, displayed in the user's local timezone on the frontend. This future-proofs for multi-timezone clubs.
- **Weekly calendar default:** Shows Mon–Sun for one org's fleet. The pilot can navigate forward/backward by week. Daily view is also available for detailed scheduling.
- **Admin cancel power:** Admins can cancel any reservation (e.g., plane going to maintenance). Pilots can only cancel their own.

## Dependency Note
AA-006 depends only on AA-003 (aircraft exist in an org). It does NOT depend on AA-004 (Hobbs) or AA-005 (maintenance). This means AA-006 could be implemented in parallel with AA-004/AA-005 if desired, as long as AA-003 is complete.

## Future Integration
- **Dispatch ↔ Reservation linking:** When a pilot checks out via dispatch (AA-004), optionally link to an active reservation. This should be a lightweight follow-up work item after both AA-004 and AA-006 are implemented.
