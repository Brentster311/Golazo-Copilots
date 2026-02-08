# GCP-0025: Retrospective Role Notes

## What Went Well

1. **Clean Phase Separation**: Breaking the work into Phase 1 (output_validator.py) and Phase 2 (integration) made the implementation manageable and testable.

2. **Test-First Development**: Writing 20 unit tests for the validator before implementing the integration caught edge cases early (like HTML comments in Required Outputs sections).

3. **Backward Compatibility**: The decision to only parse lines with explicit type prefixes (`file:`, `dir:`, `git-branch:`, `git-log:`) means existing role files continue to work without modification.

4. **Integration Tests**: The 6 integration tests validated the complete flow (transition succeeds/fails, force with/without consent, status output).

5. **Isolated Test Workspaces**: Using `tests/test-workspace/` for integration tests prevented interference with other tests.

## What Didn't Go Well

1. **Leftover Test Files**: A `.github/roles/` directory was left in `tests/` from a previous run, causing 24 tests to fail unexpectedly. This was a debugging distraction.

2. **Phase 3 Deferred**: Removing `gcp_mark_dor` and `gcp_mark_dod` was part of the original user story but deferred. The feature is incomplete without this.

3. **Default Role Files Not Updated**: The package defaults still use the old format without `file:` prefixes. They need to be updated for the new validation to work out of the box.

## Action Items

1. **Add .gitignore for test artifacts**: Add patterns to prevent accidental commits of test workspace files:
   ```
   tests/.github/
   tests/test-workspace/
   tests/test-workitems-debug*/
   ```

2. **Create GCP-0026**: Update all default role files to use new Required Outputs format with `file:`, `dir:` prefixes.

3. **Create GCP-0027**: Remove `gcp_mark_dor` and `gcp_mark_dod` tools (Phase 3 of this work item).

4. **Consider test cleanup fixture**: Add a conftest.py fixture that ensures `tests/.github/` doesn't exist at test start to prevent cross-test contamination.

## Metrics

- **Before**: gcp_mark_dor/dod required evidence parameter + 12 validation rules
- **After**: Role files define outputs, validation is automatic on transition
- **Test Count**: 139 → 165 tests (+26 tests for output validation)
- **Build Time**: ~1.2 seconds (no regression)

## Decision

GCP-0025 is complete for Phase 1 & 2. Phase 3 (removal of gcp_mark_dor/dod) to be tracked as separate work item GCP-0027.
