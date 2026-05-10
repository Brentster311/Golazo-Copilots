# AA-001 — Architect Decision Notes

## Architecture Decisions

### Monorepo Structure
Approved `client/` + `server/` layout. Prisma schema placed at `server/prisma/schema.prisma` (Prisma convention) rather than nested under `src/`.

### Auth Service as Module Export
The AuthService interface uses a plain module export pattern rather than a class. This is simpler, more testable (easy to mock with Jest), and idiomatic for Node.js. No dependency injection framework needed.

### bcryptjs over bcrypt
Recommended `bcryptjs` (pure JavaScript) instead of `bcrypt` (native C++ addon). The user is on Windows; native builds require Visual Studio build tools which add setup friction. Performance difference is negligible for an MVP with low auth volume.

### Helmet Added
Added `helmet` as a recommended dependency for HTTP security headers. Minimal code impact (`app.use(helmet())`), significant security benefit (X-Frame-Options, CSP, etc.).

### CORS Restriction
CORS must be locked to the Vite dev server origin, not wildcard. This prevents cross-origin abuse even in local development.

### Response DTO Pattern
All user-facing API responses must exclude `password` and `updatedAt`. Rather than using Prisma `select` everywhere, a `toUserResponse(user)` utility function should strip sensitive fields in one place.

## Security Review Outcome
No blocking security issues. Five implementation-level security recommendations provided (generic errors, JWT expiry, email normalization, password exclusion, CORS + Helmet). All documented in Review Comments.

## Capability Registry
- No existing capabilities affected (greenfield).
- Two new capabilities (`user-auth`, `database`) should be registered after implementation.
- capability-impact.md created with full contract documentation.

## No Scope or Design Changes
All findings are implementation guidance. No new User Stories required.
