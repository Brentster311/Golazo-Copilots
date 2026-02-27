# GCP-0056 Test Cases — Golazo Update Checker Tool

## Test Case Index

| ID | AC | Category | Description |
|----|-----|----------|-------------|
| TC-01 | AC-1 | Happy path | Check action returns current, latest stable, and latest pre-release versions |
| TC-02 | AC-1 | Happy path | Check action when only stable versions exist (no pre-release) |
| TC-03 | AC-1 | Edge case | Check action when feed returns a single version |
| TC-04 | AC-1 | Edge case | Check action when feed HTML contains both .tar.gz and .whl entries for same version |
| TC-05 | AC-1 | Error case | Check action when feed is unreachable (network timeout) |
| TC-06 | AC-1 | Error case | Check action when feed returns HTTP 401/403 |
| TC-07 | AC-1 | Error case | Check action when feed returns malformed HTML |
| TC-08 | AC-1 | Error case | Check action when `golazo-copilot` is not installed (`PackageNotFoundError`) |
| TC-09 | AC-2 | Happy path | Install action with valid version installs the specified version |
| TC-10 | AC-2 | Edge case | Install action with pre-release version installs correctly |
| TC-11 | AC-2 | Error case | Install action without version parameter returns validation error |
| TC-12 | AC-3 | Happy path | Install verifies keyring + artifacts-keyring are available before running pip |
| TC-13 | AC-3 | Error case | Install fails pre-flight when keyring is missing |
| TC-14 | AC-3 | Error case | Install fails pre-flight when artifacts-keyring is missing |
| TC-15 | AC-3 | Happy path | Install verifies az login is active before running pip |
| TC-16 | AC-3 | Error case | Install fails pre-flight when az login is not active |
| TC-17 | AC-3 | Error case | Install fails pre-flight when az CLI is not on PATH |
| TC-18 | AC-3 | Happy path | Install constructs correct pip command with --index-url |
| TC-19 | AC-4 | Happy path | Check reports "already up to date" when installed version equals latest |
| TC-20 | AC-4 | Edge case | Check reports "already up to date" when installed version is a pre-release and matches latest pre-release |
| TC-21 | AC-5 | Happy path | Successful install returns restart/refresh message |
| TC-22 | AC-5 | Happy path | Post-install message mentions bootstrap will not work until refresh |
| TC-23 | AC-6 | Happy path | Bootstrap mode "none" does not invoke golazo_bootstrap |
| TC-24 | AC-6 | Happy path | Bootstrap mode "standard" invokes golazo_bootstrap with default params |
| TC-25 | AC-6 | Happy path | Bootstrap mode "full" invokes golazo_bootstrap with force + include_roles |
| TC-26 | N/A | Edge case | Version parsing handles PEP 440 edge cases (post-release, dev, local) |
| TC-27 | N/A | Error case | pip install fails (non-zero exit code) — error is reported |
| TC-28 | N/A | Error case | pip install succeeds but installed version doesn't match target |
| TC-29 | N/A | Edge case | Feed contains versions with `InvalidVersion` strings — gracefully skipped |
| TC-30 | N/A | Unit | format_update_result correctly formats check result |
| TC-31 | N/A | Unit | format_update_result correctly formats install success |
| TC-32 | N/A | Unit | format_update_result correctly formats install failure |
| TC-33 | N/A | Unit | format_update_result correctly formats error (network, auth) |

---

## Detailed Test Cases

### TC-01: Check action returns version information
**AC:** AC-1
**Category:** Happy path
**Preconditions:** `golazo-copilot` version 2.109.0 is installed. Feed contains versions 2.108.0, 2.109.0, 2.110.0, 2.111.0a1.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- `current_version` = "2.109.0"
- `latest_stable` = "2.110.0"
- `latest_prerelease` = "2.111.0a1"
- `update_available` = True
**Mock:** `urllib.request.urlopen` returns HTML with anchor tags for all four versions. `importlib.metadata.version` returns "2.109.0".

---

### TC-02: Check action when no pre-release versions exist
**AC:** AC-1
**Category:** Happy path
**Preconditions:** Feed contains only stable versions: 2.108.0, 2.109.0, 2.110.0.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- `latest_stable` = "2.110.0"
- `latest_prerelease` = None or same as `latest_stable`
- `update_available` = True

---

### TC-03: Check action when feed has a single version
**AC:** AC-1
**Category:** Edge case
**Preconditions:** Feed contains only version 2.109.0. Installed version is 2.109.0.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- `latest_stable` = "2.109.0"
- `update_available` = False

---

### TC-04: Check action deduplicates versions across distribution formats
**AC:** AC-1
**Category:** Edge case
**Preconditions:** Feed contains `golazo_copilot-2.110.0.tar.gz` and `golazo_copilot-2.110.0-py3-none-any.whl`.
**Input:** `action="check"`
**Expected:** Version 2.110.0 appears once in the parsed results. No duplicates in output.

---

### TC-05: Check action when feed is unreachable
**AC:** AC-1
**Category:** Error case
**Preconditions:** Network is down or feed URL is unreachable.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict with descriptive message (e.g., "Unable to reach Azure Artifacts feed")
- Does not crash or raise an unhandled exception
- Completes within ~10 seconds (timeout)
**Mock:** `urllib.request.urlopen` raises `URLError`.

---

### TC-06: Check action when feed returns HTTP 401/403
**AC:** AC-1
**Category:** Error case
**Preconditions:** User is not authenticated to the feed.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict mentioning authentication failure
- Suggests running `az login` or verifying feed access
**Mock:** `urllib.request.urlopen` raises `HTTPError(403)`.

---

### TC-07: Check action when feed returns malformed HTML
**AC:** AC-1
**Category:** Error case
**Preconditions:** Feed returns HTML that cannot be parsed for version links.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict or empty version list with a descriptive message
- Does not crash
**Mock:** `urllib.request.urlopen` returns `<html><body>unexpected content</body></html>`.

---

### TC-08: Check action when golazo-copilot is not installed
**AC:** AC-1
**Category:** Error case
**Preconditions:** `importlib.metadata.version("golazo-copilot")` raises `PackageNotFoundError`.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict indicating golazo-copilot is not installed in the current environment
- Provides guidance on how to install
**Mock:** `importlib.metadata.version` raises `PackageNotFoundError`.

---

### TC-09: Install action installs the specified stable version
**AC:** AC-2
**Category:** Happy path
**Preconditions:** All pre-flight checks pass (keyring, artifacts-keyring, az login).
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- `subprocess.run` is called with `[sys.executable, "-m", "pip", "install", "golazo-copilot==2.110.0", "--index-url=<feed-url>"]`
- Return dict has `success=True`, `version="2.110.0"`
- Post-install verification confirms version 2.110.0 is installed
**Mock:** `subprocess.run` returns exit code 0.

---

### TC-10: Install action installs a pre-release version
**AC:** AC-2
**Category:** Edge case
**Preconditions:** All pre-flight checks pass.
**Input:** `action="install"`, `version="2.111.0a1"`, `workspace_path="/workspace"`
**Expected:**
- pip command includes `golazo-copilot==2.111.0a1`
- Return dict has `success=True`
**Mock:** `subprocess.run` returns exit code 0.

---

### TC-11: Install action without version parameter
**AC:** AC-2
**Category:** Error case
**Preconditions:** N/A
**Input:** `action="install"`, `workspace_path="/workspace"` (no `version`)
**Expected:**
- Returns validation error: "version parameter is required for action=install"
- Does not attempt pip install

---

### TC-12: Install verifies keyring and artifacts-keyring are available
**AC:** AC-3
**Category:** Happy path
**Preconditions:** Both `keyring` and `artifacts_keyring` are importable.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- `importlib.util.find_spec("keyring")` is called and returns non-None
- `importlib.util.find_spec("artifacts_keyring")` is called and returns non-None
- Proceeds to az login check and install
**Mock:** `find_spec` returns a non-None spec for both.

---

### TC-13: Install fails when keyring is missing
**AC:** AC-3
**Category:** Error case
**Preconditions:** `keyring` is not installed.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict mentioning `keyring` is not installed
- Provides the pip install command: `pip install keyring`
- Does NOT attempt pip install of golazo-copilot
**Mock:** `find_spec("keyring")` returns None.

---

### TC-14: Install fails when artifacts-keyring is missing
**AC:** AC-3
**Category:** Error case
**Preconditions:** `keyring` is installed but `artifacts-keyring` is not.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict mentioning `artifacts-keyring` is not installed
- Provides the pip install command: `pip install artifacts-keyring`
**Mock:** `find_spec("keyring")` returns non-None, `find_spec("artifacts_keyring")` returns None.

---

### TC-15: Install verifies az login is active
**AC:** AC-3
**Category:** Happy path
**Preconditions:** keyring + artifacts-keyring are available. `az account show` returns exit code 0.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- `subprocess.run(["az", "account", "show"], ...)` is called
- Returns exit code 0 → proceeds with install
**Mock:** `subprocess.run` for `az` returns exit code 0.

---

### TC-16: Install fails when az login is not active
**AC:** AC-3
**Category:** Error case
**Preconditions:** keyring + artifacts-keyring are available. `az account show` returns non-zero.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict instructing user to run `az login`
- Does NOT attempt pip install
**Mock:** `subprocess.run` for `az` returns exit code 1.

---

### TC-17: Install fails when az CLI is not on PATH
**AC:** AC-3
**Category:** Error case
**Preconditions:** `az` is not found on PATH.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- Returns error dict indicating Azure CLI is not installed or not on PATH
- Provides installation guidance
**Mock:** `subprocess.run(["az", ...])` raises `FileNotFoundError`.

---

### TC-18: Install constructs correct pip command
**AC:** AC-3
**Category:** Happy path
**Preconditions:** All pre-flight checks pass.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- The exact subprocess command is: `[sys.executable, "-m", "pip", "install", "golazo-copilot==2.110.0", "--index-url=https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/"]`
- Verify through mock assertion

---

### TC-19: Already up to date — stable version
**AC:** AC-4
**Category:** Happy path
**Preconditions:** Installed version is 2.110.0. Latest stable on feed is 2.110.0.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- `update_available` = False
- Message indicates "already up to date"
- No install is triggered

---

### TC-20: Already up to date — pre-release version
**AC:** AC-4
**Category:** Edge case
**Preconditions:** Installed version is 2.111.0a1. Latest pre-release on feed is 2.111.0a1. Latest stable is 2.110.0.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- `update_available` = True (stable 2.110.0 < installed 2.111.0a1, but user might want stable)
- OR `update_available` = False if logic considers the user on the latest pre-release
- **Note:** This edge case needs a design decision. Document the chosen behavior.

---

### TC-21: Post-install returns restart message
**AC:** AC-5
**Category:** Happy path
**Preconditions:** Install succeeds.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- Return dict contains a message stating MCP server must be refreshed/restarted
- Message explicitly says new version will not take effect until restart

---

### TC-22: Post-install message mentions bootstrap limitation
**AC:** AC-5
**Category:** Happy path
**Preconditions:** Install succeeds.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- Return dict contains message that bootstrap will not work until MCP server is refreshed
- The text should be clear enough for a non-technical user to understand

---

### TC-23: Bootstrap mode "none" skips bootstrap
**AC:** AC-6
**Category:** Happy path
**Preconditions:** Install succeeds.
**Input:** `action="install"`, `version="2.110.0"`, `bootstrap_mode="none"`, `workspace_path="/workspace"`
**Expected:**
- `golazo_bootstrap` is NOT called
- Return dict contains restart instructions without bootstrap action

---

### TC-24: Bootstrap mode "standard" invokes bootstrap
**AC:** AC-6
**Category:** Happy path
**Preconditions:** Install succeeds. MCP server has been restarted (simulated).
**Input:** `action="install"`, `version="2.110.0"`, `bootstrap_mode="standard"`, `workspace_path="/workspace"`
**Expected:**
- `golazo_bootstrap` is called with `workspace_path` and default parameters
- **Note:** Per RC-2, this may execute against stale code. Verify design decision on whether bootstrap is deferred.
**Mock:** `golazo_bootstrap` is mocked.

---

### TC-25: Bootstrap mode "full" invokes bootstrap with force
**AC:** AC-6
**Category:** Happy path
**Preconditions:** Install succeeds. MCP server has been restarted (simulated).
**Input:** `action="install"`, `version="2.110.0"`, `bootstrap_mode="full"`, `workspace_path="/workspace"`
**Expected:**
- `golazo_bootstrap` is called with `force=True`, `include_roles=True` (or equivalent full bootstrap params)
**Mock:** `golazo_bootstrap` is mocked.

---

### TC-26: PEP 440 edge cases in version parsing
**AC:** N/A (robustness)
**Category:** Edge case
**Preconditions:** Feed contains versions: 2.109.0, 2.110.0.post1, 2.110.0.dev1, 2.110.0+local1
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- Post-release version (2.110.0.post1) is classified as stable
- Dev version (2.110.0.dev1) is classified as pre-release
- Local version (2.110.0+local1) is handled gracefully (may raise `InvalidVersion` — should be skipped)
- No crash

---

### TC-27: pip install fails with non-zero exit code
**AC:** N/A (error handling)
**Category:** Error case
**Preconditions:** All pre-flight checks pass. pip install fails (e.g., version not found on feed).
**Input:** `action="install"`, `version="99.99.99"`, `workspace_path="/workspace"`
**Expected:**
- Return dict has `success=False`
- Error message includes pip's stderr output
- No crash
**Mock:** `subprocess.run` returns exit code 1 with stderr.

---

### TC-28: pip install succeeds but version mismatch
**AC:** N/A (verification)
**Category:** Error case
**Preconditions:** pip install returns 0 but post-install `importlib.metadata.version` returns a different version.
**Input:** `action="install"`, `version="2.110.0"`, `workspace_path="/workspace"`
**Expected:**
- Return dict has `success=False` or a warning
- Reports the mismatch between expected and actual installed version
**Mock:** `subprocess.run` returns 0. `importlib.metadata.version` returns "2.109.0" after install.

---

### TC-29: Feed contains invalid version strings
**AC:** N/A (robustness)
**Category:** Edge case
**Preconditions:** Feed HTML includes a filename like `golazo_copilot-notaversion.tar.gz`.
**Input:** `action="check"`, `workspace_path="/workspace"`
**Expected:**
- The invalid version is skipped (caught `InvalidVersion`)
- Valid versions are still returned correctly
- No crash

---

### TC-30: format_update_result — check result
**AC:** N/A (formatter)
**Category:** Unit
**Input:** `{"action": "check", "current_version": "2.109.0", "latest_stable": "2.110.0", "latest_prerelease": "2.111.0a1", "update_available": True}`
**Expected:**
- Formatted string includes all three version numbers
- Indicates an update is available
- Presents user choices (install stable, install pre-release, cancel)

---

### TC-31: format_update_result — install success
**AC:** N/A (formatter)
**Category:** Unit
**Input:** `{"action": "install", "version": "2.110.0", "success": True, "message": "Installed successfully"}`
**Expected:**
- Formatted string confirms successful installation of 2.110.0
- Includes MCP server restart instruction
- Includes bootstrap options

---

### TC-32: format_update_result — install failure
**AC:** N/A (formatter)
**Category:** Unit
**Input:** `{"action": "install", "version": "2.110.0", "success": False, "error": "pip exited with code 1: ..."}`
**Expected:**
- Formatted string indicates installation failed
- Includes the error details
- Does not present bootstrap options

---

### TC-33: format_update_result — error result
**AC:** N/A (formatter)
**Category:** Unit
**Input:** `{"error": "Unable to reach Azure Artifacts feed: connection timed out"}`
**Expected:**
- Formatted string shows the error message clearly
- Does not present install options

---

## Coverage Matrix

| Acceptance Criterion | Test Cases | Coverage |
|---------------------|------------|----------|
| AC-1: Query feed and report versions | TC-01, TC-02, TC-03, TC-04, TC-05, TC-06, TC-07, TC-08 | Happy, edge, error |
| AC-2: User choice to install | TC-09, TC-10, TC-11 | Happy, edge, error |
| AC-3: Correct pip install + auth | TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18 | Happy, error |
| AC-4: Already latest — no reinstall | TC-19, TC-20 | Happy, edge |
| AC-5: Post-install restart message | TC-21, TC-22 | Happy |
| AC-6: Bootstrap choice after refresh | TC-23, TC-24, TC-25 | Happy |
| Robustness / edge cases | TC-26, TC-27, TC-28, TC-29 | Edge, error |
| Formatter unit tests | TC-30, TC-31, TC-32, TC-33 | Unit |

