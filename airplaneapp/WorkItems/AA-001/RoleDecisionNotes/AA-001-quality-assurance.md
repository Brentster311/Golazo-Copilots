# AA-001 — Quality Assurance Decision Notes

## Design Review Summary

The design doc is well-structured and implementable. Five non-blocking review items were raised (R1–R5), all at the implementation guidance level. No design doc revisions required.

Key security recommendations for the developer:
- Generic login error messages (prevent user enumeration)
- JWT expiration (24h)
- Email normalization (lowercase + trim)
- Password field exclusion from all API responses
- Request body size limits

## Test Coverage Summary

| Acceptance Criterion | Test Cases | Coverage |
|---------------------|------------|----------|
| AC1: Registration | TC-1.1 through TC-1.6 | Happy path, duplicate, missing fields, invalid email, short password, email normalization |
| AC2: Login | TC-2.1 through TC-2.5 | Happy path, wrong password, non-existent email, missing fields, case insensitivity |
| AC3: Protected routes | TC-3.1 through TC-3.5 | Valid token, missing token, invalid token, expired token, password not leaked |
| AC4: Frontend pages | TC-4.1 through TC-4.7 | All three pages render, form submissions, error states, auth redirect |
| AC5: Database | TC-5.1 through TC-5.3 | Fresh migration, column validation, uniqueness constraint |
| Non-functional | TC-NF-1 through TC-NF-5 | bcrypt storage, env var config, service decoupling, gitignore, dev scripts |

**Total: 26 test cases** (19 automated API/unit tests + 7 manual frontend checks)

## Test Approach Decision

- Backend tests (TC-1.x through TC-3.x, TC-5.x, TC-NF-x) should be automated with Jest + Supertest as specified in the design doc.
- Frontend tests (TC-4.x) are manual verification for MVP. No frontend test framework investment for AA-001.
- TC-NF-3 (auth service decoupling) is a code review check, not a runtime test.

## No Scope Changes

All test cases map to existing acceptance criteria and non-functional requirements. No new behavior or scope was introduced.
