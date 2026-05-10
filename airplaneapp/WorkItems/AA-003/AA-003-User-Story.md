# AA-003: Aircraft Profile Management

**Status**: BACKLOG

## User Story

- **Title:** Aircraft Profile Management
- **As a:** organization admin
- **I want:** to add, edit, and view aircraft profiles within my organization
- **So that:** each plane has a record with its identifying details, and pilots/techs can see which aircraft are available

- **Out of scope:**
  - Hobbs/Tach entry — AA-004
  - Maintenance schedules attached to aircraft — AA-005
  - Reservations — AA-006
  - Aircraft deletion (future; soft-delete or archive)
  - Aircraft photo/image upload

- **Assumptions:**
  - **Assumption (explicit):** Interface type: web. Platform/persistence: same as AA-001.
  - **Assumption (explicit):** Only Admins can add or edit aircraft. Pilots and Techs can view aircraft profiles within their org.
  - **Assumption (explicit):** Aircraft profile fields: tail number (unique within org), make, model, year, engine type, current Hobbs, current Tach. Current Hobbs and Tach are the seed values for initial setup; AA-004 will manage ongoing entries.
  - **Assumption (explicit):** Seed data for development includes a Cessna 172 and a Piper Cherokee (per brainstorm).

- **Acceptance Criteria (bulleted, testable):**
  - [ ] An Admin can add an aircraft to their organization with tail number, make, model, year, engine type, initial Hobbs, and initial Tach; duplicate tail numbers within the same org are rejected.
  - [ ] An Admin can edit an existing aircraft's profile fields (except tail number, which is immutable after creation).
  - [ ] All org members (pilot, tech, admin) can view a list of aircraft in their organization with key details displayed.
  - [ ] The database schema includes an Aircraft table linked to Organization with appropriate fields and constraints.
  - [ ] The development seed script creates sample Cessna 172 and Piper Cherokee aircraft.

- **Non-functional requirements:**
  - Aircraft API endpoints require authentication and org membership verification.
  - Only Admin role can create/update aircraft (enforced server-side).
  - Tail number is validated for format (alphanumeric, max 10 chars).

- **Telemetry / metrics expected:**
  - None for MVP.

- **Rollout / rollback notes:**
  - Depends on AA-002 (organizations). New Aircraft table + endpoints. No changes to existing models.
