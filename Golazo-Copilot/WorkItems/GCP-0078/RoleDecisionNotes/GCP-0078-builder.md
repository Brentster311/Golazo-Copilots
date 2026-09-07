# GCP-0078 Builder Notes

## Build Verification

- Focused README and release-policy tests: 14 passed.
- Full functional suite under coverage, excluding the strict wall-clock performance test: 556 passed, 1 deselected, 89% total coverage, minimum module coverage 74%.
- Performance test without coverage tracing: 1 passed.
- Ruff: all checks passed.
- Wheel build: `golazo_copilot-6.0.4-py3-none-any.whl` built successfully.

One full-suite attempt encountered a transient Windows file-lock teardown error in `test_gcp_transition.py`; reruns completed all test bodies, and the split coverage/performance validation passed cleanly.

## Release Metadata

- Previous version: 6.0.3.
- New version: 6.0.4.
- Rationale: patch release correcting inaccurate and incomplete public documentation without changing runtime APIs.
- `pyproject.toml` and the newest README changelog entry both use 6.0.4.

## Capability Registry

Validation passed for all five registered capabilities. Impact analysis identified `release-policy-guidance`; no capability registry update is needed because no public function or runtime contract was introduced.