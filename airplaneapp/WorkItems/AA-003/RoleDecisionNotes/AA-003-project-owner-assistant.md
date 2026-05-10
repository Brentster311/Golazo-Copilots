# AA-003 — Project Owner Assistant Decision Notes

## Scope Decision
AA-003 delivers the aircraft profile CRUD within an org context. This is the prerequisite for Hobbs tracking (AA-004), maintenance (AA-005), and reservations (AA-006) — all of which operate on an aircraft.

## Why This Scope
- An aircraft profile is a standalone, demonstrable feature: admin adds a plane, everyone can see it.
- Initial Hobbs/Tach values are captured at aircraft creation to seed the tracking system. This avoids a chicken-and-egg problem where AA-004 has no starting value.
- Tail number immutability post-creation prevents data integrity issues with Hobbs logs and maintenance records that reference the aircraft.

## Key Design Decisions
- **Tail number unique within org, not globally:** Two different orgs could theoretically have the same tail number (e.g., during a sale/transfer). Uniqueness is scoped to the org.
- **Seed data included:** Cessna 172 (N12345) and Piper Cherokee (N67890) as dev fixtures, per the brainstorm.
- **No deletion:** Aircraft deletion is risky once Hobbs entries and maintenance records exist. Deferred to a future soft-delete/archive work item.
