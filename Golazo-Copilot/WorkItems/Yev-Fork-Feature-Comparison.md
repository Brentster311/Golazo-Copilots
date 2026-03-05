# Yev Fork vs Official Golazo Feature Comparison

Date: 2026-03-03  
Official baseline checked: `golazo-copilot==4.0.0` (installed globally)

## Scope
Compared Yev's fork at:
- `C:\Users\brentj\source\repos\golazy`

Against official Golazo code at:
- `golazo-copilot/src/golazo_copilot/`
- installed package `golazo-copilot==4.0.0`

## Additions in Yev's Fork Not Addressed in Official 4.0.0

### 1) `golazo_git_propose` MCP tool
**What it adds**
- New MCP command to record proposed git operations in work-item state.
- Supports actions: `add`, `commit`, `push`, `branch`.
- Validates required params by action (files/message/branch).

**Value proposition**
- Adds governance and traceability before risky SCM actions by turning git intent into an auditable workflow artifact.
- Reduces accidental or out-of-policy commits/pushes by requiring explicit proposal metadata first.
- Improves retrospective quality because teams can reconstruct why a git action was proposed, not just what happened.
- Creates a clean seam for future approval gates (e.g., Project Owner or QA approval) without changing core git mechanics.

**Implementation evidence (fork)**
- `src/golazo_copilot/tools/golazo_git_propose.py`
- Exported via `src/golazo_copilot/tools/__init__.py`
- Registered + dispatched in `src/golazo_copilot/server.py`
- Backed by tests: `tests/test_golazo_git_propose.py`

**State impact**
- Adds `git_actions` list on `WorkItemState` in `src/golazo_copilot/core/types.py`.

### 2) `golazo_transition_workitem` MCP tool
**What it adds**
- Project-level transition utility from a completed retrospective item to the next work item.
- Requires current role = `retrospective`.
- Computes next ID (e.g., `GCP-0006` -> `GCP-0007`).

**Value proposition**
- Introduces project-level continuity so completion of one item automatically informs planning of the next.
- Reduces coordination overhead by standardizing next-item sequencing and status updates in one operation.
- Improves portfolio visibility with explicit `next_work_item` signaling for orchestrators and dashboards.
- Prevents workflow drift by ensuring only retrospective-complete items can advance project-level progression.

**Implementation evidence (fork)**
- `src/golazo_copilot/tools/golazo_transition_workitem.py`
- Exported via `src/golazo_copilot/tools/__init__.py`
- Registered + dispatched in `src/golazo_copilot/server.py`
- Backed by tests: `tests/test_golazo_transition_workitem.py`

**Workspace-level state impact**
- Introduces/updates `global_state.json` with:
  - completed work items
  - `next_work_item`

## Confirmed Missing in Official 4.0.0
- Installed official package check showed:
  - `has_git_propose = False`
  - `has_transition_workitem = False`
- Official server references `.github/agents/Golazo-Copilot.md` pathing and does not expose these two tools.

## Additional Divergence (Not a net-new feature)
Yev's fork shifts instruction and role override paths to:
- `.github/copilot-instructions.md`
- `.github/roles/`

Official 4.0.0 uses:
- `.github/agents/Golazo-Copilot.md`
- `.github/agents/golazo-copilot/roles/`

This is a compatibility/pathing divergence, not a unique capability by itself.

## Bottom Line
Unique functional additions in Yev's fork that are not currently addressed in official Golazo 4.0.0:
1. `golazo_git_propose`
2. `golazo_transition_workitem` + `global_state.json` project-level orchestration

## Executive Value Summary
- `golazo_git_propose` strengthens change governance and auditability at the git-action intent layer.
- `golazo_transition_workitem` strengthens project flow control and cross-item orchestration.
- Together, they move Golazo from strictly work-item state management toward program-level operational control.
