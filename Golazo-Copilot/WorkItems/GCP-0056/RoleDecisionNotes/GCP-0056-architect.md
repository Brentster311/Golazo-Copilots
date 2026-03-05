# GCP-0056 Architect Role Decision Notes

## Role: Architect
## Work Item: GCP-0056 — Golazo Update Checker Tool

## Decisions Made

### 1. Removed `bootstrap_mode` from schema (D-1)

The most significant architectural decision. The design doc's `bootstrap_mode` parameter on the install action would execute `golazo_bootstrap` against stale in-memory code — a fundamental violation of process lifecycle semantics. Bootstrap MUST be a separate post-restart step. This resolves RC-2 and RC-12 from QA review.

**Impact on test cases:** TC-23 through TC-25 need rewriting. They should verify the install-success response contains textual guidance about bootstrap options, not test an executable `bootstrap_mode` parameter.

### 2. Required `version` validation on install (D-2)

Chose explicit validation over defaulting to latest. The two-step check→install flow gives users (and the LLM) full visibility into what version is being installed. Resolves RC-1.

### 3. Defined return dict contracts (D-3)

Specified exact JSON schemas for all four response scenarios (check, install-success, install-failure, error). This unblocks formatter implementation and gives tests concrete assertion targets. Resolves RC-13.

### 4. Resolved pre-release ambiguity (D-4)

`update_available` uses `packaging.version` ordering to determine if any newer version exists. Both stable and pre-release latest versions are always included in the response so the user can make an informed choice. Resolves TC-20 ambiguity.

### 5. Added version input sanitization requirement

Security review identified that the `version` string from MCP input is passed to `subprocess.run` via pip command. Required a regex validation (`^[a-zA-Z0-9._+]+$`) before subprocess invocation to prevent injection.

### 6. Confirmed no new dependencies

All stdlib modules used are available in Python 3.8+ (Golazo's minimum). `packaging.version` is a transitive dependency present in all pip-managed environments. No new third-party dependencies are introduced — this is architecturally correct.

### 7. Confirmed complete failure isolation

The tool reads no workflow state, writes no workflow state, and has no side effects on other tools. Exceptions are caught by the `call_tool` wrapper in `server.py`. A bug in `golazo_update` cannot affect any other tool.

## Assumptions

- `packaging` library is always available at runtime (transitive dep of pip/setuptools). Added guidance to include a try/except ImportError fallback.
- The Azure Artifacts feed URL is stable and will not change without coordinated team communication. Hardcoding is acceptable for v1.
- `sys.executable` correctly identifies the Python running the MCP server. This is true for standard pip-installed packages but may not hold for exotic launch configurations (documented as a known limitation per RC-5).
- Concurrent updates to the same venv are unsupported (documented per RC-4). No locking mechanism is added for v1.

## Artifacts Created

| Artifact | Path |
|----------|------|
| Architect Notes | `WorkItems/GCP-0056/Design/GCP-0056-Review-Comments.md` (appended) |
| Capability Impact | `WorkItems/GCP-0056/Design/GCP-0056-Capability-Impact.md` |
| Role Decision Notes | `WorkItems/GCP-0056/RoleDecisionNotes/GCP-0056-architect.md` (this file) |

## Recommendations for Downstream Roles

- **Developer:** Follow the error handling table in Architect Notes. Extract `_parse_versions_from_html()` as a testable helper. Validate version input with regex before subprocess. Update `capabilities.yaml` with the new `tool-update` entry.
- **Refactor Expert:** The tool follows existing patterns — no structural refactoring expected. Verify version parsing is in a helper function, not inline.
- **Builder:** No build changes needed — the tool is a new Python module within the existing package structure.
