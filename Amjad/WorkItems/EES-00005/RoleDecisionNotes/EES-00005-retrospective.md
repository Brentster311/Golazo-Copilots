# Retrospective — EES-00005

## What Went Well

- **Adapter pattern**: Separating pure adapter functions from Tkinter code kept 100% of the business logic testable without a GUI event loop
- **Capability registry**: Impact analysis correctly identified 7 downstream capabilities; the additive-only approach meant zero contract changes
- **TDD cycle**: RED → GREEN → REFACTOR executed cleanly; 18 new tests added and all 207 pass
- **Consistent patterns**: The worker/callback pattern aligns with established repo patterns (mock-friendly, no global state)
- **Zero new dependencies**: Tkinter ships with Python — no changes to `pyproject.toml` dependencies

## What Didn't Go Well

- **Context recovery overhead**: Multi-session work requires re-loading significant context. The conversation summary helps but still costs tokens each resumption
- **Manual GUI testing gap**: 8 manual test cases defined but not executed as part of an automated suite. Tkinter's event loop makes automated GUI testing difficult without additional tooling
- **`_save_all` method length**: The save method in `app.py` is ~40 lines orchestrating multiple operations. It works but could benefit from a service-layer extraction in a future refactor

## Action Items

| # | Proposal | Effort |
|---|----------|--------|
| 1 | Consider extracting a `ProcessingService` class that handles the save orchestration (shared between CLI and GUI) | Future story |
| 2 | Evaluate `unittest.mock.patch` with Tkinter `root.after()` for automated GUI integration tests | Future spike |
| 3 | Document the manual test execution checklist in the test cases doc for QA handoff | Low |

## Metrics

- **Test count**: 189 → 207 (+18 for adapters/workers)
- **Files added**: 5 production + 1 test
- **Coverage**: GUI adapter code covered; `app.py` GUI wiring not covered (manual testing only)
- **Dependencies added**: 0
