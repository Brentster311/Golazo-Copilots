# SFI-040 Retrospective

## What went well
- Scope discipline held: implementation stayed UI-only in `SFIReporter/src/sfi_reporter/app.py` with no API/cache/schema changes.
- Test-first execution was followed and evidenced: 3 targeted tests were added first, failed in red phase, then passed after implementation.
- Regression confidence remained strong: focused tests passed (`3/3`), table test file passed (`131/131`), and full SFIReporter suite remained green (`955 passed, 2 warnings, 0 failures`).
- Workflow gating produced complete artifacts across roles (design, QA, architect, developer, documenter, builder, retrospective) with clear handoff notes.
- Capability tooling was used (impact + validate), so capability awareness was present even when mappings were incomplete.

## What didn't go well
- Capability impact analysis reported **0 affected capabilities** for touched files (`app.py`, `test_sfi_039_app.py`), indicating registry coverage gaps for UI-table changes.
- Capability validation surfaced pre-existing `key_files` gaps in reporter-related cards, reducing trust in registry completeness for downstream planning.
- Builder packaging flow had avoidable friction: running `python -m build` inside `SFIReporter/` hit local module shadowing (`build/`), requiring command rerun from repo root.
- Process consistency issue persisted across nearby completed work items (closure normalization for SFI-036..039), indicating closure-step drift rather than a one-off mistake.

## Action items
1. **Capability mapping hardening (process):** In architect/developer checklist, require `golazo_capabilities(action="impact", files=[...])` and if result is empty for changed code, log either (a) registry update task or (b) explicit rationale in role notes before moving to builder.
2. **Capability validation hygiene (process):** Add a recurring maintenance work item to resolve pre-existing `key_files` gaps found by `golazo_capabilities(action="validate")`; track closure by capability card.
3. **Builder command guardrail (process):** Update builder role guidance to prefer root-invoked build command (`python -m build "SFIReporter"`) and include a preflight note about local package-name shadowing risks.
4. **Closure consistency control (process):** Add a final closure checklist item to verify profile-specific end-state and closure artifacts before retrospective starts.
5. **Assumption used for this retrospective:** Existing role notes, test outputs, and capability reports are treated as the source of truth; no independent reruns were performed in retrospective role.

## Metrics
- **Quality throughput (observed):** 3 new feature tests; red-to-green achieved; no regressions in full suite (`955 passed, 0 failures`).
- **Change containment (observed):** 1 production file changed for feature behavior (`SFIReporter/src/sfi_reporter/app.py`) plus related tests/docs.
- **Capability-tool usage (observed):** 1 impact check + 1 validate check recorded; impacted capabilities detected = 0 for changed UI files.
- **Build reliability (observed):** 1 initial packaging command failure (shadowing) followed by successful root-level build.
- **Process improvement targets (next 2 work items):**
	- Impact coverage: reduce "0-impact due to missing mapping" cases on changed files by adding/maintaining relevant capability mappings.
	- Builder reliability: reduce first-attempt packaging failures to zero by applying the command guardrail.
	- Closure consistency: achieve 100% profile-consistent closure artifacts before retrospective handoff.
