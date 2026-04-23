# AA-001 Design Document — Project Scaffolding, User Registration & Login

## Summary

Establish the AirplaneApp project foundation: a React frontend, Express.js backend, and SQLite database with Prisma ORM, delivering end-to-end user registration and login. This is the first vertical slice of the application and the prerequisite for all subsequent features.

## Problem Statement

AirplaneApp has no codebase yet. Before any domain features (Hobbs tracking, maintenance, reservations) can be built, the project needs a working full-stack skeleton with authenticated user sessions. Without this foundation, no other work item can proceed.

## Business Case

- **Why now:** This is the first work item — everything else is blocked until scaffolding and auth exist.
- **Impact:** Unblocks five downstream work items (AA-002 through AA-006). Establishes all architectural patterns that the rest of the app will follow.
- **KPIs:** 
  - A new user can register and log in within a single dev workflow (`npm run dev`).
  - All five acceptance criteria pass.
  - Future work items (AA-002+) can be started with zero scaffolding overhead.

## Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| Project Owner | MVP delivered incrementally; auth is swappable |
| Pilots / Techs / Admins | Can create an account and log in |
| Future developers | Clean, conventional project structure to build upon |

## Functional Requirements

1. **Registration:** User submits email, name, and password. Server validates input, rejects duplicate emails, hashes password, stores user, and returns a JWT.
2. **Login:** User submits email and password. Server verifies credentials, returns a JWT on success, 401 on failure.
3. **Route protection:** API endpoints marked as protected reject requests without a valid JWT (401).
4. **Frontend pages:** Login page, registration page, and an authenticated dashboard showing the user's email.
5. **Database migration:** Prisma schema defines a `users` table; `prisma migrate` runs cleanly on a fresh SQLite file.

## Non-Functional Requirements

| Requirement | Detail |
|-------------|--------|
| Security | bcrypt with ≥10 salt rounds; JWT secret from env vars |
| Adaptability | Auth logic behind a service interface; route handlers call the interface, not bcrypt/JWT directly |
| Portability | Prisma ORM on SQLite; switching to Postgres requires only a datasource change |
| Developer experience | Single `npm run dev` starts both client and server; SQLite file gitignored |
| Input validation | Email format validation; password minimum length (8 chars); name required |

## Proposed Approach (High Level)

### Project Structure

```
airplaneapp/
├── client/                  # React app (Vite)
│   ├── src/
│   │   ├── pages/           # Login, Register, Dashboard
│   │   ├── services/        # API client
│   │   ├── context/         # AuthContext (JWT storage)
│   │   └── App.jsx
│   └── package.json
├── server/                  # Express API
│   ├── src/
│   │   ├── routes/          # auth routes
│   │   ├── middleware/       # JWT verification middleware
│   │   ├── services/        # AuthService interface + implementation
│   │   ├── prisma/          # schema.prisma, migrations
│   │   └── index.js
│   └── package.json
├── package.json             # Root scripts (concurrent dev)
└── .env.example             # JWT_SECRET, DATABASE_URL
```

### Auth Service Interface

```
AuthService {
  register(email, password, name) → { user, token }
  login(email, password) → { user, token }
  verifyToken(token) → user | null
}
```

Route handlers depend on this interface. The concrete implementation uses bcrypt + JWT. This can be swapped to OAuth/SSO later without changing routes.

### API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | No | Create account |
| POST | `/api/auth/login` | No | Authenticate |
| GET | `/api/auth/me` | Yes | Return current user |

### Database Schema (Prisma)

```prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  password  String
  name      String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Next.js full-stack | Adds SSR complexity; user wants simple React + API separation for MVP |
| Knex instead of Prisma | Prisma provides type-safe client and migration tooling out of the box; better DX |
| Session-based auth (cookies) | JWT is more portable for future mobile/API clients; aligns with swappable auth goal |
| Fastify instead of Express | Express has larger ecosystem and community; user said "don't care, just MVP" |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| JWT secret committed to repo | Medium | High | `.env` file gitignored; `.env.example` with placeholder; validation on startup that JWT_SECRET is set |
| SQLite concurrency limits under load | Low (MVP) | Low | Prisma's SQLite driver handles single-writer; acceptable for local dev; Postgres migration planned |
| Auth interface over-abstraction | Low | Medium | Keep interface to 3 methods; no framework-level DI — just a module export |

## Open Questions

None — all fundamental questions were resolved during the brainstorm phase.

## Dependencies

| Dependency | Type | Notes |
|-----------|------|-------|
| Node.js ≥ 18 | Runtime | Required for modern ESM and Prisma support |
| npm | Tooling | Package management |
| None (external services) | External | SQLite is file-based; no external DB or auth provider needed |

## Migration / Rollout / Rollback Plan

- **Rollout:** This is the first commit. Run `npm install` → `npx prisma migrate dev` → `npm run dev`.
- **Rollback:** Not applicable — greenfield project. Revert commit if needed.
- **Data migration:** None — empty database created from scratch.

## Observability Plan

- **MVP:** Console logging for server startup, registration, login attempts, and auth failures.
- **No external telemetry** for now (per user decision).
- **Future:** Structured logging, request tracing when moving to cloud.

## Test Strategy Summary

| Layer | Tool | Coverage |
|-------|------|----------|
| API integration tests | Jest + Supertest | Register, login, protected route, duplicate email, invalid credentials |
| Auth service unit tests | Jest | Hash verification, JWT generation/verification, interface contract |
| Frontend | Manual verification | Registration form, login form, dashboard render, error messages |
| Database | Prisma migrate | Schema applies cleanly to fresh SQLite |
