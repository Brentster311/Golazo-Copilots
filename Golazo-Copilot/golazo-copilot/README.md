# Golazo Copilot

A Model Context Protocol (MCP) server that brings **programmatic workflow enforcement** to GitHub Copilot. Golazo Copilot transforms the Golazo development methodology from markdown-based guidance into a system with persistent state, automated gates, and auditable artifacts.

## What is Golazo?

Golazo is a structured development methodology that ensures high-quality software delivery through role-based workflows, gates, and auditable artifacts. For a complete explanation of the Golazo methodology, see the [Golazo README](https://github.com/microsoft/golazo/blob/main/README.md).

## Features

- **Persistent state tracking** – Workflow progress is saved to `state.json` files, surviving session restarts
- **Automated role transitions** – Enforce the correct sequence by profile (complete includes Domain Expert and closure re-entry)
- **Role-based output validation** – Each role defines required outputs (files, directories) that are automatically validated on transition
- **Multi-session support** – Switch between work items while preserving context
- **Workflow profiles** – Choose `complete`, `express`, or `spike` modes based on task complexity
- **Deviation recording** – Audit trail when gates are bypassed with justification
- **Role notes enforcement** – Blocks transitions when role decision notes are missing (bypass with consent)
- **Version sync warning** – Alerts when the deployed workspace instructions don't match the running MCP server version
- **Role progress display** – Shows completion progress (X/N roles) for each work item profile

### Feature Details

#### Persistent State Tracking
Each work item maintains its own `state.json` file in the `WorkItems/<id>/` directory. This file records the current role, phase, role history with timestamps, and any deviations. State survives VS Code restarts, allowing you to resume exactly where you left off.

#### Automated Role Transitions
The Golazo workflow enforces a structured progression through roles:
1. **Project Owner** – Define the user story and acceptance criteria
2. **Program Manager** – Break down work, create design document
3. **Domain Expert** – Provide domain-specific guidance when needed
4. **Quality Assurance** – Review design, define test cases
5. **Architect** – Validate architectural alignment, review contracts
6. **Developer** – Implement the solution with TDD
7. **Refactor Expert** – Improve code quality without changing behavior
8. **Documenter** – Update documentation to reflect changes
9. **Builder** – Verify builds pass, handle CI/CD concerns
10. **Retrospective** – Review what worked and what didn't

When work reaches the **Developer** role, the role instructions require creating a feature branch using:
`git checkout -b <useralias>/<workitem-id>`
This branch format requirement is documented in the default Developer role file and validated by repository tests.

For the `complete` profile, retrospective transitions to Project Owner Assistant again for formal closure.

Transitions are validated—you cannot skip roles or jump directly to Developer without completing earlier phases. Backward transitions to any prior role are always allowed.

#### Role-Based Output Validation
Each role file (in `.github/agents/golazo-copilot/roles/`) defines a `## Required Outputs` section listing the files or directories that must exist before you can transition away from that role. The system automatically validates these on transition.

For example, the `project-owner-assistant` role requires:
```
## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md
```

When you call `golazo_transition`, the system:
1. Reads the current role's `## Required Outputs` section
2. Checks that each listed file/directory exists in the workspace
3. Blocks the transition if any output is missing, with a clear error message listing what's needed
4. Allows bypass via `golazo_consent` + `force=True` when justified

This replaces manual checklist marking with automated, file-based validation.

#### Multi-Session Support
Work on multiple features simultaneously. Each work item has independent state, allowing you to:
- Switch between work items without losing progress
- Check status of any work item at any time
- Resume interrupted work days or weeks later

#### Workflow Profiles
Choose the right level of process for the task:

| Profile | Roles | Use Case |
|---------|-------|----------|
| **Complete** | Full 10-role workflow + closure re-entry | Production features, complex changes |
| **Express** | Streamlined subset of roles | Small bug fixes, minor enhancements |
| **Spike** | Minimal roles | Prototypes, research, proof-of-concept |

All profiles use the same output validation mechanism—role files define what's required, and the system enforces it on transition.

#### Deviation Recording
When you need to bypass a gate (e.g., force a transition when outputs are missing), the system:
1. Requires explicit consent via `golazo_consent` tool
2. Records the action, reason, timestamp, and current role
3. Stores deviations in the work item's `state.json`
4. Enables retrospective review of process deviations

#### Role Notes Enforcement
The Golazo workflow requires every role to produce a decision notes document. The system enforces this by:
1. **Blocking on transition** – When you transition away from a role, `golazo_transition` checks if decision notes exist for that role. If missing, the transition **fails** with an error indicating the expected file path.
2. **Force with consent** – If you need to bypass, use `golazo_consent(action='skip_role')` first, then `golazo_transition(..., force=True)`.
3. **Status visibility** – `golazo_status` includes a `missing_notes` list showing which completed roles lack decision notes.
4. **Expected file naming** – Notes should be at `WorkItems/<id>/RoleDecisionNotes/<id>-<role>.md`

This ensures an audit trail of decisions made at each workflow stage.

#### Version Sync Warning
When you call `golazo_status`, the system compares the running MCP server version against the version comment in your workspace's `.github/agents/Golazo-Copilot.md`. If they differ, a warning is displayed so you know to re-bootstrap or update the package.

#### Role Progress Display
`golazo_status` shows profile-aware progress (e.g., `4/10` in complete profile, `3/5` in express/spike), giving visibility into overall workflow progress.

#### TechBestPractices Reference
When bootstrapping a workspace, a `.github/agents/golazo-copilot/roles/TechBestPractices.md` file is deployed alongside the role files. This shared reference document is referenced by the Architect, Developer, and Refactor Expert roles to ensure consistent technical standards.

## Prerequisites

- **Python 3.10 or later** installed and available in your system PATH
- **Visual Studio Code** with GitHub Copilot extension
- Access to the Azure Artifacts feed (for installation)

### Verify Python Installation

```powershell
python --version
```

You should see `Python 3.10.x` or later. If Python is not found, download and install from [python.org](https://www.python.org/downloads/). During installation, ensure you check **"Add python.exe to PATH"**.

## Installation

Install the Azure Artifacts credential provider first, then install `golazo-copilot` into your **global Python environment**:

```bash
# Install credential providers for Azure Artifacts authentication
pip install keyring artifacts-keyring

# Install golazo-copilot from Azure Artifacts
pip install golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

> **Note:** The first time you install from Azure Artifacts, you may be prompted to authenticate via browser, or you may need to run `az login` first.

### Verify Installation

In GitHub Copilot Chat, ask: **"GCP version?"**

It will run `golazo_status` and display the running version (e.g., `v4.3.7`).

## VS Code Configuration

Configure the MCP server in your **VS Code User Settings** so it's available across all workspaces.

### Step 1: Open User MCP Configuration

1. Open Command Palette: `Ctrl+Shift+P`
2. Run: **"MCP: Open User Configuration"**
3. Add the MCP server configuration, or
4. Create/edit the file directly at:
   - **Windows**: `%APPDATA%\Code\User\mcp.json`
   - **macOS**: `~/Library/Application Support/Code/User/mcp.json`
   - **Linux**: `~/.config/Code/User/mcp.json`

### Step 2: Add MCP Server Configuration

Add the following to your `mcp.json` file:

```json
{
    "servers": {
        "golazo-copilot": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "golazo_copilot.server"]
        }
    }
}
```

### Step 3: Reload VS Code

After saving the configuration:

1. Open Command Palette: `Ctrl+Shift+P`
2. Run: **"Developer: Reload Window"**

### Step 4: Verify MCP Server is Running

In GitHub Copilot Chat, ask: *"What MCP tools do you have?"*

You should see the Golazo Copilot tools listed:
- `golazo_create_workitem` – Initialize a new work item
- `golazo_status` – Check workflow status
- `golazo_transition` – Move between roles
- `golazo_transition_workitem` – Mark retrospective-complete work item and set next work item
- `golazo_consent` – Record consent for bypassing workflow gates
- `golazo_git_propose` – Record proposal-only git action intent for auditability
- `golazo_bootstrap` – Bootstrap Golazo instructions in a workspace
- `golazo_update` – Check for and install Golazo Copilot updates

### Step 5: Bootstrap Your Workspace

Bootstrap is required before workflow tool operations (`golazo_create_workitem`, `golazo_transition`, `golazo_transition_workitem`, `golazo_status` with a work item, `golazo_consent`, `golazo_role_context`, and `golazo_git_propose`).

In GitHub Copilot Chat, say one of:

- *"Run golazo bootstrap in orchestrator-only mode"* (minimal workspace-scoped setup)
- *"Run golazo bootstrap in orchestrator-only mode with user scope"* (install orchestrator instructions into the active user Copilot directory)
- *"Please bootstrap GCP"* (full setup)

`orchestrator-only` creates only the orchestrator instructions file. By default this is written to workspace scope:
- `.github/agents/Golazo-Copilot.md` – Orchestrator instructions required for workflow execution

If you run bootstrap with `scope="User"`, the same orchestrator instructions file is written under the active user Copilot directory instead of the target workspace, using the same relative path beneath the user Copilot root.

Full bootstrap creates the Golazo Copilot directory structure and instruction files in your workspace:
- `WorkItems/` – Directory for work item artifacts
- `.github/agents/Golazo-Copilot.md` – Workflow enforcement rules for Copilot when bootstrap uses the default workspace scope
- `.github/agents/golazo-copilot/roles/` – Role-specific instruction files (including `TechBestPractices.md`)

### Step 6: Select the Golazo-Copilot Agent in Chat

After bootstrap, switch Copilot Chat to the Golazo custom agent:

1. Open the Agent picker in Copilot Chat (e.g., `Ctrl+Shift+I`)
2. Select **Agent** mode
3. Choose **Golazo-Copilot** from the dropdown
4. If it is not listed, use **Configure Custom Agents...** and ensure `.github/agents/Golazo-Copilot.md` is enabled

## Troubleshooting

### Server not starting

**"python is not recognized"** – Python is not in your PATH. Either:
- Reinstall Python and check "Add python.exe to PATH"
- Use the full path to Python in your mcp.json:
  ```json
  "command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
  ```

**"spawn EPERM" error** – This occurs with Windows Store Python. Uninstall Windows Store Python and install from [python.org](https://www.python.org/downloads/) instead.

**"No module named golazo_copilot"** – The package isn't installed in the Python environment VS Code is using. Run:
```powershell
pip install golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

### Tools not appearing in Copilot Chat

1. Check the VS Code Output panel → select "MCP" from the dropdown
2. Verify the server started without errors
3. Try reloading: `Ctrl+Shift+P` → "Developer: Reload Window"

### Test the server manually

```powershell
python -m golazo_copilot.server
```

If it starts without errors (no output, waiting for input), the server is working correctly. Press `Ctrl+C` to exit.

## Usage

### Available MCP Tools

#### `golazo_create_workitem`
Create a new Golazo Copilot work item with persistent state tracking.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `work_item_id` | string | **Yes** | Unique identifier for the work item. Format: 1-4 letters, dash, 3+ digits (e.g., `GCP-0001`, `AB-001`, `TEST-1234`) |
| `profile` | string | No | Workflow profile: `complete` (default), `express`, or `spike` |
| `workspace_path` | string | **Yes** | Workspace root path containing the WorkItems folder |

#### `golazo_status`
Read-only workflow status reporting for a work item. Returns current role, phase, required outputs, next steps, deviations, and the Golazo Copilot version number. This tool does not modify workflow state or install software.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `work_item_id` | string | No | Work item identifier. If omitted or empty, only the version is returned |
| `workspace_path` | string | **Yes** | Workspace root path containing the WorkItems folder |

#### `golazo_transition`
Transition to a new role in the Golazo Copilot workflow.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `work_item_id` | string | **Yes** | Work item identifier |
| `role` | string | **Yes** | Target role: `project-owner-assistant`, `program-manager`, `domain-expert`, `quality-assurance`, `architect`, `developer`, `refactor-expert`, `builder`, `documenter`, `retrospective` |
| `force` | boolean | No | Force transition even if gates not met (default: `false`, requires prior consent) |
| `workspace_path` | string | **Yes** | Workspace root path containing the WorkItems folder |

#### `golazo_transition_workitem`
Mark a retrospective-complete work item as completed and set the next sequential work item in workspace-level `global_state.json`.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `work_item_id` | string | **Yes** | Completed work item identifier (must currently be at role `retrospective`) |
| `workspace_path` | string | **Yes** | Workspace root path containing the WorkItems folder |

#### `golazo_consent`
Record Project Owner consent for bypassing workflow gates. The rationale MUST be provided by the Project Owner (human), not generated by the assistant. Required before using `force=true`.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `work_item_id` | string | **Yes** | Work item identifier |
| `action` | string | **Yes** | Type of deviation: `skip_outputs`, `skip_role`, `revert_progress`, or `custom` |
| `reason` | string | **Yes** | Justification for the deviation (min 10 characters) |
| `workspace_path` | string | **Yes** | Workspace root path containing the WorkItems folder |

#### `golazo_bootstrap`
Bootstrap Golazo Copilot in a workspace — creates copilot instructions and directories.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `scope` | string | No | Install scope for orchestrator instructions: `Workspace` (default) or `User` |
| `mode` | string | No | Bootstrap mode: `full` (default) or `orchestrator-only` |
| `force` | boolean | No | Overwrite existing files if they exist (default: `false`) |
| `include_roles` | boolean | No | Also copy default role files to `.github/agents/golazo-copilot/roles/` (default: `true`) |
| `workspace_path` | string | **Yes** | Workspace root path |

Notes:
- Omitted or empty `scope` behaves the same as `Workspace`.
- `scope="User"` redirects only the orchestrator instructions file to the active user Copilot directory; other full-bootstrap artifacts remain workspace-scoped.
- Workflow preflight accepts orchestrator instructions from either workspace scope or active user scope.

#### `golazo_capabilities`
Query the project capability registry for impact analysis. Reads canonical `WorkItems/capabilities.yaml` to show features, dependencies, and which capabilities are affected by file changes. If only a legacy root `capabilities.yaml` exists, it is moved to the canonical path.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | **Yes** | Action to perform: `list` (summary), `show` (full card), `impact` (affected by files), `validate` (check key_files exist) |
| `capability` | string | No | Capability name (required for `action="show"`) |
| `files` | array of strings | No | File paths to check impact for (required for `action="impact"`) |
| `workspace_path` | string | **Yes** | Workspace root path containing `WorkItems/capabilities.yaml` (legacy root `capabilities.yaml` is migration input) |

#### `golazo_git_propose`
Record proposal-only git action intent in work-item state as append-only `git_actions` history.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `work_item_id` | string | **Yes** | Work item identifier |
| `action` | string | **Yes** | Proposed git action: `add`, `commit`, `push`, or `branch` |
| `files` | array of strings | No | Required for `action="add"` |
| `message` | string | No | Required for `action="commit"` |
| `branch` | string | No | Required for `action="push"` and `action="branch"` |
| `workspace_path` | string | **Yes** | Workspace root path containing the WorkItems folder |

#### `golazo_update`
State-changing update/install tool for Golazo Copilot from Azure Artifacts. Use `action="check"` for read-only version reporting, or `action="install"` to install a specific version.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | **Yes** | `check` reports installed vs. latest versions only; `install` performs package installation |
| `version` | string | No | Target version to install (required when `action="install"`) |
| `target` | string | No | Install target: `active` (default, current interpreter environment) or `global` (system/global Python launcher) |
| `workspace_path` | string | **Yes** | Workspace root path |

### Workflow Profiles

| Profile | Description | Use Case |
|---------|-------------|----------|
| `complete` | Full Golazo workflow with all gates enforced | Production features, complex changes |
| `express` | Reduced gates for faster iteration | Small bug fixes, minor enhancements |
| `spike` | Minimal process for exploration | Prototypes, research, proof-of-concept |

### Example Session

1. **Create a work item:**
   > "Create work item GCP-0042 using complete profile"

2. **Check status:**
   > "What's the status of GCP-0042?"

3. **Work through roles — Copilot follows role instructions to create required outputs:**
   > "Transition GCP-0042 to program-manager"

4. **If outputs are missing, the transition fails with a clear message:**
   > `[FAIL] Missing required outputs for 'project-owner-assistant': WorkItems/GCP-0042/GCP-0042-User-Story.md`

5. **Continue through all roles to completion:**
   > "Transition GCP-0042 to quality-assurance"
   > "Transition GCP-0042 to architect"
   > "Transition GCP-0042 to developer"
   > ... and so on through retrospective

## Updating

The easiest way to update is via the built-in MCP tool. In GitHub Copilot Chat:

1. **Check for updates:**
   > "Check for golazo updates"

   `check` is read-only and does not install or modify your environment.

2. **Install a specific version:**
   > "Update golazo to version 4.3.7"

   Optional target control examples:
   - Active environment (default): `golazo_update(action="install", version="4.3.7", target="active")`
   - Global/system target: `golazo_update(action="install", version="4.3.7", target="global")`

The tool validates authentication prerequisites (keyring, artifacts-keyring, `az login`) before installing, and will prompt you to restart the MCP server afterward. On Windows, preflight resolves Azure CLI using `az` with an `az.cmd` fallback so standard CLI installs are detected reliably.

Alternatively, update manually via pip:

```powershell
pip install --upgrade golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

Then reload VS Code and re-bootstrap your workspace to pick up the new version:
> "Run golazo bootstrap in orchestrator-only mode with force"

## License

MIT

## Changelog (By Version)

### v4.3.7

- Enforced inline-only orchestration in spine instructions: never use subagent mode for any workflow role.
- Updated orchestration loop guidance to execute all roles inline and removed subagent delegation instructions from the spine template.

### v4.3.6

- Updated orchestrator execution matrix to run `retrospective` as an inline-required role instead of subagent-default.

### v4.3.5

- Finalized GCP-0068 release packaging for Windows Azure CLI preflight hardening in `golazo_update`, including builder verification and capability registry validation (`GCP-0068`)

### v4.3.4

- Clarified `golazo_status` semantics as read-only reporting that does not modify workflow state or install software (`GCP-0067`)
- Clarified `golazo_update` semantics as state-changing install behavior, including explicit `target` selection (`active` default, `global` explicit) (`GCP-0067`)
- Added deterministic install-target resolution and invalid-target error handling with explicit confirmation output (`GCP-0067`)
- Hardened Windows `golazo_update` preflight to resolve Azure CLI via `az`/`az.cmd` and improved missing/login/timeout/execution diagnostics (`GCP-0068`)

### v4.3.3

- Documenter role now explicitly requires maintaining the changelog at the end of `README.md` (`GCP-0066`)
- Added explicit sequencing policy: version must be defined/updated before changelog maintenance (`GCP-0066`)
- Added policy test coverage for changelog requirement and version-before-changelog semantics (`GCP-0066`)

### v4.3.2

- Canonicalized capability registry location to `WorkItems/capabilities.yaml` for `golazo_capabilities` operations (`GCP-0065`)
- Added automatic migration: when legacy root `capabilities.yaml` is found and canonical is missing, it is moved to `WorkItems/capabilities.yaml`
- Clarified dual-file behavior: canonical file wins when both canonical and legacy files exist
- Improved missing-registry guidance to point to canonical `WorkItems/capabilities.yaml`

### v4.3.1

- Modularized `golazo_status` internals for maintainability while preserving output contract and behavior (`GCP-0064`)
- Consolidated role execution-mode policy guidance (inline design roles, subagent default for non-design roles) and aligned docs/mappings (`GCP-0063`)

### v4.2.3

- Added project-level completion handoff via `golazo_transition_workitem` with next-item sequencing and `global_state.json` persistence (`GCP-0061`)

### v4.2.2

- Hardened closure guidance to require runtime UX validation evidence and explicit PO sign-off for unverifiable UX acceptance criteria

### v4.2.1

- Refactored MCP server dispatch into modular handlers without changing tool behavior
- Refreshed bootstrap capabilities template behavior
- Added/enforced builder PEP 440 versioning guidance

### v4.0.0

- Enforced workflow-managed branch naming format `<useralias>/<workitem-id>` (`GCP-0062`)
- Aligned Golazo agent bootstrap and documentation behavior

### v3.0.4

- Auto-create root `capabilities.yaml` on first successful `golazo_create_workitem` call when missing
- Preserve existing `capabilities.yaml` content when already present (`GCP-0058`)

### v3.0.3

- Introduced required bootstrap preflight with `orchestrator-only` mode and explicit remediation path (`GCP-0057`)

### v3.0.2

- Reconciled workflow state drift and retargeted execution path from `GCP-0059` to `GCP-0057` where needed
- Updated role/default guidance and bootstrap instructions to align closure and transition behavior
- Refreshed affected work-item artifacts and state files to restore consistent role progression
- Updated transition/status test coverage related to closure gate and role transitions

### v3.0.1

- Introduced the orchestrator-instructions bootstrap requirement (`GCP-0059`)
- Added `orchestrator-only` bootstrap mode support in tooling and dispatch paths
- Updated `golazo_bootstrap` behavior, server dispatch wiring, and associated bootstrap/server tests
- Added complete `GCP-0059` workflow artifacts to document and validate the rollout

### Historical Version Summary

- v2.111: update-tooling hardening and fallback/authentication improvements; eventual shift away from `golazo_update` MCP path.
- v2.110: profile-role support and associated GCP-0055 workflow artifacts.
- v2.109: bootstrap safety improvements, including protection against overwriting `capabilities.yaml` and closure guidance updates.
- v2.107: builder/versioning process updates and release hygiene notes.
- v2.106: architecture/documentation refresh and cleanup of legacy project artifacts.
- v2.105: versioning reliability fixes, including metadata-based `__version__` sourcing.
- v2.104: role/process hardening (Domain Expert addition, linter expectations, POA pre-scope checks, required `workspace_path`).
- v2.103: rule grammar/decision updates and EES-series fixes/rollbacks.
- v2.100: capability-registry introduction, checklist-system removal, and related workflow evolution.
- v2.30: baseline release bump in early pre-GCP history.
- v2.17: bootstrap-instructions refresh and version alignment.
- v2.16: evidence-driven workflow enforcement maturation (DoR/DoD evidence, role-order and validation updates).
- v2.15: initial evidence-based validation capability rollout.
- v2.12: maintenance-only minor stream (limited metadata retained).
- v2.10: enforced role decision notes on transitions.
- v2.9: Project Owner consent/deviation tracking visibility improvements.
- v2.8: version-comment alignment across package/bootstrap/role files.
- v0.3: stabilization fixes plus consent tool introduction.
- v0.2: early workflow/tooling renames and bootstrap-related maturation.
- v0.1: initial Golazo MCP foundation and first bootstrap/tooling rollout.
