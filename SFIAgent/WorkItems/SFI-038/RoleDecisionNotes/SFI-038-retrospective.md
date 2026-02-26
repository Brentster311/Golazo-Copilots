# SFI-038 — Retrospective

## What Went Well
- TDD cycle was clean: 14 tests written first, all failed, then all passed after implementation.
- Single-pass score computation in the existing `do_refresh` loop — no second iteration needed.
- Dual-key lookup (name + KPIID) adds resilience.
- No new dependencies introduced.

## What Didn't Go Well
- Branch naming: SFI-038 branch already existed from the reverted prior SFI-038 work. Had to commit on SFI-039 branch instead.
- The test `test_returns_dict_keyed_by_name` initially expected 3 entries but got 6 due to dual-key design — minor test/implementation mismatch caught quickly.

## Action Items
- None — clean implementation cycle.

## Metrics
- 14 new tests, all green
- 370 total tests passing (3 pre-existing live failures unrelated)
- Zero new dependencies
