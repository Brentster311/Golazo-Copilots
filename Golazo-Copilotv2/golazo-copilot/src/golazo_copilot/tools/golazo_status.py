"""golazo_status tool - Get comprehensive workflow status.

GCP-0051: Operations that gather independent data are run concurrently
via asyncio.gather + asyncio.to_thread for reduced latency.
"""

import asyncio
import re
from importlib import resources
from pathlib import Path

import yaml

from .. import __version__
from ..core.persistence import load_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..core.output_validator import parse_required_outputs, validate_all_outputs
from ..core.transitions import ROLE_ORDER
from ..roles.loader import load_role_instructions, get_role_content
from .golazo_transition import get_role_notes_path

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
        f"Use `golazo_capabilities(action='impact', files=[...])` to check affected features."
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


async def golazo_status(
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
            "message": f"No active work item '{work_item_id}'. Use golazo_create_workitem to start.",
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
    
    # GCP-0053: Filter closure-only outputs based on state
    closure_mode = getattr(state, 'closure_pending', False)
    output_specs = [s for s in output_specs if not s.closure_only or closure_mode]
    
    # ── GCP-0051: Parallel fan-out for independent operations ─────────
    # Each helper is sync (file I/O), so we wrap with asyncio.to_thread.
    # return_exceptions=True isolates failures per-operation.

    async def _async_validate_outputs():
        """Validate required outputs in a thread."""
        def _validate():
            results = []
            all_valid = True
            if output_specs:
                validation_result = validate_all_outputs(output_specs, workspace_root)
                all_valid = validation_result.valid
                for output in validation_result.outputs:
                    results.append({
                        "path": output["spec"].path_or_pattern,
                        "type": output["spec"].type,
                        "valid": output["valid"],
                    })
            return all_valid, results
        return await asyncio.to_thread(_validate)

    async def _async_check_missing_notes():
        """Check for missing role notes in a thread."""
        def _check():
            missing = []
            seen = set()
            for entry in state.role_history:
                if entry.exited_at is not None:
                    if entry.role not in seen:
                        notes_path = get_role_notes_path(work_item_id, entry.role, work_items_dir)
                        if not notes_path.exists():
                            missing.append(entry.role)
                        seen.add(entry.role)
            return missing
        return await asyncio.to_thread(_check)

    async def _async_stale_files():
        """Detect stale files in a thread."""
        return await asyncio.to_thread(_get_stale_files, workspace_root)

    async def _async_registry():
        """Parse registry hint in a thread."""
        return await asyncio.to_thread(_get_registry_hint, workspace_root)

    async def _async_progress():
        """Compute role progress in a thread."""
        return await asyncio.to_thread(_compute_role_progress, state)

    (
        output_result,
        missing_notes_result,
        stale_files_result,
        registry_result,
        progress_result,
    ) = await asyncio.gather(
        _async_validate_outputs(),
        _async_check_missing_notes(),
        _async_stale_files(),
        _async_registry(),
        _async_progress(),
        return_exceptions=True,
    )

    # ── Unwrap results with error isolation ───────────────────────────
    # If an operation raised, use a safe default so other data still shows.

    if isinstance(output_result, BaseException):
        outputs_complete = True
        required_outputs = []
    else:
        outputs_complete, required_outputs = output_result

    missing_notes = (
        [] if isinstance(missing_notes_result, BaseException) else missing_notes_result
    )

    stale_files = (
        [] if isinstance(stale_files_result, BaseException) else stale_files_result
    )

    registry_hint = (
        None if isinstance(registry_result, BaseException) else registry_result
    )

    role_progress = (
        {"roles": [], "roles_completed": 0, "roles_total": len(ROLE_ORDER)}
        if isinstance(progress_result, BaseException)
        else progress_result
    )

    # ── Assemble result (unchanged structure) ─────────────────────────

    # Generate next steps (with output remediation — GCP-0027)
    next_steps = _generate_next_steps(state, required_outputs, closure_pending=closure_mode)
    
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
    
    # GCP-0037: Per-file stale version reporting
    version_warning = None
    if stale_files:
        details = ", ".join(
            f"{s['file']} (v{s['deployed']} → v{s['source']})" for s in stale_files
        )
        version_warning = (
            f"{len(stale_files)} file(s) are stale: {details}. "
            f"Run golazo_bootstrap to update."
        )
    
    return {
        "active": True,
        "version": __version__,
        "work_item_id": state.work_item_id,
        "profile": state.profile,
        "current_phase": state.current_phase,
        "current_role": state.current_role,
        "closure_pending": closure_mode,
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
    closure_pending: bool = False,
) -> list[str]:
    """Generate intelligent next steps based on current state.
    
    Args:
        state: Current work item state
        required_outputs: List of output dicts with path/type/valid keys (GCP-0027)
        closure_pending: Whether the work item is in closure mode (GCP-0053)
    """
    steps = []
    
    # GCP-0053: Closure-specific guidance takes priority
    if closure_pending and state.current_role == "project-owner-assistant":
        steps.append("Perform closure: verify acceptance criteria, confirm final commit, create closure.md")
        steps.append("Update User Story status to IMPLEMENTED")
        # Still include output remediation
        _REMEDIATION_VERBS = {"file": "Create file", "dir": "Create directory"}
        if required_outputs:
            for output in required_outputs:
                if not output["valid"]:
                    verb = _REMEDIATION_VERBS.get(output["type"], f"Ensure {output['type']}")
                    steps.append(f"{verb}: {output['path']}")
        return steps
    
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
