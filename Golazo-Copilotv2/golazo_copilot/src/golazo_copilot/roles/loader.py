"""Role instruction loader."""

from pathlib import Path
from importlib import resources


def load_role_instructions(role: str, project_root: Path | None = None) -> str:
    """
    Load role instructions for a given role.
    
    Priority:
    1. Local .github/roles/{role}.md if exists
    2. Package defaults
    
    Args:
        role: Role name (e.g., "project-owner")
        project_root: Project root directory (defaults to cwd)
    
    Returns:
        Role instruction markdown content
    """
    if project_root is None:
        project_root = Path.cwd()
    
    # Try local first
    local_path = project_root / ".github" / "roles" / f"{role}.md"
    if local_path.exists():
        return local_path.read_text(encoding='utf-8')
    
    # Fall back to package defaults
    return load_default_role(role)


def load_default_role(role: str) -> str:
    """Load default role instructions from package."""
    try:
        # Try to load from package resources
        files = resources.files("golazo_copilot.roles.defaults")
        role_file = files.joinpath(f"{role}.md")
        return role_file.read_text(encoding='utf-8')
    except (FileNotFoundError, TypeError):
        # Return placeholder if not found
        return f"# {role}\n\nRole instructions not found. Please create .github/roles/{role}.md"


def has_local_role_override(role: str, project_root: Path | None = None) -> bool:
    """Check if a local role override exists."""
    if project_root is None:
        project_root = Path.cwd()
    local_path = project_root / ".github" / "roles" / f"{role}.md"
    return local_path.exists()
