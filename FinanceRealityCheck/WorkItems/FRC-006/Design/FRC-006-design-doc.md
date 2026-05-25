# FRC-006 Design Doc

## Summary
Implement a desktop-first React SPA shell that consumes the local Finance Planner API and surfaces health and capability summary contracts.

## Problem Statement
The API from FRC-005 is usable but requires manual endpoint calls. A lightweight local UI shell is required for non-technical users.

## Functional Requirements
1. Add a frontend app start command for local usage.
2. Landing view calls GET /health and shows status + version deterministically.
3. Planner summary view calls GET /planner/summary and renders capability list deterministically.
4. Error state is clear when API is unavailable.

## Non-Functional Requirements
- Initial render under 2 seconds on local machine.
- No external network dependency for core UI load.

## Proposed Approach
- Add Vite + React app under frontend/.
- Centralize API access in a small client wrapper with deterministic mapping.
- Render two route-level pages: Health and Planner Summary.
- Use explicit loading and error state boundaries for deterministic UI outputs.
- Add automated frontend tests with Vitest + React Testing Library.

## Contracts
- GET /health -> { status: string, version: string }
- GET /planner/summary -> { interface: string, capabilities: string[] }

## Risks and Mitigations
- Risk: API unavailable when UI starts.
  - Mitigation: explicit retry button and deterministic error message.
- Risk: payload drift.
  - Mitigation: strict UI contract mapping and tests with fixed fixtures.

## Test Strategy
- Unit/integration component tests for health and summary rendering.
- Error-state rendering tests for connectivity failure.
- Existing Python API tests remain green.
