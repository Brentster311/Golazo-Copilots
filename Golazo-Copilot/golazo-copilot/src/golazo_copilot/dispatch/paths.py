"""Path and workflow preflight helpers for server dispatch."""

from pathlib import Path


def resolve_work_items_dir(workspace_path: str | None) -> Path:
    """Resolve workspace_path to an absolute work_items_dir Path."""
    if not workspace_path:
        raise ValueError("workspace_path is required — MCP servers cannot rely on cwd")
    return (Path(workspace_path) / "WorkItems").resolve()


def has_orchestrator_instructions(workspace_path: str | None) -> bool:
    """Return True when .github/agents/Golazo-Copilot.md exists for workspace."""
    if not workspace_path:
        return False
    return (
        Path(workspace_path)
        / ".github"
        / "agents"
        / "Golazo-Copilot.md"
    ).exists()
