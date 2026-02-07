# SFI-018 Retrospective

**Work Item:** SFI-018 — In-App Azure Login (Browser Fallback)  
**Date:** 2025-07-11  
**Profile:** complete (all 9 roles)

---

## What Went Well

| # | Item |
|---|------|
| 1 | **Single change-point design** — all modifications confined to `accia-s360/auth.py`; no consumer code (`s360_client`, `sfi_reporter`) required changes. This validates the layered architecture established in SFI-001 through SFI-004. |
| 2 | **TDD red → green** — all 10 tests were written first and confirmed failing before implementation. Zero test rework after production code was written. |
| 3 | **Clean scope** — the work item stayed tightly scoped: auth chain + LAUNCHME.ps1 removal + doc updates. No scope creep. |
| 4 | **Refactor-expert found nothing** — code was clean on the first pass, which is a positive signal for Architect binding decisions being effective. |
| 5 | **Clarifying questions up-front** — 3 questions (browser vs device-code, fallback vs replace, remove LAUNCHME?) prevented design churn. |
| 6 | **Commit granularity** — single meaningful commit (`872a38d`) for all production + test + doc changes, followed by a separate role-notes commit. |

## What Didn't Go Well

| # | Item | Impact |
|---|------|--------|
| 1 | **`ChainedTokenCredential` evaluation and rejection** — The design doc initially proposed `ChainedTokenCredential`, but during Architect review it was rejected for lack of logging visibility. The explicit try/except approach is better, but the PM → Architect hand-off could have caught this earlier. | Low — caught before code phase. |
| 2 | **Role-notes commit timing** — the main commit (`872a38d`) included some role notes but the refactor-expert/builder/documentor notes had to be committed separately after. Ideally role notes should be committed incrementally or all at the end in one pass. | Negligible — cosmetic. |
| 3 | **BUILD_MANIFEST drift risk** — BUILD_MANIFEST.md was updated manually. If a future work item changes the build process, it could fall out of sync. | Medium — could cause user confusion. |

## Action Items

| # | Proposal | Effort | Priority |
|---|----------|--------|----------|
| 1 | **Architect should review PM design doc for library choices** — add a checklist item in the Architect role: "Validate library/API selections from design doc." | Small | Medium |
| 2 | **Batch role-notes commit at retrospective** — instead of committing role notes mid-workflow, accumulate them and commit once during the Builder or Retrospective role. | Small | Low |
| 3 | **Consider a `build.ps1` script** — a single build script that produces the exe + zip and self-validates against BUILD_MANIFEST. This would be a new work item. | Medium | Medium |

## Metrics

| Metric | Value |
|--------|-------|
| Total tests written | 10 |
| Tests passing | 10 / 10 |
| Full suite passing | 133 / 133 (SFI Reporter) + 10 / 10 (auth chain) |
| Production files changed | 1 (`auth.py`) |
| Files deleted | 1 (`LAUNCHME.ps1`) |
| Docs updated | 3 (`BUILD_MANIFEST.md`, `README.md`, `User-Story.md`) |
| Commits | 2 (`872a38d` production, `a43c8b3` role notes) |
| Roles completed | 9 / 9 |
| Scope changes | 0 |

## Summary

SFI-018 was a clean, well-scoped work item. The layered architecture paid dividends — a single file change in the auth layer propagated cleanly to all consumers. TDD worked as intended. The only process friction was minor (commit timing, design doc library validation). No process file changes proposed for this iteration.
