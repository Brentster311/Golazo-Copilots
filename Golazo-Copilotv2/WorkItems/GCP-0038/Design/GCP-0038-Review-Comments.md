# GCP-0038 — Review Comments

## QA Review
Approved with minor observations.

### Design Quality
- Clean separation of concerns: YAML parsing, graph traversal, and output formatting are distinct responsibilities
- File matching strategy (suffix match) is reasonable — handles both absolute and relative paths

### Edge Cases to Cover
1. **Empty `capabilities.yaml`** — file exists but `capabilities:` is empty list or null
2. **Duplicate capability names** — undefined behavior unless validated
3. **`depends_on` references non-existent capability** — should this be caught by `validate`?
4. **`impact` with files that match zero capabilities** — should return empty, not error
5. **`show` with non-existent capability name** — clear error message
6. **Large dependency chains** — the BFS cycle detection handles this, but test with a diamond pattern (A→B→D, A→C→D)

### Observation
The design doc says "suffix matching" for file paths. Recommend also supporting exact match as first priority, falling back to suffix match. This prevents false positives (e.g., `utils.py` matching both `src/utils.py` and `tests/utils.py`).

## Architect Notes
- **Dependency**: PyYAML is a safe choice — pure Python fallback, no C extension required, MIT licensed. Widely used. Acceptable new dependency.
- **Security**: `yaml.safe_load()` must be used (not `yaml.load()`) to prevent arbitrary code execution from malicious YAML. Design doc should be explicit about this.
- **File matching**: Agree with QA — exact match first, suffix fallback. Normalize path separators (`/` vs `\`) before comparison for cross-platform correctness.
- **Workspace resolution**: Tool needs `workspace_path` to find `capabilities.yaml`. Follow existing pattern from other tools — resolve via `resolve_work_items_dir` parent or accept explicit path.
- **Encoding**: `capabilities.yaml` should be read as UTF-8 explicitly (same as all other file reads in GCP).
- **No architectural concerns** — this is a read-only query tool with zero side effects. Blast radius is zero; rollback is removing the tool.
