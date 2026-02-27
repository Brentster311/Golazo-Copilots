# GCP-0056 Review Comments — Golazo Update Checker Tool

## Overall Assessment

The design is **well-structured and feasible**. The three-phase approach (check → install → bootstrap) is clean, the stdlib-only dependency strategy is sound, and the auth pre-flight checks are a good UX decision. The design follows existing Golazo tool patterns correctly.

Several issues and gaps are identified below, organized by severity.

---

## Critical Issues

### RC-1: `version` parameter not required when `action="install"`

The MCP tool schema shows `version` as optional, but the install phase requires a target version. If a caller sends `{"action": "install", "workspace_path": "/foo"}` without specifying `version`, the tool behavior is undefined.

**Recommendation:** Either (a) validate at dispatch time that `version` is present when `action="install"` and return a clear error, or (b) default to installing the latest stable version if `version` is omitted. Document whichever approach is chosen.

### RC-2: `bootstrap_mode` triggers bootstrap on a stale process

The design says bootstrap can be invoked as part of the install action via `bootstrap_mode`. However, the design also states that the MCP server must be restarted before bootstrap works correctly. If `bootstrap_mode="standard"` or `"full"` is passed with an install action, the bootstrap would run against the OLD code still loaded in memory.

**Recommendation:** The install action should NEVER invoke bootstrap directly. It should return a message telling the user to restart, and then the user invokes `golazo_bootstrap` as a separate tool call after restart. The `bootstrap_mode` parameter should either be removed from the schema or only accepted as a separate post-restart action. This is the most significant design inconsistency.

### RC-3: No error handling for `urllib.request` failures

The design mentions a 10-second timeout NFR and "degrade gracefully if feed is unreachable," but does not specify how `urllib.request.urlopen` errors are caught. Possible failures include: `URLError` (DNS failure, connection refused), `HTTPError` (401/403 auth required, 404 feed not found, 500 server error), socket timeout.

**Recommendation:** Document the exception handling strategy. At minimum: catch `urllib.error.URLError` and `urllib.error.HTTPError`, extract the status code/reason, and return a structured error dict. Set `timeout=10` on the `urlopen` call.

---

## Major Issues

### RC-4: Race condition — concurrent updates

If two VS Code windows or users share the same venv, concurrent `pip install` invocations could corrupt the environment. The design does not mention any locking mechanism.

**Recommendation:** This is an edge case but worth noting. At minimum, document that concurrent updates to the same environment are unsupported. Consider checking for a pip lock file or using `--no-cache-dir` to reduce conflict surface.

### RC-5: `sys.executable` may not match the MCP server's Python

The domain expert notes correctly flag using `sys.executable` for pip. However, if the MCP server is launched via a script or wrapper (e.g., `npx` → Node → Python subprocess), `sys.executable` might point to a different Python than the one running the server.

**Recommendation:** Add a sanity check that `sys.executable` resolves to the same environment that `importlib.metadata.version("golazo-copilot")` reads from. Or explicitly document the assumption that `sys.executable` is the correct interpreter.

### RC-6: Missing error path for `importlib.metadata.PackageNotFoundError`

If `golazo-copilot` is not installed at all (e.g., running from source in editable mode with a different package name), `importlib.metadata.version("golazo-copilot")` raises `PackageNotFoundError`. The design does not address this.

**Recommendation:** Catch `PackageNotFoundError` and return a clear error indicating the package is not installed in the current environment, with guidance on how to install it.

### RC-7: HTML parsing robustness

The design relies on parsing `<a href="...">` tags from the Simple API response. Azure Artifacts may include `data-requires-python` attributes or other metadata. The parser should extract versions from the `href` attribute (filename), not the anchor text, and handle all PEP 503 normalization (underscores vs hyphens, `.tar.gz` vs `.whl` vs `.zip`).

**Recommendation:** Explicitly specify the regex for extracting version from filenames. Test with both `.tar.gz` and `.whl` filenames, and with normalized/unnormalized package names (e.g., `golazo_copilot` vs `golazo-copilot`).

---

## Minor Issues

### RC-8: `az` command not found on PATH

The design assumes `az` (Azure CLI) is on the system PATH. On some systems, `az` may be installed but not on PATH, or may be named differently (e.g., `az.cmd` on Windows).

**Recommendation:** Use `shutil.which("az")` to check for `az` availability before running `az account show`. On Windows, also check for `az.cmd`. Return a clear error if not found.

### RC-9: No progress indication for long-running pip install

`pip install` can take 10–30 seconds depending on package size and network speed. The tool returns only after completion, giving no intermediate feedback.

**Recommendation:** This is acceptable for v1 but document it as a known UX limitation. Future enhancement could stream subprocess output.

### RC-10: Version comparison edge case — dev/local versions

If the user has an editable install or a local dev version (e.g., `2.110.0.dev1`), the version comparison logic may produce unexpected results (e.g., reporting that an update is available to `2.110.0` when the user intentionally has a dev version).

**Recommendation:** Document that dev/local versions are treated as pre-release by `packaging.version` and that the tool will suggest updating to the latest stable. Consider adding a flag to skip the update check for dev installs.

### RC-11: Feed URL hardcoded

The Azure Artifacts feed URL is hardcoded in the design. If the feed URL changes or a team uses a different feed, the tool breaks.

**Recommendation:** Acceptable for v1 as the feed URL is stable and shared across the team. Consider extracting it to a constant at the top of the module for easy modification.

---

## Clarity / Documentation Gaps

### RC-12: Post-install flow ambiguity

The design describes two alternatives for bootstrap: (a) return status and let the user invoke `golazo_bootstrap` separately, or (b) accept `bootstrap_mode` and invoke internally. The design doc says "Alternatively" but does not pick one. The schema includes `bootstrap_mode`, suggesting option (b) was chosen — but this contradicts the restart requirement (see RC-2).

**Recommendation:** Resolve the ambiguity. The recommended approach is option (a): the tool returns an install-success result with a message about restart and bootstrap options. Bootstrap is a separate user-initiated step after restart.

### RC-13: No specification of the return dict structure

The design mentions "return a dict" for each phase but does not define the dict keys or structure. The formatter (`format_update_result`) needs a defined contract.

**Recommendation:** Define the return dict schema for each action. Example:
- Check: `{"action": "check", "current_version": "2.109.0", "latest_stable": "2.110.0", "latest_prerelease": "2.111.0a1", "update_available": true}`
- Install success: `{"action": "install", "version": "2.110.0", "success": true, "message": "..."}`
- Install failure: `{"action": "install", "version": "2.110.0", "success": false, "error": "..."}`

---

## Positive Observations

- **Stdlib-only**: Excellent decision to avoid adding runtime dependencies for a simple HTTP + HTML parse operation.
- **Pre-flight auth checks**: Checking for `keyring`, `artifacts-keyring`, and `az login` before attempting install is a great UX pattern that prevents cryptic pip errors.
- **Separation of check and install**: The two-action design is idempotent and composable. The check action is non-destructive.
- **Follows existing patterns**: The tool module structure, server registration, and formatter pattern are consistent with all other Golazo tools.
- **Rollback simplicity**: Purely additive; no existing behavior modified.

---

## Architect Notes

### Architectural Alignment

The `golazo_update` tool follows the established Golazo tool pattern exactly: a standalone async function in `tools/golazo_update.py`, registered via import + `Tool` entry + dispatch case + formatter in `server.py`, and re-exported from `tools/__init__.py`. This is the eighth tool following this pattern (after create_workitem, transition, status, bootstrap, consent, capabilities, role_context). **No new architectural patterns are introduced.**

### Design Decisions & Resolutions

#### D-1: Remove `bootstrap_mode` from the schema (resolves RC-2 & RC-12)

**Decision:** The `bootstrap_mode` parameter MUST be removed from the `golazo_update` MCP tool schema entirely. Bootstrap after update is a **separate user-initiated step** that occurs after the MCP server is restarted.

**Rationale:** Running `golazo_bootstrap` from within the install action would execute against the OLD code still loaded in memory. The MCP server process must be restarted for the new package code to take effect. Post-restart, the user calls `golazo_bootstrap` directly — this is an existing, tested tool that requires no wrapper.

**Revised schema:** Two parameters only — `action` (enum: "check", "install") and `version` (string, required when action="install"). Plus the standard `workspace_path`.

**Post-install response contract:** The install-success result dict MUST include a `restart_required: true` field and a `message` field with explicit instructions:
1. Restart/refresh the MCP server
2. After restart, optionally call `golazo_bootstrap` or `golazo_bootstrap(force=True, include_roles=True)` for a full refresh

#### D-2: Require `version` on install action (resolves RC-1)

**Decision:** Validate at dispatch time that `version` is present when `action="install"`. Return a structured error if missing. Do NOT default to "latest" — the check action provides the version information, and the user (or LLM) makes the explicit choice.

**Rationale:** Keeps the tool composable and idempotent. The two-step flow (check → install) is cleaner than a single "install latest" action that hides which version is being installed.

#### D-3: Define return dict contracts (resolves RC-13)

**Check result:**
```json
{
  "action": "check",
  "current_version": "2.109.0",
  "latest_stable": "2.110.0",
  "latest_prerelease": "2.111.0a1",
  "update_available": true,
  "message": "Update available: 2.109.0 → 2.110.0"
}
```

**Install success:**
```json
{
  "action": "install",
  "version": "2.110.0",
  "previous_version": "2.109.0",
  "success": true,
  "restart_required": true,
  "message": "golazo-copilot 2.110.0 installed. Restart the MCP server, then optionally run golazo_bootstrap."
}
```

**Install failure:**
```json
{
  "action": "install",
  "version": "2.110.0",
  "success": false,
  "error": "<pip stderr or pre-flight failure description>"
}
```

**Error (network, auth, not installed):**
```json
{
  "error": "<descriptive message>",
  "error_type": "network|auth|not_installed|validation"
}
```

#### D-4: Pre-release installed vs. stable latest (resolves TC-20 ambiguity)

**Decision:** `update_available` is `true` if `latest_stable > current_version` OR `latest_prerelease > current_version`. If the user has `2.111.0a1` installed and `latest_stable` is `2.110.0`, `update_available` is `false` for stable but the response still shows both versions so the user can decide. The `update_available` field reflects whether ANY newer version exists on the feed compared to the installed version (using `packaging.version` ordering).

### Security Review

| Concern | Assessment |
|---------|-----------|
| **Credential exposure** | No credentials stored or logged. Auth delegated to `az login` + keyring. Subprocess calls use `capture_output=True` — stderr is returned to the user but not persisted. **Acceptable.** |
| **Subprocess injection** | The pip command is constructed with a fixed command list (`[sys.executable, "-m", "pip", "install", f"golazo-copilot=={version}", ...]`). The `version` parameter is a string from MCP input. Validate version format matches PEP 440 (alphanumeric, dots, plus signs only) before passing to subprocess to prevent command injection. |
| **Feed URL** | Hardcoded to the internal Azure Artifacts feed. No user-supplied URLs are accepted. **No SSRF risk.** |
| **Network requests** | `urllib.request.urlopen` with `timeout=10`. Only connects to the known feed URL. **Acceptable.** |

**Required validation:** Add a regex check on the `version` parameter before passing to subprocess: `re.match(r'^[a-zA-Z0-9._+]+$', version)`. Reject any version string that doesn't match.

### Dependency Review

| Dependency | Type | Risk |
|------------|------|------|
| `urllib.request` | Stdlib | None |
| `html.parser` | Stdlib | None |
| `subprocess` | Stdlib | None — used consistently across existing tools |
| `importlib.metadata` | Stdlib (3.8+) | None — Python 3.8+ is already required by Golazo |
| `importlib.util` | Stdlib | None |
| `packaging.version` | Transitive via pip/setuptools | **Low risk** — always present in any pip-managed environment. Add a try/except ImportError with a fallback message if somehow missing. |

**No new third-party dependencies.** This is the correct architectural choice.

### Failure Isolation

- The `golazo_update` tool is **completely isolated** from all other tools. It reads no state files, modifies no state files, and has no side effects on the workflow.
- The only shared resource is `server.py` (registration). A bug in `golazo_update` cannot affect `golazo_status`, `golazo_transition`, etc. — exceptions in dispatch are caught by the `call_tool` wrapper.
- pip install modifies the Python environment, but the running process is unaffected until restart. This is the correct behavior.

### Error Handling Architecture (resolves RC-3)

The tool MUST catch and wrap all external call failures:

| Call | Exception(s) | Action |
|------|-------------|--------|
| `importlib.metadata.version()` | `PackageNotFoundError` | Return `{"error": "...", "error_type": "not_installed"}` |
| `urllib.request.urlopen()` | `URLError`, `HTTPError`, `socket.timeout` | Return `{"error": "...", "error_type": "network"}` for URLError/timeout, `{"error": "...", "error_type": "auth"}` for 401/403 |
| `subprocess.run(["az", ...])` | `FileNotFoundError` | Return `{"error": "...", "error_type": "auth"}` with guidance to install Azure CLI |
| `subprocess.run([pip, ...])` | `FileNotFoundError`, non-zero exit | Return `{"error": "...", "error_type": "install_failed"}` with stderr |
| `packaging.version.Version()` | `InvalidVersion` | Skip the malformed version string, continue parsing others |

**No unhandled exceptions should escape the tool function.** Wrap the entire function body in a try/except that returns a generic error dict as a last resort.

### Scalability & Performance

- **Network call:** Single HTTP GET to the Simple API page. O(1) requests regardless of version count. 10-second timeout is appropriate.
- **HTML parsing:** Linear in page size. The feed page for a single package is typically < 100KB. No concern.
- **Version sorting:** O(n log n) for n versions. n is typically < 100. No concern.
- **No caching:** Each `check` action makes a fresh HTTP call. This is correct for v1 — the tool is only called on explicit user request, not on every status check.

### Capability Registry Impact

The `mcp-server` capability's `list_tools` contract changes from "7 tools registered" to "8 tools registered". The `depends_on` list gains `tool-update`. A new `tool-update` capability entry must be added to `capabilities.yaml`. See `GCP-0056-Capability-Impact.md` for details.

### Recommendations for Developer

1. **Version input validation** — Regex-check the `version` parameter before subprocess invocation (security).
2. **Catch `InvalidVersion`** — When parsing feed HTML, wrap `packaging.version.Version()` in try/except.
3. **Catch `PackageNotFoundError`** — Handle the case where `golazo-copilot` is not installed.
4. **Use `shutil.which("az")`** — Check for `az` availability before `subprocess.run` to produce a cleaner error on Windows (also check `az.cmd`).
5. **Extract version parsing into a tested helper** — `_parse_versions_from_html(html: str) -> list[Version]` for clean unit testing.
6. **Wrap entire tool in try/except** — Final safety net returning a generic error dict.
7. **Update `capabilities.yaml`** — Add `tool-update` capability and update `mcp-server` depends_on.

### Test Case Adjustments

- **TC-23 through TC-25** (bootstrap_mode tests): These test cases reference `bootstrap_mode` which is being removed from the schema per D-1. The developer should **skip or rewrite** these test cases to verify that the install-success response includes restart + bootstrap instructions as text guidance rather than as an executable parameter.
- **TC-20**: Implement per D-4 — `update_available` uses `packaging.version` ordering; both versions are shown in the response regardless.
