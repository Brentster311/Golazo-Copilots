# AA-002: Organization Creation & Member Invitations

**Status**: BACKLOG

## User Story

- **Title:** Organization Creation & Member Invitations
- **As a:** registered user (admin)
- **I want:** to create an organization, add aircraft placeholders, and invite other users with assigned roles (pilot, tech, admin)
- **So that:** I can set up my flying club or partnership and grant appropriate access to members

- **Out of scope:**
  - Aircraft profile details (make/model, engine, year) — that's AA-003
  - Hobbs/Tach tracking — AA-004
  - Email delivery of invitations (local-only MVP; invitations are via invite code/link)
  - Removing or banning members (future work item)

- **Assumptions:**
  - **Assumption (explicit):** Interface type: web (React frontend). Platform: same as AA-001. Persistence: SQLite via Prisma.
  - **Assumption (explicit):** Invitation flow uses a generated invite code/link that the admin shares out-of-band (copy/paste). The invitee enters the code when logged in to join the org. No email sending for MVP.
  - **Assumption (explicit):** The user who creates an org is automatically assigned the Admin role in that org.
  - **Assumption (explicit):** A user can hold different roles in different orgs (e.g., Admin in one, Pilot in another).

- **Acceptance Criteria (bulleted, testable):**
  - [ ] A logged-in user can create a new organization with a name; the creator is automatically assigned the Admin role in that org.
  - [ ] An Admin can generate an invite link/code for their org with a specified role (pilot, tech, or admin); the invite code is displayed for copying.
  - [ ] A logged-in user can enter an invite code to join an organization; upon joining, they are assigned the role specified in the invite.
  - [ ] A user who belongs to multiple organizations sees an org switcher in the UI to navigate between them.
  - [ ] The database schema includes Organization, Membership (user-org-role junction), and Invitation tables with appropriate constraints.

- **Non-functional requirements:**
  - Invite codes are cryptographically random and single-use.
  - Invite codes expire after 7 days.
  - Role assignment is enforced server-side (not just UI).
  - API endpoints for org management require authentication.

- **Telemetry / metrics expected:**
  - None for MVP.

- **Rollout / rollback notes:**
  - Depends on AA-001 (user-auth). Additive — new tables and endpoints, no changes to existing auth flow.
