# SFI-040 Test Cases

## Mapping to Acceptance Criteria

### AC1: Score appears before Cost
1. **Services table column order**
   - Arrange: Instantiate app UI.
   - Act: Inspect `services_tree` columns.
   - Assert: `score` index < `cost` index.
2. **Program table column order**
   - Assert same ordering in `program_tree`.
3. **Action Items table column order**
   - Assert same ordering in `action_tree`.

### AC2: Score/Min column exists and populated
4. **Column existence**
   - Assert `score_per_min` column exists in all three tables.
5. **Column heading label**
   - Assert heading text equals `Score/Min`.

### AC3: Cost > 0 uses score/cost
6. **Service row ratio non-zero cost**
   - Arrange data with `score=80`, `cost=40`.
   - Assert displayed ratio is `2.00`.
7. **Program row ratio non-zero cost**
   - Arrange data with `score=45`, `cost=30`.
   - Assert displayed ratio is `1.50`.
8. **Action row ratio non-zero cost**
   - Arrange data with `score=10`, `cost=8`.
   - Assert displayed ratio is `1.25`.

### AC4: Cost == 0 shows infinity symbol
9. **Zero-cost fallback rendering**
   - Arrange any row with incoming `cost=0` and `score>0`.
   - Assert displayed `Cost` is `28,800`.
   - Assert displayed `Score/Min` uses `score / 28800`.
10. **Zero/zero fallback rendering**
   - Arrange row with incoming `cost=0`, `score=0`.
   - Assert displayed `Cost` is `28,800`.
   - Assert displayed `Score/Min` is `0.00`.

### AC5: No persistence/data pipeline changes
11. **No cache schema changes**
   - Regression: existing cache read/write tests pass unchanged.
12. **No service-layer contract changes**
   - Regression: existing refresh/data tests pass unchanged.

## Failure Messages (examples)
- "Expected Score column before Cost in services table"
- "Expected Score/Min column heading to be 'Score/Min'"
- "Expected zero-cost fallback cost to be 28,800"
