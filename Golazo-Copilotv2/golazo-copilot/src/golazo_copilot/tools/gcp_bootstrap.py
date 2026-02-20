"""Bootstrap tool for Golazo Copilot."""

from pathlib import Path
from importlib import resources
import shutil

from golazo_copilot import __version__


# Workspace markers - at least one must exist
WORKSPACE_MARKERS = ["pyproject.toml", "package.json", "Cargo.toml", ".hg", "WorkItems"]

# Default role files to copy
DEFAULT_ROLES = [
    "project-owner-assistant.md",
    "program-manager.md",
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
1. Call `gcp_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the role instructions returned

## Starting a New Work Item
```
gcp_create_workitem(work_item_id="<id>", profile="complete")
```

## Role Transitions
```
gcp_transition(work_item_id="<id>", role="program-manager")
```

For full documentation, see the Golazo Copilot README.
'''


async def gcp_bootstrap(
    workspace_path: Path | str | None = None,
    force: bool = False,
    include_roles: bool = True,
) -> dict:
    """
    Bootstrap Golazo Copilot in a workspace.
    
    Creates:
    - .github/copilot-instructions.md
    - WorkItems/.gitkeep
    - .github/roles/*.md (default role files)
    
    Args:
        workspace_path: Workspace root path (auto-detected if not provided)
        force: Overwrite existing files if they exist
        include_roles: Also copy default role files to .github/roles/
    
    Returns:
        Dict with success status and list of created/skipped files.
    """
    # Resolve workspace path
    if workspace_path is None:
        workspace_path = Path.cwd()
    else:
        workspace_path = Path(workspace_path)
    
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
    
    # Create .github directory
    github_dir = workspace_path / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)
    
    # Create copilot-instructions.md
    instructions_path = github_dir / "copilot-instructions.md"
    if instructions_path.exists() and not force:
        files_skipped.append(".github/copilot-instructions.md")
    else:
        instructions_path.write_text(_get_default_instructions(), encoding="utf-8")
        files_created.append(".github/copilot-instructions.md")
    
    # Create WorkItems directory
    workitems_dir = workspace_path / "WorkItems"
    workitems_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .gitkeep
    gitkeep_path = workitems_dir / ".gitkeep"
    if not gitkeep_path.exists():
        gitkeep_path.write_text("", encoding="utf-8")
        files_created.append("WorkItems/.gitkeep")

    # Create capabilities.yaml from template
    capabilities_path = workspace_path / "capabilities.yaml"
    if capabilities_path.exists() and not force:
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
        roles_dir = github_dir / "roles"
        roles_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load role files from package
            role_files = resources.files("golazo_copilot.roles.defaults")
            for role_name in DEFAULT_ROLES:
                role_file = role_files.joinpath(role_name)
                dest_path = roles_dir / role_name
                
                if dest_path.exists() and not force:
                    files_skipped.append(f".github/roles/{role_name}")
                else:
                    content = role_file.read_text(encoding="utf-8")
                    dest_path.write_text(content, encoding="utf-8")
                    files_created.append(f".github/roles/{role_name}")
        except Exception as e:
            # If package resources fail, still succeed but note it
            pass
    
    return {
        "success": True,
        "files_created": files_created,
        "files_skipped": files_skipped,
        "message": f"Bootstrapped Golazo Copilot in {workspace_path}",
    }
