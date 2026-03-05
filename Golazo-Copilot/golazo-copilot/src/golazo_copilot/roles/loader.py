"""Role instruction loader."""

from importlib import resources
from pathlib import Path


def _candidate_local_paths(project_root: Path, role: str) -> list[Path]:
    """Return local role override search paths in priority order."""
    return [
        project_root / ".github" / "agents" / "golazo-copilot" / "roles" / f"{role}.md",
        project_root / ".github" / "roles" / f"{role}.md",  # legacy fallback
    ]


def load_role_instructions(role: str, project_root: Path | None = None) -> str:
    """
    Load role instructions for a given role.
    
    Priority:
    1. Local .github/agents/golazo-copilot/roles/{role}.md if exists
    2. Local .github/roles/{role}.md (legacy fallback)
    3. Package defaults
    
    Args:
        role: Role name (e.g., "project-owner")
        project_root: Project root directory (defaults to cwd)
    
    Returns:
        Role instruction markdown content
    """
    if project_root is None:
        project_root = Path.cwd()
    
    # Try local first
    for local_path in _candidate_local_paths(project_root, role):
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
        return (
            f"# {role}\n\nRole instructions not found. "
            f"Please create .github/agents/golazo-copilot/roles/{role}.md"
        )


def has_local_role_override(role: str, project_root: Path | None = None) -> bool:
    """Check if a local role override exists."""
    if project_root is None:
        project_root = Path.cwd()
    return any(path.exists() for path in _candidate_local_paths(project_root, role))


def get_role_content(role: str, project_root: Path | None = None) -> str:
    """
    Get raw role file content for parsing (without version update).
    
    Args:
        role: Role name
        project_root: Project root directory
        
    Returns:
        Raw role file content
    """
    if project_root is None:
        project_root = Path.cwd()
    
    # Try local first
    for local_path in _candidate_local_paths(project_root, role):
        if local_path.exists():
            return local_path.read_text(encoding='utf-8')
    
    # Fall back to package defaults
    try:
        files = resources.files("golazo_copilot.roles.defaults")
        role_file = files.joinpath(f"{role}.md")
        return role_file.read_text(encoding='utf-8')
    except (FileNotFoundError, TypeError):
        return ""
