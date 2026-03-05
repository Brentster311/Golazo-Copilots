**Status**: IMPLEMENTED

**User Story**
- **Title**: Rename MCP Tools from `gcp_` Prefix to `golazo_` Prefix
- **As a**: Golazo Copilot user
- **I want**: All MCP tool names to use the `golazo_` prefix instead of `gcp_`
- **So that**: Tool names clearly reflect the product name (Golazo) rather than an internal abbreviation, improving discoverability and branding

- **Out of scope**:
  - Renaming historical WorkItems documents (design docs, decision notes, user stories from past work items)
  - Renaming test file names (only references inside test files are renamed)
  - Changing any tool behavior or parameters
  - Version bump (separate task)

- **Assumptions**:
  - **Assumption (explicit)**: This is a pure rename — no behavior changes, no parameter changes, no new tools, no removed tools.
  - **Assumption (explicit)**: The 7 tools to rename are: `gcp_status`, `gcp_transition`, `gcp_create_workitem`, `gcp_bootstrap`, `gcp_consent`, `gcp_capabilities`, `gcp_role_context`.
  - **Assumption (explicit)**: Tool source files will be renamed from `gcp_*.py` to `golazo_*.py`.
  - **Assumption (explicit)**: All references in operational code (server.py, tool files, role markdown, .github files, capabilities.yaml, README, bootstrap-instructions.md, tests, __init__.py) will be updated.

- **Acceptance Criteria** (bulleted, testable):
  - [x] **AC1**: All 7 MCP tools are registered with `golazo_` prefix names in server.py and callable by those names.
  - [x] **AC2**: All tool source files are renamed from `gcp_*.py` to `golazo_*.py` and all imports updated.
  - [x] **AC3**: All role markdown files (defaults + deployed .github/roles) reference `golazo_` tool names.
  - [x] **AC4**: All existing tests pass with zero regressions after rename.
  - [x] **AC5**: No remaining `gcp_` references in operational files (excluding historical WorkItems and test filenames).

- **Non-functional requirements**:
  - Pure rename with no behavior changes
  - All ~695 operational occurrences updated

- **Telemetry / metrics expected**: None

- **Rollout / rollback notes**:
  - This is a breaking change for any consumers calling tools by the old `gcp_` names.
  - The `.github/copilot-instructions.md` bootstrap file will be updated with new tool names.
  - Deployed `.github/roles/` files will be updated.

## Closure

### Summary
All 7 MCP tools renamed from `gcp_` to `golazo_` prefix. 55 files changed (628/628 insertions/deletions), version bumped to 2.107.0, branch pushed to origin.

### Acceptance Criteria Status
| AC | Status | Evidence |
|----|--------|----------|
| AC1 | PASS | server.py registers all 7 tools with `golazo_` names |
| AC2 | PASS | git mv renamed all files; imports updated |
| AC3 | PASS | All 30+ role/doc files updated |
| AC4 | PASS | 409 tests pass, 0 regressions |
| AC5 | PASS | grep verification: 0 remaining `gcp_` in operational files |

### Future Work Items
- Architecture Overview and Handoff Protocol docs had stale `gcp_` references not caught by the initial Developer audit — fixed by Documenter
- Retrospective recommended: CWD validation before git operations, smarter exclusion patterns for doc scans
