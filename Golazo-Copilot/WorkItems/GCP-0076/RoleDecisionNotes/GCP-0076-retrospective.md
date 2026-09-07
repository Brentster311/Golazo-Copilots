# GCP-0076 Retrospective

## What Went Well

- The initial inventory distinguished active, legacy, nested-project, and test-workspace registries before cleanup.
- TDD isolated path behavior first, then registry population and repository cleanup.
- Live MCP list, validate, and impact calls proved the populated registry is useful rather than merely syntactically valid.
- Repository-wide Ruff was brought fully clean.

## What Didn't Go Well

- GCP-0065 canonicalized the query tool but did not audit bootstrap, work-item creation, or status, allowing path literals to diverge.
- A tracked test fixture at a legacy path was migrated during testing, revealing that fixtures also need workspace-boundary reasoning.
- The 10 ms wall-clock test is sensitive to coverage instrumentation, and Windows occasionally locks generated fixture files during teardown; both passed in clean reruns.

## Action Items

- For path migrations, inventory every reader, writer, status reporter, template, fixture, and user-facing document.
- Treat zero impact as “no existing card matched,” not as evidence that a new card is unnecessary.
- Keep capability cards current whenever durable contracts or policy tests are introduced.
- Consider a future work item to make timing tests use a benchmark strategy resilient to instrumentation and scheduler pauses.

## Metrics

- One canonical registry per workspace boundary.
- Five top-level capability cards, all key files valid.
- 551 tests passed; 3 optional Azure Identity tests skipped.
- Repository-wide Ruff passed.
