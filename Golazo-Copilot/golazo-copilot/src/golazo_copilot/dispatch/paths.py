"""Path and workflow preflight helpers for server dispatch."""

from pathlib import Path

AGENTS_ROOT = Path(".github") / "agents"
ORCHESTRATOR_REL_PATH = AGENTS_ROOT / "Golazo-Copilot.md"
VALID_BOOTSTRAP_SCOPES = ("Workspace", "User")


def resolve_work_items_dir(workspace_path: str | None) -> Path:
    """Resolve workspace_path to an absolute work_items_dir Path."""
    if not workspace_path:
        raise ValueError("workspace_path is required — MCP servers cannot rely on cwd")
    return (Path(workspace_path) / "WorkItems").resolve()


def resolve_workspace_orchestrator_instructions_path(workspace_path: Path | str) -> Path:
    """Return the workspace-local orchestrator instructions path."""
    return Path(workspace_path) / ORCHESTRATOR_REL_PATH


def resolve_user_orchestrator_instructions_path() -> Path:
    """Return the active user's Copilot orchestrator instructions path."""
    return Path.home() / ".copilot" / ORCHESTRATOR_REL_PATH


def normalize_bootstrap_scope(scope: str | None) -> str:
    """Normalize omitted/empty scope to Workspace and validate supported values."""
    normalized = (scope or "Workspace").strip() or "Workspace"
    if normalized not in VALID_BOOTSTRAP_SCOPES:
        supported = ", ".join(VALID_BOOTSTRAP_SCOPES)
        raise ValueError(
            f"Invalid scope '{normalized}'. Expected one of: {supported}"
        )
    return normalized


def resolve_orchestrator_bootstrap_path(workspace_path: Path | str, scope: str | None) -> Path:
    """Resolve the bootstrap target path for the requested scope."""
    normalized = normalize_bootstrap_scope(scope)
    if normalized == "User":
        return resolve_user_orchestrator_instructions_path()
    return resolve_workspace_orchestrator_instructions_path(workspace_path)


def has_orchestrator_instructions(workspace_path: str | None) -> bool:
    """Return True when orchestrator instructions exist in workspace or user scope."""
    if not workspace_path:
        return False
    return resolve_workspace_orchestrator_instructions_path(workspace_path).exists() or resolve_user_orchestrator_instructions_path().exists()
