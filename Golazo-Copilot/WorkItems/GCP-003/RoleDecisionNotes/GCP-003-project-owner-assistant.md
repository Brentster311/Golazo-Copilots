# GCP-003: Project Owner Assistant Decision Document

## Work Item
GCP-003 — Enforce TDD and Builder Git Operations

## Decisions Made

### 1. Single User Story
Both TDD enforcement and git operations are related process improvements from RETRO-001. They share a common theme: "enforce discipline in the workflow."

### 2. Scope Limited to Documentation Changes
This work item only modifies `.github/` instruction files. No code changes.

### 3. Acceptance Criteria Are Self-Verifiable
Each criterion can be verified by reading the updated files.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Split into 2 stories (TDD + Git) | Too small; tightly coupled |
| Add git hooks for enforcement | Out of scope; adds complexity |

## Tradeoffs Accepted

- No automated enforcement (relies on Copilot following instructions)
- Branch creation is manual command (no git hooks)

## Known Limitations or Risks

- Copilot may still violate TDD if instructions aren't clear enough
- Git commands may fail in restricted environments
