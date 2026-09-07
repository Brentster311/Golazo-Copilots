# GCP-0076 Quality Assurance Decision Notes

## Coverage Decision

Test path resolution through public tool behavior rather than only constants. Pair temporary-workspace tests with one repository-layout policy test so both reusable behavior and this repository's cleanup remain protected.

## Acceptance Mapping

- AC1: bootstrap, create-work-item, status, and list integration tests.
- AC2: legacy migration, coexistence, malformed canonical, and read-only status tests.
- AC3: schema, validation, and representative impact tests against the real registry.
- AC4: scoped repository-layout assertions.
- AC5: focused regressions followed by full pytest and Ruff.

## Reliability

No test may depend on global user files. Temporary paths isolate migration behavior, and the real-registry test resolves from the checked-out repository root.
