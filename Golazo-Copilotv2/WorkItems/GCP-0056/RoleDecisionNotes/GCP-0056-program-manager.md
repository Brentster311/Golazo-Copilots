# GCP-0056 Program Manager Role Notes

## Decisions Made

### 1. Two-action tool design (`check` / `install`)
Chose to split the tool into two discrete actions rather than a single "update" action that does everything. This keeps each invocation idempotent and lets the user (or orchestrating agent) make an informed decision between check and install. The bootstrap step is folded into the install action via a `bootstrap_mode` parameter rather than requiring a third tool call.

### 2. Stdlib-only for network and parsing
Using `urllib.request` and `html.parser` instead of adding `requests` or `httpx` as dependencies. The Simple API response is a trivial HTML page — no need for a full HTTP client library. This avoids adding a runtime dependency to the package.

### 3. `packaging.version` for version classification
Leveraging `packaging.version.Version.is_prerelease` to distinguish stable from pre-release versions. This library is already a transitive dependency (shipped with pip/setuptools) and is the canonical Python approach to PEP 440 version parsing.

### 4. Pre-flight auth checks before install
The tool checks for `keyring`, `artifacts-keyring`, and `az login` status before attempting `pip install`. This avoids cryptic pip authentication errors and provides actionable guidance. The checks use `importlib.util.find_spec` (zero-cost) and `subprocess.run(["az", "account", "show"])` (fast).

### 5. No auto-restart after update
The design explicitly does NOT restart the MCP server process after installation. The tool informs the user that a restart is needed. Auto-restart would be fragile (platform-dependent, could lose state) and is out of scope per the user story's "no auto-updating without consent" constraint.

### 6. No new dependencies
All functionality is implemented with Python stdlib plus `packaging` (transitive). No changes to `pyproject.toml` dependencies are required.

### 7. Bootstrap delegation
Post-install bootstrap reuses the existing `golazo_bootstrap` function directly rather than shelling out. This keeps behavior consistent and testable.

## Assumptions Documented

- The Simple API endpoint at the Azure Artifacts feed returns standard PEP 503 HTML (anchor tags with package filenames).
- `packaging` is available in the runtime environment (it ships with pip and setuptools, which are present in any venv).
- The user's pip is configured to use the same Python environment as the running MCP server (i.e., `sys.executable` can be used to locate the correct pip).
- A server restart is required after update for the new version to take effect — the tool will state this clearly.
- The tool does not need to handle proxy configuration — it inherits from the system/environment settings used by `urllib.request`.

## Risks Flagged

- **Stale process after update**: After `pip install`, the old code is still loaded in memory. The tool must clearly communicate that a restart is needed. This is the highest-impact UX concern.
- **Feed HTML format change**: If Azure Artifacts changes the Simple API response format, parsing could break. Mitigation: the parser is simple and follows PEP 503; format changes are unlikely.
- **Subprocess pip invocation**: Running pip via subprocess is the officially recommended approach (not `pip._internal`), but it adds a child process. Timeout and error handling are critical.
