# AA-001 — Program Manager Decision Notes

## Design Decisions

### Monorepo with `client/` and `server/`
Chose a simple two-folder monorepo over a Next.js fullstack approach. Rationale: user wants React + Node.js as separate concerns; keeps the API independently testable and future-proofs for mobile clients.

### Vite for React
Selected Vite over Create React App (deprecated) or Webpack manual config. Vite is the current React community standard for fast dev server and builds.

### Auth Service Interface Pattern
Rather than sprinkling bcrypt/JWT calls throughout route handlers, auth logic is encapsulated in an `AuthService` module with three methods. This satisfies the user's explicit request for swappable auth without introducing a DI framework (which would be over-engineering for MVP).

### Minimal API Surface
Only three endpoints for AA-001: register, login, me. This keeps the work item small and independently testable. Organization and role endpoints are deferred to AA-002.

### Test Strategy
API integration tests with Jest + Supertest for the backend. No frontend unit tests in AA-001 — manual verification of the three pages is sufficient for MVP. Frontend testing can be introduced in a later work item if needed.

## Risks Accepted
- SQLite single-writer limitation accepted for MVP; Prisma migration path to Postgres is the planned escape hatch.
- No rate limiting on auth endpoints for MVP; acceptable for local-only deployment.

## No Scope Changes
Design doc stays within User Story scope. No new requirements introduced.
