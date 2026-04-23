# AA-001 — Domain Expert Decision Notes

## Domain Expertise Analysis

### Work Item Summary
AA-001 is project scaffolding with user registration and login — a standard full-stack CRUD setup using React, Express, Prisma, SQLite, bcrypt, and JWT.

### Domain Expert Evaluation

**No specialized domain expertise required.** Justification:

1. **No distributed systems or cloud-native concerns** — local-only SQLite deployment; no scaling, partitioning, or replication considerations.
2. **No AI/ML components** — straightforward CRUD operations.
3. **No Azure platform dependencies** — local development only for MVP.
4. **No industry-specific regulatory requirements** — user auth is standard; aviation-specific domain logic (FAA maintenance intervals, ADs, Hobbs tracking) starts in AA-003+.
5. **Security pattern is well-established** — bcrypt + JWT is a mature, widely-documented approach. The design doc already specifies minimum salt rounds, env-based secrets, and input validation. No novel security challenge here.
6. **API design is minimal** — three endpoints (register, login, me) following REST conventions. No complex contract design needed.

### Security Guidance (Proactive, Non-Blocking)

While a dedicated Security Expert consultation is not warranted for AA-001, the following standard security practices should be verified during implementation:

- Password minimum length (8 chars) enforced server-side, not just client-side
- Email normalized to lowercase before storage and comparison
- JWT expiration set (e.g., 24h) — don't issue tokens that never expire
- Error messages for login failures should not distinguish between "email not found" and "wrong password" (prevents user enumeration)
- CORS configured to restrict origins in production

These are documented here as guidance for the Architect and Developer roles — no design changes needed.

### Conclusion

Proceed to Quality Assurance without domain expert consultation. Aviation domain expertise will be critical starting at AA-003 (Aircraft Profile) and especially AA-005 (FAA Maintenance Scheduling & AD Tracking).
