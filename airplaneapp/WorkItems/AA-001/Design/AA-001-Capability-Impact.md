# AA-001 — Capability Impact Analysis

## Impact Summary

**No existing capabilities affected.** This is the first work item — the project has no production code or established capabilities yet. The capabilities.yaml contains only a placeholder entry.

## New Capabilities Introduced by AA-001

After implementation, the following capabilities should be registered in `capabilities.yaml`:

### 1. `user-auth`
- **Description:** User registration, login, and JWT-based authentication
- **Key files:** `server/src/services/authService.js`, `server/src/routes/auth.js`, `server/src/middleware/auth.js`
- **Contracts:**
  - `AuthService.register(email, password, name) → { user, token }`
  - `AuthService.login(email, password) → { user, token }`
  - `AuthService.verifyToken(token) → user | null`
  - `POST /api/auth/register → 201 { user, token } | 400 | 409`
  - `POST /api/auth/login → 200 { user, token } | 400 | 401`
  - `GET /api/auth/me → 200 { user } | 401`
- **Depends on:** (none)

### 2. `database`
- **Description:** Prisma ORM with SQLite datasource and User model
- **Key files:** `server/prisma/schema.prisma`
- **Contracts:** `User { id, email, password, name, createdAt, updatedAt }`
- **Depends on:** (none)

## Downstream Impact for Future Work Items

- **AA-002 (Orgs)** will depend on `user-auth` and `database`
- **AA-003–AA-006** will transitively depend on `user-auth` via `database`

## Action Required

Developer should update `capabilities.yaml` after implementation to register `user-auth` and `database` capabilities.
