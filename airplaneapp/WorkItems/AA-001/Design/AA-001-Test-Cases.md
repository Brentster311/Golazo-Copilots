# AA-001 — Test Cases

## Test Strategy

- **Backend:** Jest + Supertest for API integration tests
- **Auth Service:** Jest unit tests for the service layer
- **Database:** Prisma migration validation
- **Frontend:** Manual verification (documented checklist)

All tests should be created before production code (TDD-first).

---

## AC1: Registration — Happy Path & Duplicate Rejection

### TC-1.1: Successful registration
- **Input:** POST `/api/auth/register` with `{ email: "pilot@test.com", password: "securepass1", name: "Test Pilot" }`
- **Expected:** 201 status, response body contains `{ user: { id, email, name }, token: "<jwt>" }`, password is NOT in response
- **Failure message:** "Registration should return 201 with user object and JWT token"

### TC-1.2: Duplicate email rejected
- **Precondition:** User with `pilot@test.com` already exists
- **Input:** POST `/api/auth/register` with `{ email: "pilot@test.com", password: "otherpass1", name: "Dupe Pilot" }`
- **Expected:** 409 status, response body contains an error message indicating email is already registered
- **Failure message:** "Duplicate email registration should return 409 with descriptive error"

### TC-1.3: Missing required fields
- **Input:** POST `/api/auth/register` with `{ email: "pilot@test.com" }` (no password, no name)
- **Expected:** 400 status, response body lists missing fields
- **Failure message:** "Registration with missing fields should return 400 with validation errors"

### TC-1.4: Invalid email format
- **Input:** POST `/api/auth/register` with `{ email: "not-an-email", password: "securepass1", name: "Bad Email" }`
- **Expected:** 400 status, response body indicates invalid email format
- **Failure message:** "Registration with invalid email should return 400"

### TC-1.5: Password too short
- **Input:** POST `/api/auth/register` with `{ email: "short@test.com", password: "abc", name: "Short Pass" }`
- **Expected:** 400 status, response body indicates password must be at least 8 characters
- **Failure message:** "Registration with short password should return 400"

### TC-1.6: Email normalization
- **Input:** Register with `{ email: "Pilot@Test.COM", ... }` then try to register with `{ email: "pilot@test.com", ... }`
- **Expected:** Second registration returns 409 (duplicate)
- **Failure message:** "Email should be normalized to lowercase; case-variant duplicates must be rejected"

---

## AC2: Login — Valid & Invalid Credentials

### TC-2.1: Successful login
- **Precondition:** User `pilot@test.com` registered with password `securepass1`
- **Input:** POST `/api/auth/login` with `{ email: "pilot@test.com", password: "securepass1" }`
- **Expected:** 200 status, response body contains `{ user: { id, email, name }, token: "<jwt>" }`, password NOT in response
- **Failure message:** "Login with valid credentials should return 200 with user and JWT"

### TC-2.2: Wrong password
- **Precondition:** User `pilot@test.com` exists
- **Input:** POST `/api/auth/login` with `{ email: "pilot@test.com", password: "wrongpassword" }`
- **Expected:** 401 status, generic error message `"Invalid email or password"`
- **Failure message:** "Login with wrong password should return 401 with generic error (no user enumeration)"

### TC-2.3: Non-existent email
- **Input:** POST `/api/auth/login` with `{ email: "nobody@test.com", password: "anything" }`
- **Expected:** 401 status, generic error message `"Invalid email or password"` (same as wrong password)
- **Failure message:** "Login with non-existent email should return 401 with same generic error as wrong password"

### TC-2.4: Missing fields
- **Input:** POST `/api/auth/login` with `{ email: "pilot@test.com" }` (no password)
- **Expected:** 400 status
- **Failure message:** "Login with missing password should return 400"

### TC-2.5: Email case insensitivity
- **Precondition:** Registered with `pilot@test.com`
- **Input:** POST `/api/auth/login` with `{ email: "PILOT@TEST.COM", password: "securepass1" }`
- **Expected:** 200 status, successful login
- **Failure message:** "Login should be case-insensitive for email"

---

## AC3: Protected Routes — Auth Middleware

### TC-3.1: Authenticated request succeeds
- **Precondition:** Valid JWT obtained from login
- **Input:** GET `/api/auth/me` with `Authorization: Bearer <valid-jwt>`
- **Expected:** 200 status, response contains user object (id, email, name), no password field
- **Failure message:** "Authenticated request to /me should return 200 with user data"

### TC-3.2: Missing token rejected
- **Input:** GET `/api/auth/me` with no Authorization header
- **Expected:** 401 status
- **Failure message:** "Request without token should return 401"

### TC-3.3: Invalid token rejected
- **Input:** GET `/api/auth/me` with `Authorization: Bearer invalid.token.here`
- **Expected:** 401 status
- **Failure message:** "Request with invalid JWT should return 401"

### TC-3.4: Expired token rejected
- **Precondition:** JWT issued with very short expiration (or mocked as expired)
- **Input:** GET `/api/auth/me` with expired JWT
- **Expected:** 401 status
- **Failure message:** "Request with expired JWT should return 401"

### TC-3.5: Password not leaked in /me response
- **Input:** GET `/api/auth/me` with valid JWT
- **Expected:** Response body does NOT contain `password` field
- **Failure message:** "User response must never include the password hash"

---

## AC4: Frontend Pages (Manual Verification Checklist)

### TC-4.1: Registration page renders
- **Steps:** Navigate to `/register`
- **Expected:** Page displays email, name, and password fields with a submit button
- **Pass criteria:** All form fields visible, page renders without errors

### TC-4.2: Registration submits and redirects
- **Steps:** Fill in valid registration data, submit
- **Expected:** User is redirected to dashboard; dashboard displays user's email
- **Pass criteria:** Redirect occurs, email visible on dashboard

### TC-4.3: Registration shows error on duplicate email
- **Steps:** Register, then try same email again
- **Expected:** Error message displayed on registration form
- **Pass criteria:** Error is visible and descriptive

### TC-4.4: Login page renders
- **Steps:** Navigate to `/login`
- **Expected:** Page displays email and password fields with a submit button
- **Pass criteria:** All form fields visible, page renders without errors

### TC-4.5: Login with valid credentials redirects to dashboard
- **Steps:** Log in with registered user
- **Expected:** Redirected to dashboard, email displayed
- **Pass criteria:** Dashboard loads with user email

### TC-4.6: Login shows error on invalid credentials
- **Steps:** Enter wrong password
- **Expected:** Generic error message displayed
- **Pass criteria:** Error visible, does not reveal whether email exists

### TC-4.7: Dashboard is inaccessible without auth
- **Steps:** Navigate directly to dashboard URL without logging in
- **Expected:** Redirected to login page
- **Pass criteria:** Dashboard content not visible

---

## AC5: Database Schema & Migrations

### TC-5.1: Fresh migration succeeds
- **Steps:** Delete SQLite file (if exists), run `npx prisma migrate dev`
- **Expected:** Migration creates `users` table, command exits with 0
- **Failure message:** "Prisma migration should apply cleanly to a fresh SQLite database"

### TC-5.2: Users table has correct columns
- **Steps:** After migration, inspect schema
- **Expected:** Table `User` has columns: `id` (Int, PK, autoincrement), `email` (String, unique), `password` (String), `name` (String), `createdAt` (DateTime), `updatedAt` (DateTime)
- **Failure message:** "Users table schema does not match design specification"

### TC-5.3: Email uniqueness constraint enforced at DB level
- **Steps:** Attempt to insert two users with same email directly via Prisma
- **Expected:** Second insert throws a unique constraint violation
- **Failure message:** "Database should enforce email uniqueness at the schema level"

---

## Non-Functional Tests

### TC-NF-1: Password stored as bcrypt hash
- **Steps:** Register a user, read the user record directly from database
- **Expected:** `password` field starts with `$2b$` (bcrypt prefix) and is 60 characters long
- **Failure message:** "Password must be stored as a bcrypt hash, not plaintext"

### TC-NF-2: JWT secret from environment
- **Steps:** Unset `JWT_SECRET` env var, start server
- **Expected:** Server fails to start or logs a clear error about missing JWT_SECRET
- **Failure message:** "Server should refuse to start without JWT_SECRET configured"

### TC-NF-3: Auth service is decoupled
- **Steps:** Verify route handlers import from `services/authService` interface, not from `bcrypt` or `jsonwebtoken` directly
- **Expected:** Route files have zero direct imports of bcrypt or jsonwebtoken
- **Failure message:** "Auth implementation details should be encapsulated in the service layer"

### TC-NF-4: SQLite file is gitignored
- **Steps:** Check `.gitignore` contains `*.db` or the specific SQLite database path
- **Expected:** Database file is listed in `.gitignore`
- **Failure message:** "SQLite database file must be gitignored"

### TC-NF-5: Dev startup script works
- **Steps:** Run `npm run dev` from project root
- **Expected:** Both client and server start; client is accessible in browser; API responds to requests
- **Failure message:** "npm run dev should start both client and server concurrently"
