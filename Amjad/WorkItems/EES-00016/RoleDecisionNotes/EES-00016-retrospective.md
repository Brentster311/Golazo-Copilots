# EES-00016 Retrospective

## What went well
- **TDD cycle was clean**: 27 tests written first, all passed on first green implementation. The match/case pattern kept `validate_value()` simple.
- **Refactoring found real duplication**: `_CHAINING_KINDS` was defined in two places. Caught and consolidated during refactor role.
- **Design docs and test cases were high quality**: They made implementation straightforward — no ambiguity in what to build.
- **String removal was fast**: Once the user decided, the change was 3 lines in production code and 6 lines in tests. The design made it trivial to evolve.

## What didn't go well
- **Mid-implementation scope change**: The user story was written with `string` as a supported type, then the user decided to drop it post-implementation. This required re-updating the user story, design doc, test cases, and tests — work that could have been avoided if the decision was made during the PO or PM phase.
- **Design docs accumulated stale references**: 19 occurrences of "string" across design docs needed updating. A smaller doc surface would reduce this maintenance overhead.

## Action items
1. **Frame type decisions as explicit PO questions early**: When a design includes a "permissive fallback" (like `string` type), proactively ask the PO during design review whether they want it — don't assume.
2. **Keep design docs lean**: Large design docs increase the cost of mid-stream scope changes. Consider whether all sections are genuinely needed.

## Metrics
- Track how often post-implementation scope changes occur. Target: fewer than 1 in 5 work items.
