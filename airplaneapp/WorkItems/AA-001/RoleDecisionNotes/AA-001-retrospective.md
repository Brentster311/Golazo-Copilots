# AA-001 — Retrospective

## What Went Well

1. **Clean vertical slice scoping.** AA-001 was scoped as scaffolding + auth — the minimum needed to be independently demonstrable. All brainstorm context was captured upfront, avoiding back-and-forth during implementation.

2. **TDD worked smoothly.** Tests were written first, confirmed failing (red), then production code made them pass (green). This caught the email normalization requirement early.

3. **Security reviewed at multiple stages.** Domain expert flagged proactive security concerns (generic error messages, JWT expiry, email normalization). QA raised them as review items. Architect confirmed. Developer implemented. No security gaps in the final product.

4. **Small file sizes.** The modularity audit showed the largest source file at 73 lines. The codebase starts clean and modular, setting a good pattern for AA-002+.

5. **Capabilities registry updated immediately.** Three capabilities registered after developer phase, validated by builder. Future work items can use impact analysis from day one.

## What Didn't Go Well

1. **Test DB file locking on Windows.** The initial test setup used `fs.unlinkSync` to delete the SQLite DB between test suites. On Windows, this caused EBUSY errors because Prisma held the file lock. Fixed by switching to `--runInBand` and using `deleteMany()` for cleanup instead of file deletion. **Lesson:** SQLite file operations on Windows need extra care; prefer in-process cleanup over filesystem operations.

2. **No git repository initialized.** The builder role calls for git commit/push, but no git repo exists in this workspace yet. This should be set up before the next work item.

## Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Initialize git repo and make first commit before AA-002 | Project Owner | High |
| 2 | Consider adding ESLint config as a chore task | Developer | Low |
| 3 | Add `test.db` to `.gitignore` explicitly | Developer | Medium |

## Metrics

- **Test coverage:** 27 automated tests covering all 5 acceptance criteria
- **Files created:** 20 (11 server, 9 client)
- **Role deviations:** 0
- **Scope changes:** 0
- **Build warnings:** 0

## Capability Registry Check

`golazo_capabilities` was used appropriately:
- Architect ran impact analysis (no existing capabilities to impact — greenfield)
- Developer updated capabilities.yaml with 3 new capabilities
- Builder validated all key_files exist

No missed opportunities for impact analysis.
