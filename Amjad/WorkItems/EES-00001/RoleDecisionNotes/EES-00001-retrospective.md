# Retrospective — EES-00001

## What Went Well

1. **TDD approach worked cleanly** — Writing all 28 test cases (66 tests) before implementation caught issues early and made refactoring safe. All refactorings applied with zero regressions.
2. **Design doc caught architectural decisions early** — The LLM provider decision, auth model, and data format were all locked down before code was written.
3. **Refactor-expert role added real value** — Extracted custom exceptions from library classes, eliminated duplication, and added `Fact.match_key()`. These are genuine quality improvements.
4. **Incremental vertical slice** — Starting with the simplest possible end-to-end flow (CLI, single incident, YAML persistence) delivered a working system without overengineering.
5. **Capability registry integration** — Having `capabilities.yaml` from the start enables impact analysis for future work items.

## What Didn't Go Well

1. **Mid-development architectural change** — The LLM provider was changed from OpenAI to Azure OpenAI *after* developer role had started. This required reverting to architect (2 deviations recorded). The LLM provider choice should have been pinned during the PM or Architect role before any code was written.
2. **State.json overwrite during context recovery** — Calling `gcp_create_workitem` during session recovery overwrote the existing state.json. The `workspace_path` parameter workaround was not obvious.
3. **Deferred imports went unnoticed** — Two `from ees.models import Incident` lines were placed inline during initial development. This is a code smell that the developer role should catch before handoff.
4. **Windows chmod test issue** — `os.chmod(dir, 0o444)` doesn't enforce on Windows. The initial test was platform-specific. Cross-platform testing considerations should be flagged earlier.

## Action Items

| # | Improvement | Target |
|---|-------------|--------|
| 1 | **Pin LLM/cloud provider in PM role** — Add a checklist item to the program-manager role requiring explicit provider + auth strategy before architect begins | `.github/roles/program-manager.md` |
| 2 | **Add cross-platform note to developer role** — Warn about platform-specific behavior in file I/O tests | `.github/roles/developer.md` |
| 3 | **Document state recovery procedure** — Add guidance to copilot-instructions.md about using `workspace_path` when recovering state across sessions | `.github/copilot-instructions.md` |

## Metrics

| Metric | Value |
|--------|-------|
| Roles completed | 9/9 |
| Deviations | 4 (2 revert_progress, 2 skip_outputs) |
| Total tests | 69 (66 original + 3 refactor) |
| Test pass rate | 100% |
| Production files | 8 (7 modules + exceptions.py) |
| Lines of production code | ~650 |
| Lines of test code | ~500 |
