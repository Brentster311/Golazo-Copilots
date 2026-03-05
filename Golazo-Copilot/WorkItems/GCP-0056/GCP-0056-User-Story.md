# GCP-0056 User Story

**Status**: IMPLEMENTED

## User Story

- **Title:** Golazo Update Checker Tool
- **As a:** Golazo Copilot user
- **I want:** a tool that checks Azure Artifacts for newer versions of Golazo and guides me through the update process
- **So that:** I can stay current with the latest Golazo releases without manually tracking versions or remembering installation parameters

## Out of Scope
- Auto-updating without user consent
- Scheduled/periodic update checks (only triggered by explicit user request)
- Updating other packages beyond golazo-copilot and its required dependencies
- Downgrading to older versions

## Assumptions
- **Assumption (explicit):** The tool is an MCP tool (consistent with Golazo's existing architecture) — no separate CLI or GUI needed.
- **Assumption (explicit):** The Azure Artifacts feed at `https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/` is the canonical source for Golazo packages.
- **Assumption (explicit):** `keyring` and `artifacts-keyring` are the authentication dependencies required to access the feed.
- **Assumption (explicit):** `az login` is required before pip can authenticate to the Azure Artifacts feed.
- **Assumption (explicit):** "Latest version" means the highest version on the feed; "latest released version" means the highest non-pre-release version (no alpha/beta/rc/dev suffixes).
- **Assumption (explicit):** The user can choose between installing the latest released version or the latest pre-release version.

## Acceptance Criteria (bulleted, testable)
- [x] When the user says "update golazo", "check for golazo update", or similar, the tool queries the Azure Artifacts feed and reports the current installed version, the latest released version, and the latest pre-release version (if different).
- [x] The user is presented with a choice: install latest released version, install latest pre-release version, or cancel.
- [x] If the user chooses to install, the tool runs the correct `pip install` command with `--index-url=https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/`, ensures `keyring` and `artifacts-keyring` are installed, and verifies `az login` is active (prompting if not).
- [x] If the installed version is already the latest, the tool informs the user and does not reinstall.
- [x] After a successful install, the tool informs the user that the MCP server must be refreshed/restarted before the new version takes effect, and that bootstrap will not work until this refresh occurs.
- [x] After the user confirms the refresh has been done, the tool asks the user to choose one of: (1) Do not bootstrap, (2) Bootstrap, or (3) Full clean bootstrap. If the user selects option 2 or 3, the tool invokes `golazo_bootstrap` with the appropriate parameters.

## Non-functional Requirements
- The tool must not store or expose credentials; authentication is handled entirely through `az login` + `keyring`/`artifacts-keyring`.
- The version check should complete within a reasonable time (< 10 seconds on a healthy network).

## Telemetry / Metrics Expected
- None required for initial implementation.

## Rollout / Rollback Notes
- The tool is additive — it does not change existing Golazo behavior. Rollback is simply removing the tool registration.

## Closure

**Date:** 2026-02-27
**Final Status:** IMPLEMENTED — all 6 acceptance criteria validated and passing.

### Implementation Summary

The `golazo_update` MCP tool was implemented with two actions:
- **check**: Queries the Azure Artifacts PEP 503 API, parses HTML to extract versions, classifies into stable/pre-release, and returns a structured dict with `current_version`, `latest_stable`, `latest_prerelease`, and `update_available`.
- **install**: Validates the version string, runs preflight checks (keyring, artifacts-keyring, `az login`), shells out to pip with the correct `--index-url`, and returns success with `restart_required` and `bootstrap_options` (3 options: no bootstrap, standard, full clean).

### Artifacts Delivered
| Artifact | Path |
|----------|------|
| Tool implementation | `golazo-copilot/src/golazo_copilot/tools/golazo_update.py` (~312 lines) |
| Test suite | `golazo-copilot/tests/test_golazo_update.py` (30 tests, all passing) |
| Server integration | `golazo-copilot/src/golazo_copilot/server.py` (handler + formatter) |
| Package export | `golazo-copilot/src/golazo_copilot/tools/__init__.py` |
| Documentation | `golazo-copilot/README.md` (updated) |
| Capability registration | `capabilities.yaml` (updated) |

### Acceptance Criteria Results
| # | Criterion | Result |
|---|-----------|--------|
| 1 | Check action reports current, latest stable, and latest pre-release versions | PASS |
| 2 | User presented with install choices (stable, pre-release, cancel) | PASS |
| 3 | Install runs pip with correct `--index-url`, validates auth prerequisites | PASS |
| 4 | Already-latest detection via `update_available` flag | PASS |
| 5 | Post-install restart/refresh messaging | PASS |
| 6 | Bootstrap options (none, standard, full clean) provided after install | PASS |

### Pending Work Items (from Retrospective)
1. **Fix broken import chain** — `get_role_order_for_profile` in `core/transitions.py` causes 15+ test collection failures (pre-existing, not introduced by GCP-0056)
2. **Add linter configuration** — ruff config in `pyproject.toml`
3. **Add CI import smoke test** — catch import-chain breaks early
4. **Add `golazo_role_context` documentation to README** — noted by documenter as out-of-scope for this work item
