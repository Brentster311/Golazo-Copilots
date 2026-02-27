# SFI-021 Retrospective

## What Went Well

1. **TDD cycle worked cleanly**: Tests were written first, confirmed failing (7 failed/2 passed), then production code was written to make all 9 pass. Full suite of 188 tests remained green throughout.
2. **Design doc was solid**: The design document accurately mapped to implementation — 6 URL fields, `ThreadPoolExecutor(max_workers=6)`, `timeout=10`, `max_length=1500`, `ProviderError` catch. No surprises during implementation.
3. **Existing `url_content` parameter**: `build_prompt()` and `analyze_item()` already had `url_content` parameter support from SFI-020 design. This made integration seamless.
4. **llm-extender library**: `fetch_url()` worked as expected with HTML stripping, timeouts, and `ProviderError` exceptions. Clean integration.

## What Didn't Go Well

1. **`_format_item_for_prompt` function lost during edit**: When adding `fetch_action_item_urls()` above `_format_item_for_prompt`, the function definition line (`def _format_item_for_prompt(item: dict) -> str:`) was accidentally dropped — its body was concatenated under the `return results` of the new function. Caught immediately by the test collection error. Root cause: the replacement `oldString` included `def _format_item_for_prompt(item: dict) -> str:` in the match but the `newString` replacement stopped at the line above.
2. **Working directory confusion with git**: `git add .` from S360Reporter subdirectory didn't stage WorkItems files (at parent level). Had to use `git add -A` from repo root.

## Action Items

1. **Verify function boundaries after edits**: When inserting new code between existing functions, always verify that both the preceding and following function definitions are intact by running a quick grep or read.
2. **Always `cd` to repo root for git operations**: Ensure `git add` and `git commit` are run from `c:\repos\Golazo-Copilots\SFIAgent`, not from a subdirectory.

## Metrics

- 9 new tests added, all passing
- 0 regressions in existing 179 tests (+ 1 skipped)
- 1 edit fix required (lost function definition)
- Total SFI-021 implementation: 4 production files changed, ~100 lines of new code
