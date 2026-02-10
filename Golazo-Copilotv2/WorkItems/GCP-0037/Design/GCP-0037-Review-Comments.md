# Review Comments — GCP-0037

## Design Review
- **Approved**. Single-function replacement with clear algorithm.
- Note: The `_VERSION_PATTERN` regex is already defined and reusable — good.
- Note: `importlib.resources` is already imported in `loader.py` but `gcp_status.py` will need its own import for source file reading.
- Suggestion: Extract a `_get_source_version(source_resource_path)` helper for reading source file versions via `importlib.resources` to keep `_get_stale_files` clean.
- Edge case: `TechBestPractices.md` has a version comment now (was updated in the 2.101.0 bump), so it should be included in stale checking like any other file.

## Architect Notes
- **Approved**. Minimal scope, single-file change, no new dependencies.
- Use `importlib.resources` consistently (already the pattern in `loader.py` and `gcp_bootstrap.py`).
- Encoding: Ensure `read_text(encoding="utf-8")` on both deployed and source reads.
- Error handling: Wrap source reads in try/except — a corrupted package install shouldn't crash `gcp_status`.
- The file mapping (deployed → source) should be a constant, not inline — makes future additions (like `capabilities.yaml` from GCP-0040) easy to add.
