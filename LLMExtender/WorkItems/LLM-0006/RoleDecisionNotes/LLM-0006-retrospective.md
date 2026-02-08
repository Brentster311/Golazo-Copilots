# LLM-0006 Retrospective

## What went well
- TDD approach: tests written first, all 14 test cases (19 functions) passed on first run
- Clean design: `url_fetcher.py` is self-contained, no changes needed during refactor
- `AuthStrategy` reuse: same `AzureChainedAuth` with different `scope` works for URL auth
- Total test count grew from 92 → 111 with zero regressions

## What didn't go well
- GCP state was lost between sessions — had to recreate the work item and fast-forward through roles
- The initial client method signature used `url_auth: str` (plain token) but tests expected `url_auth: AuthStrategy` — caught during test review before running

## Action items
- Consider persisting GCP state more durably or adding a "resume" command
- Always review test expectations for parameter types before writing implementation

## Metrics
- 19 new tests, 111 total, 0 failures
- Commit: `86af465`
