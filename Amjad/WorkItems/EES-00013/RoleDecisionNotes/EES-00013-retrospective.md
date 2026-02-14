# EES-00013 Retrospective

## What Went Well

1. **Design-first approach paid off**: The tool schemas, validation rules, and agentic loop were fully specified before code. Implementation followed the design almost exactly — zero deviations documented.

2. **TDD worked smoothly**: 31 tests written first, all failed on old code, all passed on new code without iteration. The mock helper functions (`_tool_call`, `_assistant_msg_with_tools`, `_assistant_msg_done`) made test authoring efficient.

3. **Contract preservation**: `extract()` signature unchanged, `LLMResponse` return type unchanged. 222 existing tests (non-extractor) passed without modification — zero regressions.

4. **Capability impact analysis**: Used `gcp_capabilities` to verify only `fact-extraction` was directly affected. Transitively affected capabilities (`cli-orchestration`, `gui`) needed no changes.

5. **Single-file change**: Only `fact_extractor.py` and its test file changed. Small blast radius, easy rollback.

## What Didn't Go Well

1. **Session continuity**: Workflow started in a prior session, required resumption. The conversation summary mechanism handled this well, but note that token budget was exceeded before PM design doc was created — requiring a new response to continue.

2. **`Capability-Impact.md` gate surprise**: Architect transition failed because `Capability-Impact.md` wasn't listed in the design doc's required outputs but was required by the Golazo gate. Quickly resolved by creating the file.

## Action Items

1. **Document `Capability-Impact.md` requirement**: Architect role requires this file but it's not obvious in the PM design doc template. Consider adding it to the PM role's required outputs or at least noting it in the architect role docs. (Low priority — single-occurrence friction.)

## Metrics

- **Time to implement**: 1 session (from PM design through retrospective)
- **Tests**: 31 new, 253 total, 0 regressions
- **Deviations from design**: 0
- **Golazo gate failures**: 1 (Capability-Impact.md — resolved immediately)
