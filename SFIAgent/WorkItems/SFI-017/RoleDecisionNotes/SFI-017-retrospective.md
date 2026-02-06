# SFI-017 Retrospective

## What Went Well

1. **User story iteration was fast** — three rounds of feedback (fixed filters → generic clauses → add caching) converged quickly because the user provided a clear reference screenshot (ADO/IcM query editor).
2. **TDD discipline** — 32 tests written before production code; all passed on first GREEN run with no rework.
3. **Pure-function design** — keeping `evaluate_clauses()` and helpers as pure functions made testing trivial and decoupled UI from logic completely.
4. **Full pipeline in one session** — PO → PM → QA → Architect → Developer → Refactor → Builder → Documentor completed without blocking issues.
5. **Test coverage breadth** — 20 test cases mapped to 32 test functions covering edge cases (None dates, list fields, USSec exclusion, And/Or precedence, corrupt cache).
6. **PyInstaller hidden-import** — caught the dynamic import issue proactively with `--hidden-import sfi_reporter.query_builder`.

## What Didn't Go Well

1. **Session freezes** — the token budget was exceeded twice during the developer and documentor phases, requiring the user to say "try again" and the agent to resume from context.
2. **configure_python_environment cancellation** — the environment configuration step was cancelled by the user mid-workflow, causing a restart of the developer phase.
3. **No zip rebuild** — the distribution zip was not rebuilt after the exe was updated; the user may need to manually repackage.

## Action Items

| # | Improvement | Owner |
|---|------------|-------|
| 1 | Commit more frequently during developer phase (after tests pass, after production code, after integration) to reduce risk of losing work on freezes | Process |
| 2 | Add a "checkpoint" habit — after each major sub-step, briefly summarize progress so context recovery is faster | Process |
| 3 | Consider adding a zip-rebuild step to the Builder role checklist | Process |

## Metrics

- **Tests**: 32 new tests, 171 total passing (0 failures)
- **Code**: ~530 lines production, ~400 lines test
- **Files changed**: 16 (2 modified, 14 new)
- **Iterations on user story**: 3
- **Roles traversed**: 9 (full pipeline)
- **Session interruptions**: 2 (token budget exceeded)
