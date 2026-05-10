# AA-001 — Developer Decision Notes

## Implementation Summary

All five acceptance criteria are implemented and verified.

### What Was Built

**Server (`server/`)**
- Express.js app with helmet, CORS (locked to localhost:5173), JSON body parsing (1mb limit)
- Prisma ORM with SQLite, User model with id/email/password/name/timestamps
- `AuthService` — 3-method module (register, login, verifyToken) encapsulating bcrypt + JWT
- Auth middleware for protected routes
- 3 API endpoints: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me
- Health check at GET /api/health

**Client (`client/`)**
- React 18 + Vite + React Router
- AuthContext for JWT storage (localStorage) and user state
- 3 pages: Login, Register, Dashboard
- Protected route (Dashboard) redirects to /login when unauthenticated
- Vite proxy forwards /api to server on port 3001

### Security Implementation (per Review Comments R1–R5)
- **R1:** Login returns generic "Invalid email or password" for both wrong password and non-existent email
- **R2:** JWT expires per JWT_EXPIRES_IN env var (defaults to 24h)
- **R3:** Email normalized to lowercase and trimmed before storage and comparison
- **R4:** `toUserResponse()` utility strips password from all API responses
- **R5:** Express body parser limited to 1mb

### Architect Recommendations Implemented
- `bcryptjs` (pure JS) used instead of `bcrypt` to avoid Windows native build issues
- `helmet` added for HTTP security headers
- CORS locked to `http://localhost:5173` (Vite dev server)
- Prisma schema at `server/prisma/schema.prisma` (Prisma convention)
- Auth service is a plain module export, not a class

### Dependency Justification
All dependencies match the design doc and architect review. No additional dependencies beyond:
- `helmet` — recommended by architect for HTTP security headers (approved)

### Test Results
- **27 tests passing** across 2 test suites
  - `authService.test.js`: 12 unit tests (register, login, verifyToken)
  - `auth.api.test.js`: 15 API integration tests (all TC-1.x through TC-3.x)
- Client builds successfully with `vite build`

### Dev Startup
```
npm run dev          # Starts both client (port 5173) and server (port 3001)
npm test             # Runs server tests
```

### Files Created

**Server:**
- `server/package.json`
- `server/.env` / `server/.env.example`
- `server/jest.config.js`
- `server/prisma/schema.prisma`
- `server/src/index.js` — entry point with JWT_SECRET validation
- `server/src/app.js` — Express app config
- `server/src/services/authService.js` — auth business logic
- `server/src/middleware/auth.js` — JWT verification middleware
- `server/src/routes/auth.js` — auth API routes

**Client:**
- `client/package.json`
- `client/vite.config.js`
- `client/index.html`
- `client/src/main.jsx`
- `client/src/App.jsx`
- `client/src/index.css`
- `client/src/context/AuthContext.jsx`
- `client/src/services/api.js`
- `client/src/pages/Login.jsx`
- `client/src/pages/Register.jsx`
- `client/src/pages/Dashboard.jsx`

**Root:**
- `package.json` — root scripts with concurrently
- `.gitignore`

### No Scope Changes
Implementation matches the User Story and Design Doc exactly. No new features or scope changes.
