# AA-007: Forgot Password Flow

**Status**: BACKLOG

## User Story

- **Title:** Forgot Password Flow
- **As a:** registered user
- **I want:** to click a "Forgot password?" link on the login page and reset my password
- **So that:** I can regain access to my account if I forget my credentials

- **Out of scope:**
  - Account lockout after failed attempts
  - Two-factor authentication
  - Admin-initiated password resets

- **Assumptions:**
  - **Assumption (explicit):** For MVP (local-only), the reset flow will use a token-based approach. Since there's no email service yet, the reset token/link will be logged to the server console (swappable to email delivery when cloud hosting is added).
  - **Assumption (explicit):** Interface type: web (same React frontend from AA-001). Platform: same as existing. Persistence: same SQLite database.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] The login page displays a "Forgot password?" link below the login form.
  - [ ] Submitting an email on the forgot-password page generates a time-limited reset token (expires in 1 hour) and returns a success message regardless of whether the email exists (prevents user enumeration).
  - [ ] A user can submit a new password with a valid reset token and successfully log in with the new password.
  - [ ] Expired or already-used reset tokens are rejected with a clear error message.

- **Non-functional requirements:**
  - Reset tokens are cryptographically random (not guessable).
  - Reset tokens are single-use and expire after 1 hour.
  - The auth service interface is extended, not replaced.

- **Telemetry / metrics expected:**
  - None for MVP.

- **Rollout / rollback notes:**
  - Depends on AA-001 (user-auth capability). Additive change — no breaking impact on existing login flow.
