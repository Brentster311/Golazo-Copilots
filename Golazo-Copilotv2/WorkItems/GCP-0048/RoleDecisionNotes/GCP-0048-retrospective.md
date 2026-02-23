# GCP-0048 — Retrospective Decision Notes

## What Went Well
1. **Clean TDD cycle** — 33 tests failed in red phase, all 357 passed in green phase, zero regressions
2. **Accurate design** — front-matter format worked on first implementation; no design changes needed during dev
3. **QA caught the refactor filename issue** — `{id}-refactor.md` vs `{id}-refactor-expert.md` could have caused AC6 drift test failures
4. **Parallel with GCP-0051** — working on markdown-only changes was fast since no Python runtime behavior changed
5. **Capability impact analysis confirmed zero contract changes** — 6 capabilities affected, all NONE impact

## What Didn't Go Well
1. **User story lost during branch switch** — `git stash` removed uncommitted work from previous session. Had to recreate the user story on the new branch. Future work: commit user stories immediately when creating them.
2. **Closure file gate** — POA required a `{id}-closure.md` file that's only needed during closure re-entry, requiring `gcp_consent` to bypass. This is a known quirk of the deployed POA role file vs the source default.
3. **Local `.github/roles/` not present** — several roles showed "Role instructions not found" because bootstrap hadn't run on this branch. The test suite reads from package defaults (correct) but gcp_status reads from `.github/roles/` (not present). Minor UX issue.

## Action Items
1. **Commit user stories to main immediately** when batch-creating them, before starting dev work on any branch
2. **Consider conditional Required Outputs** — the closure.md gate should not apply during initial pass (potential GCP enhancement)
3. **Run `gcp_bootstrap`** at start of each work item to ensure local role files exist

## Metrics
- Red phase: 33 failed / 31 passed
- Green phase: 357 passed / 0 failed
- Time: rapid (markdown-only changes, no complex Python logic)
- Files changed: 10 role files + 1 test file + 14 work item artifacts
