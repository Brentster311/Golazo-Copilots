"""golazo_capabilities tool - Query project capability registry for impact analysis."""

from collections import defaultdict, deque
from pathlib import Path
import shutil

import yaml


CANONICAL_REGISTRY_REL_PATH = Path("WorkItems") / "capabilities.yaml"
LEGACY_REGISTRY_REL_PATH = Path("capabilities.yaml")


def _resolve_registry_path(workspace_path: Path) -> Path:
    """Resolve canonical registry location, migrating legacy file when needed."""
    canonical_path = workspace_path / CANONICAL_REGISTRY_REL_PATH
    legacy_path = workspace_path / LEGACY_REGISTRY_REL_PATH

    if canonical_path.exists():
        return canonical_path

    if legacy_path.exists():
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(legacy_path), str(canonical_path))
        except OSError as e:
            raise ValueError(
                f"Failed to move legacy capabilities registry from {legacy_path} "
                f"to {canonical_path}: {e}"
            ) from e
        return canonical_path

    raise ValueError(
        "Capability registry not found. Expected canonical path: "
        f"{CANONICAL_REGISTRY_REL_PATH.as_posix()}"
    )


def _load_registry(workspace_path: Path) -> dict:
    """Load capabilities registry from canonical path.

    Raises ValueError when the file is missing or malformed.
    """
    yaml_path = _resolve_registry_path(workspace_path)

    content = yaml_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(
            f"Failed to parse {CANONICAL_REGISTRY_REL_PATH.as_posix()}: {e}"
        ) from e

    if not isinstance(data, dict) or "capabilities" not in data:
        raise ValueError(
            f"{CANONICAL_REGISTRY_REL_PATH.as_posix()} must contain a 'capabilities' key"
        )

    return data


def _build_depended_on_by(capabilities: list[dict]) -> dict[str, list[str]]:
    """Compute inverse dependency map: for each capability, who depends on it."""
    result: dict[str, list[str]] = defaultdict(list)
    for cap in capabilities:
        for dep in cap.get("depends_on", []):
            result[dep].append(cap["name"])
    return dict(result)


def _normalize_path(path: str) -> str:
    """Normalize path separators to forward slashes."""
    return path.replace("\\", "/")


def _match_files(input_files: list[str], key_files: list[str]) -> bool:
    """Check if any input file matches any key_file.
    
    Matching strategy:
    1. Exact match (after normalization)
    2. Suffix match (input is a suffix of key_file)
    """
    normalized_inputs = [_normalize_path(f) for f in input_files]
    normalized_keys = [_normalize_path(f) for f in key_files]
    
    for inp in normalized_inputs:
        for key in normalized_keys:
            # Exact match
            if inp == key:
                return True
            # Suffix match: input is a suffix of key_file
            if key.endswith("/" + inp) or key.endswith(inp):
                return True
    return False


def _get_transitive_dependents(
    start_names: set[str],
    depended_on_by: dict[str, list[str]],
) -> list[str]:
    """BFS to find all transitive dependents, with cycle detection."""
    visited: set[str] = set(start_names)
    queue = deque(start_names)
    result: list[str] = []
    
    while queue:
        current = queue.popleft()
        for dependent in depended_on_by.get(current, []):
            if dependent not in visited:
                visited.add(dependent)
                result.append(dependent)
                queue.append(dependent)
    
    return result


async def golazo_capabilities(
    action: str,
    capability: str | None = None,
    files: list[str] | None = None,
    workspace_path: Path | str | None = None,
) -> dict:
    """Query the project capability registry.
    
    Args:
        action: "list" | "show" | "impact" | "validate"
        capability: Capability name (required for "show")
        files: List of file paths (required for "impact")
        workspace_path: Workspace root containing WorkItems/capabilities.yaml
    
    Returns:
        dict with results varying by action
    """
    if workspace_path is None:
        workspace_path = Path.cwd()
    elif isinstance(workspace_path, str):
        workspace_path = Path(workspace_path)
    
    # Load registry
    try:
        data = _load_registry(workspace_path)
    except ValueError as e:
        return {"success": False, "error": str(e)}
    
    capabilities = data.get("capabilities") or []
    cap_by_name = {c["name"]: c for c in capabilities}
    depended_on_by = _build_depended_on_by(capabilities)
    
    if action == "list":
        return {
            "success": True,
            "capabilities": [
                {"name": c["name"], "description": c.get("description", "")}
                for c in capabilities
            ],
        }
    
    elif action == "show":
        if not capability:
            return {"success": False, "error": "capability parameter is required for action='show'"}
        
        cap = cap_by_name.get(capability)
        if not cap:
            return {"success": False, "error": f"Capability '{capability}' not found in registry"}
        
        return {
            "success": True,
            "capability": {
                "name": cap["name"],
                "description": cap.get("description", ""),
                "key_files": cap.get("key_files", []),
                "contracts": cap.get("contracts", []),
                "depends_on": cap.get("depends_on", []),
                "depended_on_by": depended_on_by.get(cap["name"], []),
            },
        }
    
    elif action == "impact":
        if not files:
            return {"success": False, "error": "files parameter is required for action='impact'"}
        
        # Find directly affected capabilities
        directly_affected = []
        for cap in capabilities:
            if _match_files(files, cap.get("key_files", [])):
                directly_affected.append(cap)
        
        direct_names = {c["name"] for c in directly_affected}
        
        # Find transitive dependents
        transitive_names = _get_transitive_dependents(direct_names, depended_on_by)
        transitively_affected = [
            cap_by_name[name] for name in transitive_names if name in cap_by_name
        ]
        
        return {
            "success": True,
            "directly_affected": [
                {"name": c["name"], "description": c.get("description", "")}
                for c in directly_affected
            ],
            "transitively_affected": [
                {"name": c["name"], "description": c.get("description", "")}
                for c in transitively_affected
            ],
        }
    
    elif action == "validate":
        results = []
        for cap in capabilities:
            missing = []
            for f in cap.get("key_files", []):
                if not (workspace_path / f).exists():
                    missing.append(f)
            results.append({
                "name": cap["name"],
                "valid": len(missing) == 0,
                "missing_files": missing,
            })
        
        return {
            "success": True,
            "results": results,
        }
    
    else:
        return {"success": False, "error": f"Unknown action: {action}. Valid actions: list, show, impact, validate"}
