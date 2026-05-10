# AirplaneApp

A web application for pilots to track aircraft Hobbs/Tach time, maintenance schedules, and reservations.

## Quick Start

### Prerequisites
- Node.js >= 18
- npm

### Installation

```bash
# Install all dependencies (root, server, client)
npm run install:all
```

### Environment Setup

```bash
# Copy the example env file
cp server/.env.example server/.env

# Edit server/.env and set a strong JWT_SECRET
```

### Database Setup

```bash
cd server
npx prisma migrate dev
cd ..
```

### Run Development Servers

```bash
npm run dev
```

This starts both:
- **Client:** http://localhost:5173 (React + Vite)
- **Server:** http://localhost:3001 (Express API)

### Run Tests

```bash
npm test
```

## Project Structure

```
airplaneapp/
├── client/                  # React frontend (Vite)
│   ├── src/
│   │   ├── pages/           # Login, Register, Dashboard
│   │   ├── services/        # API client
│   │   ├── context/         # AuthContext
│   │   └── App.jsx          # Routing
│   └── package.json
├── server/                  # Express API
│   ├── src/
│   │   ├── routes/          # API route handlers
│   │   ├── middleware/       # Auth middleware
│   │   ├── services/        # Business logic (AuthService)
│   │   └── app.js           # Express configuration
│   ├── prisma/              # Schema & migrations
│   ├── __tests__/           # Jest + Supertest tests
│   └── package.json
├── package.json             # Root scripts
└── .gitignore
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | No | Register a new user |
| POST | `/api/auth/login` | No | Log in |
| GET | `/api/auth/me` | Yes | Get current user |
| GET | `/api/health` | No | Health check |

## Tech Stack

- **Frontend:** React 18, Vite, React Router
- **Backend:** Node.js, Express, Helmet
- **Database:** SQLite via Prisma ORM
- **Auth:** bcryptjs + JWT
