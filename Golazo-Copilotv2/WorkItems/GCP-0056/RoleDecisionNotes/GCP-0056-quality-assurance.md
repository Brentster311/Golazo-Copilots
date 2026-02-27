# GCP-0056 Quality Assurance Role Notes

## Decisions Made

### 1. Flagged bootstrap_mode as a critical design inconsistency (RC-2)

The design allows `bootstrap_mode="standard"` or `"full"` to be passed alongside `action="install"`, which would invoke `golazo_bootstrap` on the stale (pre-update) code still loaded in memory. This contradicts the design's own statement that the MCP server must be restarted before bootstrap works. Elevated this to a critical issue requiring resolution before development. The recommended fix is to make bootstrap a separate post-restart step only.

### 2. Required explicit return dict schemas (RC-13)

The design mentions returning dicts but never defines the keys. Without a defined contract, the formatter (`format_update_result`) cannot be implemented correctly, and test assertions would be arbitrary. Required the design to specify exact keys for check results, install success, install failure, and error responses.

### 3. Comprehensive error path coverage

Prioritized error path testing based on the domain expert's recommendation. Created 10 error/edge-case test cases (TC-05 through TC-08, TC-11, TC-13, TC-14, TC-16, TC-17, TC-27) covering network failures, auth failures, missing packages, malformed input, and pip failures. These represent the most likely real-world failure modes.

### 4. Version parsing edge cases

Added test cases for PEP 440 edge cases (TC-26, TC-29) including post-release, dev, local versions, and `InvalidVersion` strings. The domain expert noted that `packaging.version.Version` raises `InvalidVersion` for non-PEP-440 strings — the implementation must catch this gracefully.

### 5. Accepted TC-20 as a design ambiguity

When the user has a pre-release installed (e.g., 2.111.0a1) and the latest stable is 2.110.0, the `update_available` flag behavior is ambiguous. Is the user "up to date" because they have a newer pre-release, or should they be offered the stable version? Flagged this as needing a design decision — did not prescribe the answer, but ensured a test case exists to verify whichever behavior is chosen.

### 6. Test strategy uses mocking throughout

All test cases mock external dependencies (`urllib.request`, `subprocess.run`, `importlib.metadata.version`, `importlib.util.find_spec`). No test case should make real network calls or real pip installs. This is consistent with the existing Golazo test patterns.

## Assumptions

- The `packaging` library will be available at test time (it is a transitive dependency and is present in the dev environment).
- Tests will use `pytest` and `pytest-asyncio`, consistent with the existing test suite.
- The `golazo_bootstrap` function signature is stable and can be mocked without change.
- The test framework supports `unittest.mock.patch` for all stdlib modules used by the tool.

## Review Summary

- **Critical issues found:** 3 (RC-1, RC-2, RC-3) — all are resolvable without redesign
- **Major issues found:** 4 (RC-4 through RC-7) — improve robustness
- **Minor issues found:** 4 (RC-8 through RC-11) — acceptable for v1 with documentation
- **Test cases created:** 33, covering all 6 acceptance criteria
- **All acceptance criteria have at least 2 test cases** (happy path + error/edge case)

## Recommendations for Downstream Roles

- **Architect:** Resolve RC-2 (bootstrap_mode timing) and RC-12 (post-install flow ambiguity) before proceeding. Define the return dict schema (RC-13).
- **Developer:** Implement `InvalidVersion` handling (TC-29), `PackageNotFoundError` handling (TC-08), and `FileNotFoundError` for missing `az` CLI (TC-17). These are commonly missed error paths.
- **Refactor Expert:** No structural concerns — the tool follows existing patterns. Focus on ensuring the version parsing logic is extracted into a testable helper function.

