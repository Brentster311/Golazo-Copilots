# SFI-030 Retrospective

## What Went Well

1. **Clean module separation**: The dependency layering (models → formatters → services → dialogs → app) was designed up front and worked without circular import issues
2. **Backward compatibility**: The re-export shim approach meant zero changes needed in external consumers (tests, query_builder, diagnostic scripts)
3. **Incremental creation**: Building modules bottom-up (models first, app last) meant each module could be validated against its dependencies
4. **Test coverage caught issues**: The existing test suite immediately surfaced the mock-patch targeting problem

## What Didn't Go Well

1. **Emoji encoding**: The `create_file` tool converted emoji characters to `\U0001f534` Unicode escapes. Tests using `inspect.getsource()` check literal source text, so this broke 5 tests. Required a separate Python script to fix byte-level encoding.
2. **Mock patch targets**: Tests that `patch("sfi_reporter.tk_app._load_setting")` stopped working because the function now lives in `sfi_reporter.services` and is imported into `sfi_reporter.dialogs`. This is an inherent limitation of Python mock patching — you must patch where the name is looked up, not where it's defined. Required updating 19 patch targets in `test_sfi_025.py`.
3. **Express profile was appropriate** but the work item had many gate artifacts to produce.

## Action Items

1. **Document mock-patch convention**: When refactoring moves functions between modules, all `patch("old.path.func")` calls must be updated to the new lookup path. Add this as a note in TechBestPractices.
2. **Emoji handling note**: When using `create_file` for source containing emoji literals, verify the output file contains the actual characters, not escape sequences.

## Metrics

- Before: 1 file, 3,813 lines
- After: 6 files, ~2,820 lines total (25% reduction via removing blank lines/comments in extraction + shim)
- Tests: 0 new failures introduced
- Mock patches updated: 19
