# GCP-0052 Retrospective

## What Went Well
- **Domain expert review paid off** — The 6 discrepancies identified in the handoff matrix (zero-bridge transitions, reach-back patterns) made the final protocol document significantly more accurate than the initial design doc's matrix.
- **TDD caught real issues** — 4 test failures in the first run surfaced: workspace-root vs work-item-relative path resolution, Pydantic model attribute access (not dict subscripting), role notes requirement before backward transitions, and the POA closure comment edge case.
- **Subagent delegation** — PM, DE, QA, and Architect roles were effectively delegated to subagents, producing good artifacts with minimal iteration.
- **Fast test execution** — 20 integration tests run in 0.56s (NFR target < 10s), no real I/O beyond temp directories.

## What Didn't Go Well
- **REQUIRED_OUTPUTS path resolution** — First pass used work-item-relative paths, but the output validator resolves from workspace root. Required a full rewrite of the constant. Should have read the `output_validator.py` path resolution code before writing tests.
- **POA closure comment still a friction point** — The `<!-- Only during Closure re-entry -->` inline HTML comment in POA's Required Outputs is parsed as part of the file path. This has now caused workarounds in GCP-0050, GCP-0052, and every real workflow run. It should be fixed upstream.

## Action Items
1. **Fix POA closure comment** — New work item: strip inline HTML comments in `parse_required_outputs()` or move the closure file to a conditional output. This affects every work item's POA transition.
2. **Document Pydantic model access** — Add a note in TechBestPractices.md that `load_state()` returns a Pydantic model (attribute access), not a dict. This tripped up test writing.
3. **Add path resolution examples to TechBestPractices.md** — Document that output validation resolves `workspace_root / pattern` and `gcp_role_context` resolves `project_root / pattern` for `WorkItems/` prefixed paths.

## Metrics
- Test count: 371 → 391 (+20)
- Integration test time: 0.56s
- Handoff protocol: 115 lines (58% of 200-line budget)
- TDD iterations: 2 (first run: 4 failures, second run: 3 failures, third run: 0)
