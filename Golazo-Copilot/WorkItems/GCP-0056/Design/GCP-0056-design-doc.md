# GCP-0056 Design Document — Golazo Update Checker Tool

## Summary

Add a new MCP tool `golazo_update` that checks the Azure Artifacts feed for newer versions of `golazo-copilot`, reports version information to the user, and orchestrates the install + optional bootstrap flow — all within the existing Golazo MCP server architecture.

## Problem Statement

Users currently have no in-workflow way to discover or install newer versions of Golazo Copilot. They must manually check the Azure Artifacts feed, remember the `--index-url` parameter, ensure auth dependencies are installed, and know to re-bootstrap after updating. This friction causes users to run stale versions and miss improvements.

## Business Case

| Dimension | Detail |
|-----------|--------|
| **Why now** | Golazo is iterating rapidly (v2.110+). Users on older versions encounter bugs already fixed or miss new capabilities, generating avoidable support requests. |
| **Impact** | Reduces "works on my machine" version skew across the team; shortens time-to-adoption for new features. |
| **KPIs** | (1) Reduction in support tickets related to stale versions. (2) Average lag between release and user adoption (target: < 1 day for active users). |

## Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| **Golazo users** | Stay current without leaving their IDE workflow. |
| **Golazo maintainers** | Fewer version-mismatch bug reports; faster rollout of fixes. |
| **Azure Artifacts feed owners** | No change — read-only consumer of the existing feed. |

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | The tool queries the Azure Artifacts feed Simple API for available versions of `golazo-copilot`. |
| FR-2 | The tool reports: (a) currently installed version, (b) latest stable (non-pre-release) version, (c) latest pre-release version (if different from stable). |
| FR-3 | If the installed version equals the latest, the tool informs the user and takes no further action. |
| FR-4 | If a newer version exists, the tool presents the user with a choice: install latest stable, install latest pre-release, or cancel. |
| FR-5 | Before installing, the tool verifies that `keyring` and `artifacts-keyring` are importable. If not, it reports the missing packages and provides the install command. |
| FR-6 | Before installing, the tool checks that `az login` credentials are available (e.g., via `az account show`). If not, it instructs the user to run `az login`. |
| FR-7 | Installation uses `pip install golazo-copilot==<version> --index-url=<feed-url>`. |
| FR-8 | After successful installation, the tool informs the user that the MCP server must be refreshed/restarted before the new version takes effect. Bootstrap will not work until this refresh occurs. The tool then presents the post-install bootstrap choice: (1) Do not bootstrap, (2) Bootstrap, (3) Full clean bootstrap (force + include_roles). If the user selects option 2 or 3, the tool invokes `golazo_bootstrap` with appropriate parameters. |
| FR-9 | The tool returns structured results (dict) that the server formats for display, consistent with all other Golazo tools. |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Version check completes in < 10 seconds on a healthy network. |
| NFR-2 | The tool must not store, log, or expose credentials. Auth is delegated to `az login` + `keyring`/`artifacts-keyring`. |
| NFR-3 | The tool must work on Windows (primary), macOS, and Linux. |
| NFR-4 | The tool must degrade gracefully if the feed is unreachable (clear error message, no crash). |
| NFR-5 | The tool does not auto-update without explicit user consent. |

## Proposed Approach (High Level)

### New file: `golazo-copilot/src/golazo_copilot/tools/golazo_update.py`

The tool module exposes an async function `golazo_update(action, version, workspace_path)` with three logical phases:

1. **Check phase** (`action="check"`):
   - Read the currently installed version via `importlib.metadata.version("golazo-copilot")`.
   - Fetch the Simple API page for `golazo-copilot` from the Azure Artifacts feed using `urllib.request` (stdlib — no new dependency).
   - Parse the HTML to extract all available versions (anchor tags with `href` containing version numbers).
   - Classify versions into stable vs. pre-release using `packaging.version.Version` (already a transitive dependency via pip/setuptools).
   - Return a dict with `current_version`, `latest_stable`, `latest_prerelease`, and `update_available`.

2. **Install phase** (`action="install"`, `version=<target>`):
   - Pre-flight: verify `keyring` and `artifacts-keyring` are importable; verify `az account show` succeeds.
   - Run `pip install golazo-copilot==<version> --index-url=<feed-url>` via `subprocess.run`.
   - Verify the installed version matches the target.
   - Return success/failure dict.

3. **Bootstrap phase** (post-install, delegated):
   - This is handled by returning a status indicating install success plus bootstrap options. The MCP server or the user then invokes `golazo_bootstrap` as a separate tool call.
   - Alternatively, the tool can accept `bootstrap_mode` parameter ("none", "standard", "full") and invoke `golazo_bootstrap` internally.

### Server registration

- Import `golazo_update` in `server.py`.
- Add a `Tool` entry in `list_tools()` with an `inputSchema` describing the `action`, `version`, and `workspace_path` parameters.
- Add a `format_update_result()` formatter.
- Add dispatch logic in `_dispatch_tool()`.

### MCP Tool Schema

```json
{
  "name": "golazo_update",
  "description": "Check for and install updates to Golazo Copilot from Azure Artifacts.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["check", "install"],
        "description": "check = report versions; install = install a specific version"
      },
      "version": {
        "type": "string",
        "description": "Target version to install (required when action=install)"
      },
      "bootstrap_mode": {
        "type": "string",
        "enum": ["none", "standard", "full"],
        "default": "none",
        "description": "Post-install bootstrap behavior"
      },
      "workspace_path": {
        "type": "string",
        "description": "Workspace root path (required)"
      }
    },
    "required": ["action", "workspace_path"]
  }
}
```

### Version parsing strategy

Use the [PEP 503 Simple Repository API](https://peps.python.org/pep-0503/) response format. The feed returns an HTML page with `<a href="...">golazo-copilot-X.Y.Z.tar.gz</a>` links. Parse with `html.parser.HTMLParser` (stdlib). Extract version strings using a regex on filenames. Classify using `packaging.version.Version.is_prerelease`.

### Authentication check strategy

- **keyring / artifacts-keyring**: Attempt `importlib.util.find_spec("keyring")` and `importlib.util.find_spec("artifacts_keyring")`. If either is `None`, return an error dict with the exact pip install command.
- **az login**: Run `subprocess.run(["az", "account", "show"], capture_output=True, timeout=10)`. If the return code is non-zero, return an error dict instructing the user to run `az login`.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| **Separate CLI command** | Breaks the MCP-only pattern; users would need to leave their IDE. |
| **Use `pip index versions`** | Requires pip >= 21.2, and the command's output format is not stable. Also doesn't handle Azure Artifacts auth as cleanly. |
| **Use `requests` library** | Would add a new runtime dependency. `urllib.request` via stdlib is sufficient for a single HTML page fetch. |
| **Auto-check on every `golazo_status` call** | Violates the "only when explicitly requested" constraint; adds latency to the most-used tool. |
| **Use PyPI JSON API** | Azure Artifacts doesn't support the PyPI JSON API — only the Simple API. |

## Risks, Mitigations, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Azure Artifacts feed is unreachable | Low | Medium | Return a clear error message; do not block other tool functionality. Timeout after 10 seconds. |
| `pip install` fails mid-update | Low | High | The previous version remains importable until the process restarts. The tool reports the failure and the user can retry. |
| `packaging` module not available | Very Low | Medium | `packaging` is a transitive dep of pip/setuptools. Fall back to string comparison if truly unavailable. |
| `az login` session expired | Medium | Low | Pre-flight check catches this before attempting install. Clear guidance provided. |
| User runs update in a venv where golazo-copilot is not editable-installed | Low | Medium | `pip install` handles both editable and non-editable installs. Document that the MCP server must be restarted after update. |

### Open Questions

1. **Should the tool restart the MCP server after update?** — Assumption: No. The user restarts VS Code or the MCP process. The tool should inform the user that a restart is needed for the new version to take effect.
2. **Should we pin `keyring`/`artifacts-keyring` versions?** — Assumption: No. Any version that satisfies Azure Artifacts auth is acceptable.
3. **Should we support installing from a local wheel?** — Assumption: Out of scope for initial implementation.

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| `urllib.request` | Stdlib | For fetching the Simple API page |
| `html.parser` | Stdlib | For parsing PEP 503 HTML |
| `subprocess` | Stdlib | For running `pip install` and `az account show` |
| `importlib.metadata` | Stdlib | For reading currently installed version |
| `importlib.util` | Stdlib | For checking if `keyring`/`artifacts-keyring` are installed |
| `packaging.version` | Transitive (via pip) | For version parsing and pre-release classification |
| `golazo_bootstrap` | Internal | Post-install bootstrap (existing tool) |

No new third-party dependencies are required.

## Migration / Rollout / Rollback Plan

### Rollout

1. Implement `golazo_update.py` as a new tool module.
2. Register in `server.py` (import, list_tools, dispatch).
3. Export from `tools/__init__.py`.
4. Add tests.
5. Bump version in `pyproject.toml`.
6. Publish to Azure Artifacts feed.

### Rollback

The tool is purely additive — no existing behavior is modified. To roll back:
- Remove the import, tool registration, and dispatch block from `server.py`.
- Remove the export from `tools/__init__.py`.
- Delete `golazo_update.py`.
- Republish.

No data migration is involved. No state files are created or modified by this tool.

## Observability Plan

| Signal | Mechanism |
|--------|-----------|
| Tool invocation | Standard MCP tool call logging (already exists in the server framework). |
| Version check result | Returned in the tool response (visible in chat). |
| Install success/failure | Returned in the tool response with exit code and stderr if applicable. |
| Network errors | Caught and returned as error dict with description. |

No custom telemetry or metrics are required for the initial implementation (per user story).

## Test Strategy Summary

| Test Type | Coverage |
|-----------|----------|
| **Unit — version parsing** | Feed HTML parsing extracts correct versions; pre-release classification works; "latest" calculation is correct. |
| **Unit — auth checks** | `find_spec` returns None → correct error; subprocess returns non-zero → correct error. |
| **Unit — result formatting** | `format_update_result()` produces expected display text for each scenario (up-to-date, update-available, error). |
| **Integration — check action** | Mock the HTTP response; verify end-to-end flow returns correct version comparison. |
| **Integration — install action** | Mock subprocess; verify correct pip command is constructed; verify bootstrap delegation. |
| **Edge cases** | Empty feed response; malformed HTML; no network; `packaging` unavailable; version already installed. |

Tests will follow the existing pattern in `golazo-copilot/tests/` using `pytest` and `pytest-asyncio`.
