# EES-00019 Retrospective

## What Went Well

1. **TDD 4-phase approach was effective** — Each phase (AST Model → Evaluator → LLM Integration → GUI) was independently testable. RED/GREEN cycles were clean — no test required modification after initial writing.

2. **Zero regressions** — All 344 existing tests continued to pass unchanged throughout the implementation. The additive design (new classes alongside legacy) was the right call.

3. **Golazo workflow provided good structure** — The PO → PM → QA → Architect → Developer pipeline front-loaded the right questions (RC-1 through RC-6 in QA, capability impact in Architect).

4. **Clean separation of concerns** — AST models, parser, evaluator, LLM handler, and GUI adapter are all independently testable with no coupling between phases.

5. **Capability registry validation** caught no issues — all 9 capabilities remained valid after changes.

## What Didn't Go Well

1. **MCP server workspace root issue** consumed ~2 turns at the start. The server defaulted to `C:\Users\Brent` instead of the workspace root. This was a pre-existing configuration problem, not an EES-00019 issue.

2. **Git push blocked by `Amjad.zip`** — A 109 MB zip file (unrelated to this work item) prevents pushing to GitHub. This should have been caught earlier.

3. **Full pipeline wiring deferred** — The system prompt, `_TOOLS` schema, `main.py` CLI, and `app.py` GUI still reference the legacy format. The new AST code is implemented and tested but not yet the default path. This means the convergence fix (the original motivation) won't be observable until a follow-up work item wires everything together.

4. **Token budget constraints** — The initial conversation hit the context window limit during Phase 1 GREEN, requiring a resume.

## Action Items

| # | Action | Owner | Type |
|---|--------|-------|------|
| 1 | Create follow-up work item to wire AST into the full extraction/evaluation pipeline (system prompt, `_TOOLS`, `main.py`, `app.py`) | PO | New User Story |
| 2 | Add `Amjad.zip` and `*.zip` to `.gitignore` | PO | Bug fix |
| 3 | Ensure `.vscode/mcp.json` with correct `cwd` is committed so MCP server workspace root is always correct | PO | Bug fix |
| 4 | Consider removing legacy `Rule`, `RuleConditions`, `RuleOutput`, `RuleEvaluator` after pipeline wiring is complete | PO | Future cleanup |

## Metrics

- **Test count growth**: 344 → 372 (+28 new tests, 8.1% increase)
- **Files changed**: 7 modified, 4 deleted, 4 new test files
- **New production code**: ~400 lines across 5 files
- **Regression failures**: 0
- **Roles completed**: 9/9
- **TDD cycle violations**: 0 (all RED confirmed before GREEN)
