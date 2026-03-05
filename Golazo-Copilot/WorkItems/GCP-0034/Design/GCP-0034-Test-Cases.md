# GCP-0034: Test Cases

1. **WorkItems marker recognized** — `_is_workspace(path)` returns True when `path/WorkItems/` exists
2. **Existing markers still work** — `.git`, `pyproject.toml` etc. still valid
3. **Bootstrap succeeds** — `gcp_bootstrap(workspace_path=dir_with_workitems)` returns success
