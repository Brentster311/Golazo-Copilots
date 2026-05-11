"""Bootstrap tool for Golazo Copilot."""

from importlib import resources
from pathlib import Path

from golazo_copilot import __version__

# Workspace markers - at least one must exist
WORKSPACE_MARKERS = ["pyproject.toml", "package.json", "Cargo.toml", ".hg", "WorkItems"]

BOOTSTRAP_MODES = {"full", "orchestrator-only"}

AGENTS_ROOT = Path(".github") / "agents"
ORCHESTRATOR_REL_PATH = AGENTS_ROOT / "Golazo-Copilot.md"
ROLES_REL_DIR = AGENTS_ROOT / "golazo-copilot" / "roles"

# Default role files to copy
DEFAULT_ROLES = [
    "planner.md",
    "project-owner-assistant.md",
    "program-manager.md",
    "domain-expert.md",
    "quality-assurance.md",
    "architect.md",
    "developer.md",
    "refactor-expert.md",
    "builder.md",
    "documenter.md",
    "retrospective.md",
    "TechBestPractices.md",
]


def _is_workspace(path: Path) -> bool:
    """Check if path is a valid workspace root."""
    return any((path / marker).exists() for marker in WORKSPACE_MARKERS)


def _get_default_instructions() -> str:
    """Get default copilot instructions content from bootstrap-instructions.md."""
    try:
        # Read from package resource
        files = resources.files("golazo_copilot")
        # bootstrap-instructions.md is in the package root (copied during install)
        # Fall back to hardcoded if not found
        bootstrap_file = files.joinpath("bootstrap-instructions.md")
        content = bootstrap_file.read_text(encoding="utf-8")
        return content
    except (FileNotFoundError, TypeError):
        # Fall back to minimal hardcoded version
        return f'''<!-- Last Updated in Golazo Copilot Version: {__version__} -->
# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## REQUIRED: Before EVERY Response
1. Call `golazo_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the role instructions returned

## Starting a New Work Item
```
golazo_create_workitem(work_item_id="<id>", profile="complete")
```

## Role Transitions
```
golazo_transition(work_item_id="<id>", role="program-manager")
```

For full documentation, see the Golazo Copilot README.
'''


async def golazo_bootstrap(
    workspace_path: Path | str | None = None,
    force: bool = False,
    include_roles: bool = True,
    mode: str = "full",
    scope: str | None = "Workspace",
) -> dict:
    """
    Bootstrap Golazo Copilot in a workspace.
    
    Creates:
    - .github/agents/Golazo-Copilot.md
    - WorkItems/.gitkeep
    - .github/agents/golazo-copilot/roles/*.md (default role files)
    
    Args:
        workspace_path: Workspace root path (auto-detected if not provided)
        force: Overwrite existing files if they exist
        include_roles: Also copy default role files to
            .github/agents/golazo-copilot/roles/
        mode: Bootstrap mode. "full" scaffolds all files; "orchestrator-only"
            only creates/updates .github/agents/Golazo-Copilot.md
        scope: Install scope for orchestrator instructions. Supported values:
            Workspace and User. Omitted or empty behaves as Workspace.
    
    Returns:
        Dict with success status and list of created/skipped files.
    """
    # Resolve workspace path
    if workspace_path is None:
        workspace_path = Path.cwd()
    else:
        workspace_path = Path(workspace_path)

    if mode not in BOOTSTRAP_MODES:
        return {
            "success": False,
            "error": f"Invalid mode '{mode}'. Expected one of: full, orchestrator-only",
            "files_created": [],
            "files_skipped": [],
        }

    from golazo_copilot.dispatch.paths import (
        normalize_bootstrap_scope,
        resolve_orchestrator_bootstrap_path,
    )

    try:
        normalized_scope = normalize_bootstrap_scope(scope)
    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
            "files_created": [],
            "files_skipped": [],
        }
    
    # Validate workspace
    if not _is_workspace(workspace_path):
        return {
            "success": False,
            "error": f"Not a valid workspace. No workspace markers found ({', '.join(WORKSPACE_MARKERS)})",
            "files_created": [],
            "files_skipped": [],
        }
    
    files_created = []
    files_skipped = []

    # Create Golazo-Copilot.md spine file
    instructions_path = resolve_orchestrator_bootstrap_path(workspace_path, normalized_scope)
    instructions_path.parent.mkdir(parents=True, exist_ok=True)
    if instructions_path.exists() and not force:
        files_skipped.append(ORCHESTRATOR_REL_PATH.as_posix())
    else:
        instructions_path.write_text(_get_default_instructions(), encoding="utf-8")
        files_created.append(ORCHESTRATOR_REL_PATH.as_posix())

    if mode == "orchestrator-only":
        return {
            "success": True,
            "scope": normalized_scope,
            "target_path": str(instructions_path),
            "files_created": files_created,
            "files_skipped": files_skipped,
            "message": (
                f"Bootstrapped Golazo Copilot in {workspace_path} "
                f"(mode: orchestrator-only, scope: {normalized_scope})"
            ),
        }
    
    # Create WorkItems directory
    workitems_dir = workspace_path / "WorkItems"
    workitems_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .gitkeep
    gitkeep_path = workitems_dir / ".gitkeep"
    if not gitkeep_path.exists():
        gitkeep_path.write_text("", encoding="utf-8")
        files_created.append("WorkItems/.gitkeep")

    # Create capabilities.yaml from template, but never overwrite existing file.
    # This protects project-specific capability registry data even in force mode.
    capabilities_path = workspace_path / "capabilities.yaml"
    if capabilities_path.exists():
        files_skipped.append("capabilities.yaml")
    else:
        try:
            files_pkg = resources.files("golazo_copilot")
            template = files_pkg.joinpath("capabilities-template.yaml")
            capabilities_path.write_text(
                template.read_text(encoding="utf-8"), encoding="utf-8"
            )
            files_created.append("capabilities.yaml")
        except (FileNotFoundError, TypeError):
            pass  # Graceful degradation if resource missing
    
    # Optionally copy role files
    if include_roles:
        roles_dir = workspace_path / ROLES_REL_DIR
        roles_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load role files from package
            role_files = resources.files("golazo_copilot.roles.defaults")
            for role_name in DEFAULT_ROLES:
                role_file = role_files.joinpath(role_name)
                dest_path = roles_dir / role_name
                
                if dest_path.exists() and not force:
                    files_skipped.append(f"{ROLES_REL_DIR.as_posix()}/{role_name}")
                else:
                    content = role_file.read_text(encoding="utf-8")
                    dest_path.write_text(content, encoding="utf-8")
                    files_created.append(f"{ROLES_REL_DIR.as_posix()}/{role_name}")
        except Exception:
            # If package resources fail, still succeed but note it
            pass
    
    return {
        "success": True,
        "scope": normalized_scope,
        "target_path": str(instructions_path),
        "files_created": files_created,
        "files_skipped": files_skipped,
        "message": (
            f"Bootstrapped Golazo Copilot in {workspace_path} "
            f"(mode: full, scope: {normalized_scope})"
        ),
    }
