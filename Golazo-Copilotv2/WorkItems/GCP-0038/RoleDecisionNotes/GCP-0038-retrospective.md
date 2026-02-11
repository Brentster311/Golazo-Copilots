# Retrospective — GCP-0038: Capability Registry Tool

## What Went Well
1. **Clean design-to-implementation flow**: The brainstorming session produced a clear, well-scoped design that translated directly to implementation with zero deviations
2. **TDD discipline**: All 19 tests written first, all failed, then implementation brought them green — no test-after shortcuts
3. **Thorough integration analysis**: Running a subagent to find all integration points caught the V1 vs follow-on distinction early, keeping scope manageable
4. **Good separation of concerns**: The tool is self-contained (one file, no cross-dependencies with existing tools), making it easy to add and test independently
5. **Fixture design**: Reusable YAML fixtures (sample, diamond, circular) covered all dependency graph topologies without redundancy

## What Didn't Go Well
1. **Version bump not propagated to source .md files**: When `__version__` was bumped to 2.100.11, the 11 source `.md` files were not updated. This caused 2 test failures that appeared unrelated to GCP-0038. The tests were checking dynamic version stamping behavior that was removed in GCP-0036 — they needed updating to the new static contract.
2. **Test assertions lagged behind architecture change**: The `test_instructions_version_matches_package` and `test_role_loader_updates_version` tests still expected `__version__` to appear in loaded content, which was the old dynamic stamping behavior. These should have been updated in GCP-0036 itself.

## Action Items
| Action | Owner | Work Item |
|--------|-------|-----------|
| Implement per-file stale version reporting | Developer | GCP-0037 (created) |
| Add version bump checklist to builder role | Process | Consider adding to builder role: "verify source .md files match `__version__` if version was bumped" |
| Update test assertions when removing features | Process | When removing a capability (like dynamic stamping), grep for ALL tests that assert that capability's behavior |

## Metrics
- **Test failures from stale versioning**: Should drop to 0 after GCP-0037
- **Time to diagnose unrelated test failures**: ~5 min this time; should be instant with better version reporting
