"""gcp_status tool - Get comprehensive workflow status."""

import re
from importlib import resources
from pathlib import Path

import yaml

from .. import __version__
from ..core.persistence import load_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..core.output_validator import parse_required_outputs, validate_all_outputs
from ..core.transitions import ROLE_ORDER
from ..roles.loader import load_role_instructions, get_role_content
from .gcp_transition import get_role_notes_path

_VERSION_PATTERN = re.compile(r'<!-- Last Updated in Golazo Copilot Version: ([\d.]+) -->')

# Mapping: (deployed relative path, source package resource info)
# Each entry: (deployed_rel_path, package_name, resource_filename)
_DEPLOYED_TO_SOURCE: list[tuple[str, str, str]] = [
    (".github/copilot-instructions.md", "golazo_copilot", "bootstrap-instructions.md"),
    (".github/roles/project-owner-assistant.md", "golazo_copilot.roles.defaults", "project-owner-assistant.md"),
    (".github/roles/program-manager.md", "golazo_copilot.roles.defaults", "program-manager.md"),
    (".github/roles/quality-assurance.md", "golazo_copilot.roles.defaults", "quality-assurance.md"),
    (".github/roles/architect.md", "golazo_copilot.roles.defaults", "architect.md"),
    (".github/roles/developer.md", "golazo_copilot.roles.defaults", "developer.md"),
    (".github/roles/refactor-expert.md", "golazo_copilot.roles.defaults", "refactor-expert.md"),
    (".github/roles/builder.md", "golazo_copilot.roles.defaults", "builder.md"),
    (".github/roles/documenter.md", "golazo_copilot.roles.defaults", "documenter.md"),
    (".github/roles/retrospective.md", "golazo_copilot.roles.defaults", "retrospective.md"),
    (".github/roles/TechBestPractices.md", "golazo_copilot.roles.defaults", "TechBestPractices.md"),
]


def _extract_version(content: str) -> str | None:
    """Extract version from a version comment in content."""
    match = _VERSION_PATTERN.search(content)
    return match.group(1) if match else None


def _get_source_version(package_name: str, resource_filename: str) -> str | None:
    """Read a source file from the installed package and extract its version."""
    try:
        files = resources.files(package_name)
        content = files.joinpath(resource_filename).read_text(encoding="utf-8")
        return _extract_version(content)
    except Exception:
        return None


def _get_stale_files(workspace_root: Path) -> list[dict]:
    """Compare each deployed file's version against its source counterpart.
    
    Returns list of {"file": str, "deployed": str, "source": str} for stale files.
    Files that are missing, unreadable, or have no version comment are skipped.
    """
    stale = []
    for deployed_rel, pkg_name, res_name in _DEPLOYED_TO_SOURCE:
        deployed_path = workspace_root / deployed_rel
        if not deployed_path.exists():
            continue
        try:
            deployed_content = deployed_path.read_text(encoding="utf-8")
        except Exception:
            continue
        deployed_ver = _extract_version(deployed_content)
        if deployed_ver is None:
            continue
        source_ver = _get_source_version(pkg_name, res_name)
        if source_ver is None:
            continue
        if deployed_ver != source_ver:
            stale.append({
                "file": deployed_rel.split("/")[-1],
                "deployed": deployed_ver,
                "source": source_ver,
            })
    return stale


def _get_registry_hint(workspace_root: Path) -> str | None:
    """Return a capability registry hint, or None if no capabilities.yaml.

    - File absent → None (silent)
    - Malformed YAML → warning string
    - Missing 'capabilities' key → warning string
    - Valid → count string with usage hint
    """
    yaml_path = workspace_root / "capabilities.yaml"
    if not yaml_path.exists():
        return None
    try:
        content = yaml_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except Exception as e:
        return f"Capability Registry: capabilities.yaml exists but failed to parse: {e}"
    if not isinstance(data, dict) or "capabilities" not in data:
        return "Capability Registry: capabilities.yaml missing 'capabilities' key"
    caps = data["capabilities"]
    count = len(caps) if isinstance(caps, list) else 0
    return (
        f"Capability Registry: {count} capability(ies) found. "
        f"Use `gcp_capabilities(action='impact', files=[...])` to check affected features."
    )


def _compute_role_progress(state) -> dict:
    """Compute role progress from state's role_history.
    
    Returns dict with:
        roles: list of {"role": str, "status": "completed"|"in-progress"|"pending"}
        roles_completed: int
        roles_total: int
    """
    # Build latest entry per role from history
    latest: dict[str, object] = {}
    for entry in state.role_history:
        latest[entry.role] = entry
    
    roles = []
    completed = 0
    for role in ROLE_ORDER:
        entry = latest.get(role)
        if entry and entry.exited_at is not None:
            status = "completed"
            completed += 1
        elif role == state.current_role:
            status = "in-progress"
        else:
            status = "pending"
        roles.append({"role": role, "status": status})
    
    return {
        "roles": roles,
        "roles_completed": completed,
        "roles_total": len(ROLE_ORDER),
    }


async def gcp_status(
    work_item_id: str,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    project_root: Path | None = None,
) -> dict:
    """
    Get comprehensive workflow status for a work item.
    
    Args:
        work_item_id: Work item identifier
        work_items_dir: Work items directory
        project_root: Project root for local role overrides
    
    Returns:
        Dict with full workflow status
    """
    # Check work item exists
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "active": False,
            "message": f"No active work item '{work_item_id}'. Use gcp_create_workitem to start.",
            "version": __version__,
        }
    
    # Load state
    state = load_state(work_item_id, work_items_dir)
    
    # Load role instructions
    role_instructions = load_role_instructions(state.current_role, project_root)
    
    # GCP-0025: Validate required outputs for current role
    # (Moved before _generate_next_steps so remediation can be included — AR-1)
    workspace_root = work_items_dir.parent
    role_content = get_role_content(state.current_role, workspace_root)
    output_specs = parse_required_outputs(role_content, work_item_id)
    
    required_outputs = []
    outputs_complete = True
    if output_specs:
        validation_result = validate_all_outputs(output_specs, workspace_root)
        outputs_complete = validation_result.valid
        for output in validation_result.outputs:
            required_outputs.append({
                "path": output["spec"].path_or_pattern,
                "type": output["spec"].type,
                "valid": output["valid"],
            })
    
    # Generate next steps (with output remediation — GCP-0027)
    next_steps = _generate_next_steps(state, required_outputs)
    
    # Build deviations list
    deviations = [
        {
            "id": d.id,
            "action": d.action,
            "reason": d.reason,
            "timestamp": d.timestamp.isoformat(),
            "consumed": d.consumed,
        }
        for d in state.deviations
    ]
    
    # Check for missing role notes (completed roles only)
    missing_notes = []
    seen_roles = set()
    for entry in state.role_history:
        if entry.exited_at is not None:  # Role has been exited (completed)
            if entry.role not in seen_roles:
                notes_path = get_role_notes_path(work_item_id, entry.role, work_items_dir)
                if not notes_path.exists():
                    missing_notes.append(entry.role)
                seen_roles.add(entry.role)
    
    # GCP-0037: Per-file stale version reporting
    stale_files = _get_stale_files(workspace_root)
    version_warning = None
    if stale_files:
        details = ", ".join(
            f"{s['file']} (v{s['deployed']} → v{s['source']})" for s in stale_files
        )
        version_warning = (
            f"{len(stale_files)} file(s) are stale: {details}. "
            f"Run gcp_bootstrap to update."
        )
    
    # GCP-0033: Compute role progress
    role_progress = _compute_role_progress(state)

    # GCP-0042: Capability registry hint
    registry_hint = _get_registry_hint(workspace_root)
    
    return {
        "active": True,
        "version": __version__,
        "work_item_id": state.work_item_id,
        "profile": state.profile,
        "current_phase": state.current_phase,
        "current_role": state.current_role,
        "required_outputs": {
            "complete": outputs_complete,
            "outputs": required_outputs,
        },
        "role_progress": role_progress,
        "deviations": deviations,
        "missing_notes": missing_notes,
        "version_warning": version_warning,
        "registry_hint": registry_hint,
        "role_instructions": role_instructions,
        "next_steps": next_steps,
    }


def _generate_next_steps(
    state,
    required_outputs: list[dict] | None = None,
) -> list[str]:
    """Generate intelligent next steps based on current state.
    
    Args:
        state: Current work item state
        required_outputs: List of output dicts with path/type/valid keys (GCP-0027)
    """
    steps = []
    
    # GCP-0027: Add remediation for missing required outputs
    _REMEDIATION_VERBS = {"file": "Create file", "dir": "Create directory"}
    if required_outputs:
        for output in required_outputs:
            if not output["valid"]:
                verb = _REMEDIATION_VERBS.get(output["type"], f"Ensure {output['type']}")
                steps.append(f"{verb}: {output['path']}")
    
    if state.current_phase == "definition":
        steps.append("Complete current role responsibilities, then transition to next role")
    
    elif state.current_phase == "development":
        if state.current_role == "developer":
            steps.append("Implement feature following TDD")
        elif state.current_role == "refactor-expert":
            steps.append("Review code for refactoring opportunities")
    
    elif state.current_phase == "completion":
        if state.current_role == "documenter":
            steps.append("Update documentation")
        elif state.current_role == "builder":
            steps.append("Build and verify")
        elif state.current_role == "retrospective":
            steps.append("Conduct retrospective")
    
    return steps if steps else ["Continue with current role responsibilities"]
