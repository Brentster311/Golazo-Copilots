# EES-00005 — QA Decision Notes

## Review Approach
Focused on feasibility of automating GUI tests, thread safety, and data consistency between GUI and CLI.

## Key Decisions
1. **Test strategy split:** 14 unit tests (adapters + workers, no Tk dependency), 2 integration, 8 manual. This balances TDD requirement with GUI testing realities.
2. **Adapter pattern:** GUI panels use adapter functions to convert models → display data. These adapters are the test seam — fully automatable without Tk.
3. **Worker thread testing:** Workers are testable in isolation (they take inputs and produce results via queue/callback).

## Conditional Items
- MJ-1: Fact editing approach needs architect decision (dialog vs inline)
- MJ-2: Test automation scope confirmed — adapters and workers are automated, widget interaction is manual
