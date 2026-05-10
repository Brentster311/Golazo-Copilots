# AA-001 — Project Owner Assistant Decision Notes

## Scope Decision

AA-001 is scoped as the **foundation work item** — project scaffolding plus user registration and login. This is the minimum viable vertical slice that delivers a working, deployable system end-to-end (React ↔ API ↔ Database) while providing a user-observable outcome (register and log in).

## Why This Scope

- Every subsequent feature (orgs, aircraft, Hobbs, maintenance, reservations) depends on authenticated users.
- Scaffolding alone is not user-observable — pairing it with auth makes AA-001 independently demonstrable.
- Including org creation would exceed a single user-observable outcome and push to 6+ acceptance criteria.

## Decomposition Plan

| Work Item | Title | Depends On |
|-----------|-------|-----------|
| AA-001 | Project Scaffolding, User Registration & Login | — |
| AA-002 | Organization Creation & Member Invitations | AA-001 |
| AA-003 | Aircraft Profile Management | AA-002 |
| AA-004 | Hobbs & Tach Entry with Dispatch Flow | AA-003 |
| AA-005 | Maintenance Scheduling & Alerts | AA-003, AA-004 |
| AA-006 | Reservations & Calendar | AA-003 |

## Key Assumptions Rationale

- **Express.js:** User said "don't care, just want MVP" for backend framework. Express is the most common Node.js choice, well-documented, lowest friction.
- **Prisma ORM:** User confirmed ORM for SQLite → Postgres migration. Prisma has first-class SQLite support and type-safe queries.
- **Monorepo layout:** `client/` + `server/` in one repo keeps MVP simple. No need for separate repos at this stage.
- **Auth adaptability:** User explicitly requested the auth code be adaptable. Wrapping auth behind a service interface satisfies this without over-engineering.

## Questions Resolved During Brainstorm

All fundamental questions (interface type: web, platform: local, persistence: SQLite, security model: email/password with JWT) were answered during the brainstorm phase. No blocking questions remain for AA-001.
