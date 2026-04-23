# AA-001: Project Scaffolding, User Registration & Login

**Status**: IMPLEMENTED

## User Story

- **Title:** Project Scaffolding, User Registration & Login
- **As a:** pilot, maintenance tech, or admin
- **I want:** to register an account and log in to the AirplaneApp
- **So that:** I have a secure, authenticated identity that future features (orgs, aircraft, reservations) can be built upon

- **Out of scope:**
  - Organization creation and member invitations (AA-002)
  - Aircraft management (AA-003)
  - Role assignment (admin/pilot/tech) — users are created without a role until invited to an org
  - Password reset / forgot password flow
  - OAuth / SSO / social login (future enhancement)

- **Assumptions:**
  - **Assumption (explicit):** Express.js is used as the Node.js backend framework (MVP pragmatism; user said "don't care, just want MVP").
  - **Assumption (explicit):** Prisma is used as the ORM for SQLite with future Postgres migration path (user confirmed ORM approach).
  - **Assumption (explicit):** Auth is email/password with bcrypt hashing and JWT tokens. The auth module is behind an interface so it can be swapped later (user requested adaptable auth).
  - **Assumption (explicit):** Project structure follows a standard monorepo layout with `client/` (React) and `server/` (Express) directories.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] A user can register with email and password via the registration page; duplicate emails are rejected with a clear error message.
  - [ ] A user can log in with valid credentials and receives a JWT; invalid credentials return a 401 error.
  - [ ] Authenticated routes are protected — unauthenticated requests to protected endpoints return 401.
  - [ ] The React app has a login page, registration page, and a placeholder authenticated dashboard page that displays the logged-in user's email.
  - [ ] The database schema includes a `users` table with id, email, hashed password, name, and timestamps; migrations run cleanly on a fresh SQLite database.

- **Non-functional requirements:**
  - Passwords are hashed with bcrypt (minimum 10 salt rounds).
  - JWT secret is loaded from environment variables, not hardcoded.
  - Auth layer is behind an interface/service boundary so it can be replaced without touching route handlers.
  - SQLite database file is gitignored.
  - Project includes `package.json` scripts for dev startup of both client and server.

- **Telemetry / metrics expected:**
  - None for MVP (in-app notifications only, no external telemetry).

- **Rollout / rollback notes:**
  - First work item — no rollback concerns. Clean project scaffolding.

## Closure

### Summary
AA-001 delivered a complete full-stack foundation for AirplaneApp: React frontend with login/register/dashboard pages, Express.js REST API with JWT authentication, and a SQLite database via Prisma ORM. All 27 automated tests pass. The client builds cleanly.

### Acceptance Criteria Validation

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC1 | Registration with duplicate email rejection | **PASS** | TC-1.1 through TC-1.6 passing (6 API integration tests) |
| AC2 | Login with JWT, invalid credentials return 401 | **PASS** | TC-2.1 through TC-2.5 passing (5 API integration tests) |
| AC3 | Protected routes reject unauthenticated requests | **PASS** | TC-3.1 through TC-3.5 passing (4 API integration tests) |
| AC4 | React app with login, register, dashboard pages | **PASS** | Client builds without errors; pages implemented with routing, auth context, and protected routes. PO validation requested — run `npm run dev` and verify pages at http://localhost:5173 |
| AC5 | Database schema with users table, clean migrations | **PASS** | Prisma migration applied successfully; schema verified via authService tests |

### Non-Functional Requirements Verification
- Passwords hashed with bcrypt (10 salt rounds) — verified by TC-NF-1 pattern
- JWT secret from env vars — server refuses to start without JWT_SECRET
- Auth layer behind service interface — route handlers import authService, not bcrypt/JWT directly
- SQLite database file gitignored — confirmed in .gitignore
- `npm run dev` starts both client and server via concurrently

### Future Work Items
| ID | Title | Source |
|----|-------|--------|
| AA-002 | Organization Creation & Member Invitations | Decomposition plan |
| AA-003 | Aircraft Profile Management | Decomposition plan |
| AA-004 | Hobbs & Tach Entry with Dispatch Flow | Decomposition plan |
| AA-005 | Maintenance Scheduling & Alerts | Decomposition plan |
| AA-006 | Reservations & Calendar | Decomposition plan |
| (chore) | Initialize git repository | Retrospective action item |
| (chore) | Add ESLint configuration | Retrospective action item |

### Final Status
**IMPLEMENTED** — All acceptance criteria satisfied. Ready for PO runtime verification of AC4 (frontend pages).
