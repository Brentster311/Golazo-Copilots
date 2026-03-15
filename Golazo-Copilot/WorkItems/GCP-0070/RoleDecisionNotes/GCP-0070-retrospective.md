# GCP-0070 Retrospective

## What Went Well

- The removal was executed cleanly across registration, dispatch, formatting, legacy compatibility, docs, and tests, so the public contract stayed consistent.
- Tests were updated early and provided fast feedback for the tool-surface change.
- The new spine guidance is more explicit than the removed tool UX because it points directly to the interpreter and feed that actually matter.

## What Didn't Go Well

- The direct Golazo role-transition MCP wrapper was not available in the active tool surface, so workflow progression had to be driven through the underlying package transition implementation.
- The repository still contains a placeholder capability entry that fails builder validation and creates avoidable noise during release verification.
- The workspace status reports stale bootstrap files from prior versions, which makes it harder to tell whether current warnings are relevant to the active work item.

## Action Items

- Add or restore a dedicated orchestrator-accessible role transition tool wrapper so workflow advancement does not require fallback execution paths.
- Replace or remove the placeholder `example-capability` entry so builder capability validation is signal-bearing.
- Consider a bootstrap refresh work item that reconciles stale instruction-version warnings separately from product changes.

## Metrics

- Workflow completion should require zero fallback transition invocations.
- Builder capability validation should produce zero known-irrelevant failures.
- Future tool-surface removals should keep targeted regression suites green in a single focused pytest run.