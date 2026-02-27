# SFI-033 Retrospective

## What Went Well
- **TDD discipline**: 27 tests written first, all failed (red), then all passed after implementation (green). Clean cycle.
- **Scope clarity**: User Story was explicit about what to remove vs. what to add. Expanded scope (LLM removal made permanent) was decided before development started.
- **Phase 0 elimination**: Removing ~1,025 lines of old LLM code first made the subsequent phases cleaner — no merge conflicts with dead code.
- **ghcpsdk reference**: Having a working reference app (353 lines) made porting AsyncBridge + CopilotPanel straightforward.
- **Net code reduction**: +1,157 / -2,182 lines — the codebase is smaller and simpler after this feature.
- **Capability registry**: Impact analysis correctly identified `reporter-build` as affected.

## What Didn't Go Well
- **DoR done twice**: Scope expansion after initial DoR completion required redoing PM, QA, and Architect roles. Early scope lock would have saved time.
- **QA capability check was incomplete**: QA originally checked only 3 files and found 1 affected capability; Architect's broader check found 5. The QA role should check all files in the design doc's modification table.
- **Tk fixture flakiness**: Creating/destroying multiple `tk.Tk()` roots in tests caused Tcl init errors — required defensive `try/except` in fixture. Known issue but adds noise.
- **Pre-existing test failures**: 2 failures + 8 errors in `test_tk_app.py`/`test_data.py` unrelated to SFI-033 but create noise when running the full suite.

## Action Items
1. **QA role guidance**: When checking capabilities.yaml, always check ALL files listed in the design doc's "Files to Delete" and "Files to Modify" tables, not just a subset.
2. **Fix pre-existing test failures**: Create a work item to fix the 2 failures in `test_tk_app.py` (aggregate_by_owner assertions) and the fixture issues.
3. **Tk test helper**: Consider a shared module-scoped Tk root fixture in `conftest.py` to avoid re-creating roots per test class.

## Metrics
- **Tests**: 27 new, 0 regressions
- **Lines**: -1,025 net (removal > addition)
- **Roles completed**: 9/9
- **Blocked transitions**: 0
