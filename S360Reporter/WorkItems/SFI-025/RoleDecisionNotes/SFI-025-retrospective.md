# SFI-025 — Retrospective

## What Went Well
- **Clean single-pass implementation**: The ConfigureLLMDialog was straightforward. Leveraging existing `_load_setting`/`_save_setting` and the LLM-0012 discovery feature meant minimal new code.
- **TDD worked smoothly**: All 13 tests written first, confirmed red, then went green in one implementation pass.
- **LLM-0012 review paid off**: Reviewing the LLMExtender discovery feature beforehand meant the integration mapping (LLMExtender config → S360Reporter config) was understood upfront with no surprises.
- **No regressions**: 230/231 tests passed (1 pre-existing flaky test).

## What Didn't Go Well
- **grep_search missed client.py during LLM-0012 review**: The `search.exclude` settings caused `LLMClient.discover()` to appear missing. This was a false alarm resolved by direct file read, but wasted time.
- **Two LLMConfig types**: S360Reporter's `LLMConfig` and LLMExtender's `LLMConfig` have different field names (`endpoint` vs `base_url`). This is a minor confusion point. Future consolidation could help.

## Action Items
1. **Update `.gitignore` / `search.exclude`**: Ensure `__pycache__` exclusions don't accidentally exclude `.py` files in the same directory hierarchy.
2. **Consider shared config constants**: A future work item could unify the default deployment/API version constants between `llm_client.py` and `ConfigureLLMDialog`.

## Metrics
- Implementation time: single session, no blockers
- Test coverage: 13 new tests, all passing
- Regression: none
