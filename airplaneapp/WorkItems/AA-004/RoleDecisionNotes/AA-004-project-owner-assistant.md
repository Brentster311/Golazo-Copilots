# AA-004 — Project Owner Assistant Decision Notes

## Scope Decision
AA-004 delivers the core Hobbs/Tach tracking feature through a dispatch (check-out / check-in) flow. This is the highest-priority domain feature per the brainstorm.

## Why This Scope
- The dispatch flow ties together the user's primary workflow: take a plane out, fly it, bring it back, log the time.
- Dispatch is independent of reservations so it can be delivered and tested without AA-006. When reservations land, dispatch will optionally link to a reservation record.
- No editing/deleting past entries to maintain audit integrity — a core requirement for any Hobbs tracking system used for maintenance compliance.

## Key Design Decisions
- **Dispatch as a state machine:** Aircraft has a dispatch status (available / in-use). Check-out transitions to in-use and snapshots the current Hobbs/Tach. Check-in records ending values and transitions back to available. This prevents two pilots from checking out the same plane.
- **Delta auto-calculation:** The user enters only the ending value. The system computes `ending - starting` for the flight time. This matches real-world pilot workflow (read the Hobbs meter, write it down).
- **Decimal precision:** Hobbs meters display 1/10 hour increments (e.g., 1234.5). Storing as decimal with 1 decimal place matches the real instrument.
- **History view on aircraft detail:** Pilots need to see recent flight entries for the aircraft (who flew, when, how long). This is the "optional flight log" from the brainstorm — we show the basic data that's already being captured.

## Dependency Note
AA-004 depends on AA-003, which provides the Aircraft model with initial Hobbs/Tach seed values. The first check-in delta is calculated against the aircraft's initial values.
