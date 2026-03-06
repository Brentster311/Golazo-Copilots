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

It will run `golazo_status` and display the running version (e.g., `v4.3.1`).

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

- *"Run golazo bootstrap in orchestrator-only mode"* (minimal setup)
- *"Please bootstrap GCP"* (full setup)

`orchestrator-only` creates only:
- `.github/agents/Golazo-Copilot.md` – Orchestrator instructions required for workflow execution

Full bootstrap creates the Golazo Copilot directory structure and instruction files in your workspace:
- `WorkItems/` – Directory for work item artifacts
- `.github/agents/Golazo-Copilot.md` – Workflow enforcement rules for Copilot
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
Get comprehensive workflow status for a work item. Returns current role, phase, required outputs, next steps, deviations, and the Golazo Copilot version number.

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
| `mode` | string | No | Bootstrap mode: `full` (default) or `orchestrator-only` |
| `force` | boolean | No | Overwrite existing files if they exist (default: `false`) |
| `include_roles` | boolean | No | Also copy default role files to `.github/agents/golazo-copilot/roles/` (default: `true`) |
| `workspace_path` | string | **Yes** | Workspace root path |

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
Check for and install updates to Golazo Copilot from Azure Artifacts.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | **Yes** | `check` to report installed vs. latest versions, or `install` to install a specific version |
| `version` | string | No | Target version to install (required when `action="install"`) |
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

2. **Install a specific version:**
   > "Update golazo to version 4.3.1"

The tool validates authentication prerequisites (keyring, artifacts-keyring, `az login`) before installing, and will prompt you to restart the MCP server afterward.

Alternatively, update manually via pip:

```powershell
pip install --upgrade golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

Then reload VS Code and re-bootstrap your workspace to pick up the new version:
> "Run golazo bootstrap in orchestrator-only mode with force"

## License

MIT

## Changelog (By Version)

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

### Historical Version Notes (Backfilled)

Backfilled from `golazo-copilot/pyproject.toml` version-bump commit subjects:

- v2.111.5: GCP-0058 drop golazo_update MCP tool, use terminal strategy
- v2.111.4: GCP-0057 harden update-check fallback launchers
- v2.111.3: GCP-0057 authenticated fallback for golazo_update check
- v2.111.2: GCP-0056 bump version to 2.111.2
- v2.111.1: Retro inline exception and version bump
- v2.111.0: version bump
- v2.110.0: GCP-0055 artifacts and profile role support updates
- v2.109.1: GCP-0053 never overwrite capabilities.yaml on force bootstrap
- v2.109.0: GCP-0053 document closure re-entry in bootstrap instructions
- v2.107.0: GCP-0054 version bump and builder notes
- v2.106.0: architecture overview rewrite and legacy VS project cleanup
- v2.105.2: fixed `__version__` package metadata source
- v2.105.1: version bump
- v2.105.0: version bump
- v2.104.5: GCP-0046 add Domain Expert role to definition phase
- v2.104.3: refactor role linter check requirement
- v2.104.2: POA pre-scope review requirements for capabilities and best practices
- v2.104.1: GCP-0044 make `workspace_path` required on MCP tools
- v2.103.6: V2 rule grammar updates and EES work item creation
- v2.103.5: EES-00007 fix run_in_worker call signature
- v2.103.4: EES-00007 retrospective notes
- v2.103.1: rollback of SFI-026 manager_alias fix
- v2.100.11: GCP-0038 capability registry tool implementation
- v2.100.10: version bump
- v2.100.9: GCP-0031 remove DoR/DoD checklist system
- v2.100.8: update commit (limited metadata retained)
- v2.100.7: LLM-0007 client-side JS rendering via Playwright
- v2.30.0: version bump
- v2.17.0: bootstrap instructions update and version bump
- v2.16.7: GCP-0025 output validation for role transitions
- v2.16.5: checklist item type and evidence validation fix
- v2.16.3: expose evidence parameter in MCP tool schemas
- v2.16.2: dynamic version injection in bootstrap and role loader
- v2.16.1: version bump
- v2.16.0: GCP-0024 evidence-based validation and role order update
- v2.15.0: GCP-0023 evidence-based validation for DoR/DoD items
- v2.12.1: maintenance release (`foo` commit message)
- v2.10.0: GCP-0019 enforce role decision notes on transition
- v2.9.0: GCP-0014 require PO consent for gate bypass and status deviations
- v2.8.0: GCP-0011 align version comments across package/bootstrap/roles
- v0.3.2: fixed server.py syntax error
- v0.3.1: replaced emojis with ASCII icons to avoid encoding issues
- v0.3.0: GCP-0005 add consent tool for deviation tracking
- v0.2.2: repaired server.py indentation errors
- v0.2.1: renamed `gcp_init` to `gcp_create_workitem`
- v0.2.0: minor release for GCP-0010 completion
- v0.1.4: GCP-0010 add bootstrap tool
- v0.1.3: updated roles to match Golazo v1 source of truth
- v0.1.2: synchronized `pyproject.toml` version
- v0.1.0: initial Python MCP implementation (`GCP-0001`)
