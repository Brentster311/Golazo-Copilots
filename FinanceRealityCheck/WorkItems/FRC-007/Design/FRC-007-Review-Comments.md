# FRC-007 Review Comments

## Domain Expert Guidance
- Keep direct connectors isolated from planner storage logic.
- Normalize provider-specific errors into stable categories for UI/actionability.
- Maintain fixture path for deterministic local and CI testing.

## Quality Assurance Review
- Add tests for direct auth success/failure and transaction retrieval.
- Verify retry after transient connectivity error does not create duplicate rows.
- Verify fixture tests remain green after direct-path additions.

## Architect Notes
- Define explicit connector protocol contract for fetch semantics.
- Avoid persisting plaintext credentials; continue encrypted token storage path.
- Ensure direct connectors are opt-in and injectable to limit blast radius.
