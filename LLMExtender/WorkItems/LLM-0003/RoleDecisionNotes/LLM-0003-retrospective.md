# LLM-0003 Retrospective

## What Went Well

1. **Feature branch created first** — Lesson from LLM-0001 applied. `feature/LLM-0003-auth-manager` created before any code.
2. **TC cross-reference done** — All 14 QA-defined test cases verified against actual test functions before marking `testsWrittenFirst`. New developer role gate worked.
3. **Zero regressions** — All 30 LLM-0001 tests passed throughout. `api_key` default change (A5) was backward compatible.
4. **Architect A4 (client integration) caught early** — Asking the PO whether integration was in scope avoided building the wrong thing.
5. **Refactor caught real bug** — `_config` was storing the pre-auth-resolution copy. Fixed before it could cause issues downstream.
6. **Build smoke test in refactor/builder** — `pip install -e .` verified (LLM-0001 retro action item applied).

## What Didn't Go Well

1. **Role notes file naming mismatch** — Created `LLM-0003-refactor-expert.md` but GCP expected `LLM-0003-refactor.md`. Had to rename to unblock transition. This happened because LLM-0001 used `refactor` but the role is called `refactor-expert` in the GCP transition system.

## Action Items

| # | Proposal | Impact |
|---|---|---|
| 1 | **Standardize role notes filename to match GCP role slug** — always use the exact role name from `gcp_transition` (e.g., `refactor-expert` not `refactor`). Or check what LLM-0001 used and stay consistent. | Avoids transition failures. |

## Metrics

- **Tests written before code:** 23/23 (100%)
- **Tests passing at completion:** 53/53 (100%) — 30 LLM-0001 + 23 LLM-0003
- **Build/install success:** Yes (first try)
- **Roles traversed:** Architect → Developer → Refactor → Builder → Documentor → Retrospective (6 roles in dev phase)
- **Rework cycles:** 0 (build passed first try)
- **PO consultations:** 1 (A4 scope question — answered correctly)
