# AirplaneApp — MVP Overview

## Target Audience

Individual aircraft owners, partnerships, and small flight clubs. Eventually a commercial SaaS product, starting with personal/club use.

## Roles

| Role | Permissions |
|------|------------|
| **Pilot** | Logs flights (Hobbs/Tach), makes reservations, views maintenance status |
| **Maintenance Tech** | Marks maintenance complete, uploads records/documents |
| **Admin** | Creates the organization, manages aircraft, invites users, manages maintenance schedules |

## Tech Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Frontend | React | Responsive web |
| Backend | Node.js (Express) | REST API |
| Database | SQLite | Via ORM (Prisma or Knex) for future migration to Postgres |
| Auth | Email/Password | Swappable auth layer for future upgrade |
| Hosting | Local-only | Cloud-ready architecture |

## Organization & Aircraft Model

- An **Admin** creates an organization and invites pilots and techs via email.
- A user can belong to **multiple organizations** (e.g., a pilot in both a partnership and a flying club).
- Each organization manages **1–N aircraft**.
- Each aircraft has a profile: tail number, make/model, engine type, year, and other relevant details.

## Feature 1: Hobbs & Tach Tracking (Highest Priority)

- Pilot enters the **ending Hobbs and Tach values** after each flight.
- **Validation:** a new value cannot be lower than the last recorded value.
- **Delta** is auto-calculated from the last known value.
- Optional flight log entries.
- Running totals per aircraft.

## Feature 2: Maintenance Scheduling

### Pre-Loaded FAA Maintenance Intervals

| Item | Interval Type | Default Interval |
|------|--------------|-----------------|
| Annual Inspection | Calendar | 12 months |
| 100-Hour Inspection | Hobbs | 100 hours |
| Oil Change | Hobbs | 50 hours (editable) |
| Transponder Check | Calendar | 24 months |
| ELT Inspection | Calendar | 12 months |
| Pitot-Static Check | Calendar | 24 months |
| Airworthiness Directives | Varies | Per AD requirements |

- All intervals are **editable per aircraft** (e.g., oil change at 25 hours instead of 50).
- Tracks by **both Hobbs hours and calendar date**.
- **Alerts fire at 10% remaining** of the interval (e.g., 10 hours before a 100-hr inspection, ~36 days before an annual).
- **AD tracking** via periodic import from the FAA AD database.
- Only the **Maintenance Tech** role can mark maintenance as complete.
- Supports **document and photo uploads** for maintenance records (logbook entries, receipts, work orders).

## Feature 3: Reservations

- **Calendar view** with visual conflict detection.
- **30-minute** minimum reservation blocks.
- **First-come-first-served** — no approval workflow needed.
- Pilots can **cancel freely** with no restrictions.
- No reservation caps per pilot.
- **Dispatch flow** ties reservations to Hobbs entries:
  1. Pilot checks out the aircraft → enters starting Hobbs
  2. Pilot flies
  3. Pilot checks in the aircraft → enters ending Hobbs
  4. System records the flight and updates running totals

## Notifications

- **In-app only** for MVP.
- Maintenance approaching alerts based on the 10% remaining threshold.

## Sample / Seed Data

- **Cessna 172** — most common GA trainer/rental
- **Piper Cherokee** — popular partnership aircraft

## Future Considerations (Post-MVP)

- Cloud hosting migration (SQLite → Postgres)
- Enhanced authentication (OAuth, SSO)
- Email/SMS/push notifications
- FAA AD database real-time integration
- Mobile-optimized or native app
- Commercial SaaS multi-tenancy and billing
