# GCP-0077 Test Cases

## TC-1: Azure Tests Removed

- Inspect `test_best_practices.py`.
- Expected: no `TestAzureIdentityBestPractice` class or Azure Identity imports remain.
- Failure: any removed test name or `azure.identity` import remains.

## TC-2: Focused Tests Pass Without Skips

- Run `pytest tests/test_best_practices.py -q` from `golazo-copilot`.
- Expected: all remaining tests pass and zero are skipped.
- Failure: any failure, error, or skip is reported.

## TC-3: Full Suite Passes

- Run the full pytest suite.
- Expected: all tests pass and zero are skipped.
- Failure: any failure, error, or skip is reported.

## TC-4: Version Unchanged

- Inspect the final diff.
- Expected: no package version file is modified.
- Failure: any version metadata change appears.
