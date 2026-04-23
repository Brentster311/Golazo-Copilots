# AA-001 — Design Review Comments

## Overall Assessment

The design is **clear, feasible, and well-scoped**. No blocking issues found. Minor recommendations below.

---

## Review Items

### R1: Login error message should not reveal whether email exists
- **Severity:** Medium (Security)
- **Location:** Design Doc → API Endpoints → POST `/api/auth/login`
- **Issue:** Design says "401 on failure" but doesn't specify the error message. If the API returns "Email not found" vs "Wrong password," it enables user enumeration attacks.
- **Recommendation:** Return a generic message like `"Invalid email or password"` for all login failures. The domain expert notes already flagged this — ensure it's implemented.
- **Action:** Developer should implement generic error messages. No design change needed.

### R2: JWT expiration not specified
- **Severity:** Medium (Security)
- **Location:** Design Doc → Auth Service Interface
- **Issue:** The design mentions JWT but does not specify a token expiration time. Tokens that never expire are a security risk.
- **Recommendation:** Set JWT expiration to 24 hours for MVP. Document this in the `.env.example` as a configurable value (`JWT_EXPIRES_IN=24h`).
- **Action:** Developer should add expiration. No design change needed — this is an implementation detail.

### R3: Email normalization
- **Severity:** Low (Data integrity)
- **Location:** Design Doc → Functional Requirements → Registration
- **Issue:** `User@Example.com` and `user@example.com` could create duplicate accounts if email is not normalized.
- **Recommendation:** Lowercase and trim email before storage and comparison.
- **Action:** Developer should implement. No design change needed.

### R4: Password field excluded from API responses
- **Severity:** Medium (Security)
- **Location:** Design Doc → API Endpoints → GET `/api/auth/me`
- **Issue:** The design doesn't explicitly state that the hashed password should never be returned in API responses.
- **Recommendation:** Ensure all user-facing API responses exclude the `password` field. Use Prisma `select` or a response DTO.
- **Action:** Developer should implement. No design change needed.

### R5: Request body size limit
- **Severity:** Low (Reliability)
- **Location:** Design Doc → Proposed Approach
- **Issue:** No mention of request body size limits. Large payloads could cause issues.
- **Recommendation:** Use Express's built-in JSON body parser with a reasonable limit (e.g., `express.json({ limit: '1mb' })`).
- **Action:** Developer should implement. No design change needed.

---

## Domain Expert Guidance

Per the domain expert review (AA-001-domain-expert.md): no specialized domain expertise required for this work item. Proactive security guidance was provided and is incorporated into review items R1–R4 above.

---

## Summary

| ID | Severity | Category | Blocking? |
|----|----------|----------|-----------|
| R1 | Medium | Security | No — implementation guidance |
| R2 | Medium | Security | No — implementation guidance |
| R3 | Low | Data integrity | No — implementation guidance |
| R4 | Medium | Security | No — implementation guidance |
| R5 | Low | Reliability | No — implementation guidance |

**Verdict:** Design is approved. All items are implementation-level guidance for the Developer role — no design doc revisions required.

---

## Architect Notes

### Architectural Alignment
The proposed structure (React SPA ↔ Express REST API ↔ Prisma/SQLite) is appropriate for an MVP. The separation of client and server enables independent testing and future deployment flexibility.

### API Contracts — Approved
The three-endpoint surface is clean and conventional:
- `POST /api/auth/register` — 201/400/409
- `POST /api/auth/login` — 200/400/401
- `GET /api/auth/me` — 200/401

**Contract detail:** All responses returning a user object must use a consistent shape: `{ id: number, email: string, name: string, createdAt: string }`. The `password` and `updatedAt` fields must be excluded from all API responses.

### Auth Service Interface — Approved with Notes
The three-method interface (`register`, `login`, `verifyToken`) is the right level of abstraction. Implementation notes:
- The interface should be a plain JS module export (not a class with `new`). This keeps it simple and mockable for tests.
- `verifyToken` should throw or return null on invalid tokens — do not return a partial object.

### Security Review
- **Approved.** bcrypt + JWT with env-based secrets is sound for MVP.
- **CORS:** Developer must configure CORS to allow only the Vite dev server origin in development (`http://localhost:5173`). Do not use `cors({ origin: '*' })`.
- **Helmet:** Add `helmet` middleware for HTTP security headers (small dependency, high value).
- **Input sanitization:** Prisma parameterizes queries by default, so SQL injection is mitigated. No additional sanitization layer needed for MVP.

### Scalability & Portability
- SQLite → Postgres migration path via Prisma datasource swap is validated. No schema patterns that would break on Postgres (autoincrement is compatible).
- `Int` for user ID is fine for MVP. Future: consider UUID if multi-database merge scenarios arise (not needed now).

### Dependency Choices — Approved
| Package | Risk | Notes |
|---------|------|-------|
| express | Low | Mature, widely used |
| prisma | Low | Well-maintained, SQLite support solid |
| bcryptjs | Low | Pure JS bcrypt; no native compilation issues on Windows |
| jsonwebtoken | Low | Industry standard |
| cors | Low | Express middleware standard |
| helmet | Low | Recommended addition for security headers |
| concurrently | Low | Dev-only, for running client+server |

**Note:** Recommend `bcryptjs` (pure JS) over `bcrypt` (native) to avoid Windows build tool issues.

### Folder Structure — Approved
The `client/` + `server/` monorepo is appropriate. One recommendation: place Prisma schema at `server/prisma/schema.prisma` (Prisma default) rather than `server/src/prisma/` to follow Prisma conventions.

### Naming Clarity
- Routes file: `server/src/routes/auth.js` ✓
- Service: `server/src/services/authService.js` ✓
- Middleware: `server/src/middleware/auth.js` ✓
- Pages: `Login.jsx`, `Register.jsx`, `Dashboard.jsx` ✓

### No Architectural Changes Required
All findings are implementation-level. No new User Stories needed.
