# -*- coding: utf-8 -*-
"""golazo_role_context tool — Assemble a self-contained context bundle for a role.

GCP-0049: Role Context Bundler MCP Tool
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from ..core.persistence import load_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..core.transitions import ROLE_ORDER
from ..roles.loader import load_role_instructions
from ..tools.golazo_transition import ROLE_SUFFIX_MAP, get_role_notes_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _parse_front_matter(role_content: str) -> dict | None:
    """Extract YAML front-matter from role markdown content.

    Returns the parsed dict, or *None* if no front-matter block is found.
    """
    m = _FRONT_MATTER_RE.match(role_content)
    if not m:
        return None
    raw = m.group(1)
    try:
        return yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        # Front-matter may contain {id} tokens that YAML treats as flow
        # mappings.  Quote any bare values that start with '{'.
        lines = []
        for line in raw.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("- {"):
                # Turn  `- {id}-Foo.md`  into  `- "{id}-Foo.md"`
                indent = line[: len(line) - len(stripped)]
                value = stripped[2:].strip()
                lines.append(f'{indent}- "{value}"')
            else:
                lines.append(line)
        try:
            return yaml.safe_load("\n".join(lines)) or {}
        except yaml.YAMLError:
            return None


def _get_previous_role(role: str) -> str | None:
    """Return the role immediately before *role* in ROLE_ORDER, or None for the first."""
    if role not in ROLE_ORDER:
        return None
    idx = ROLE_ORDER.index(role)
    return ROLE_ORDER[idx - 1] if idx > 0 else None


def _resolve_artifact_path(
    pattern: str, work_item_id: str, work_items_dir: Path, project_root: Path | None
) -> Path:
    """Resolve an artifact pattern to an absolute path.

    Patterns from the role front-matter are workspace-root-relative
    (e.g. ``WorkItems/{id}/{id}-User-Story.md``).  If the pattern starts
    with ``WorkItems/`` we resolve from *project_root* (or the parent of
    *work_items_dir*).  Otherwise we treat it as relative to the work-item
    directory.
    """
    relative = pattern.replace("{id}", work_item_id)
    if relative.startswith("WorkItems/") or relative.startswith("WorkItems\\"):
        root = project_root or work_items_dir.parent
        return root / relative
    # Legacy / shorthand: relative to work-item dir
    return work_items_dir / work_item_id / relative


# ---------------------------------------------------------------------------
# Main tool
# ---------------------------------------------------------------------------

async def golazo_role_context(
    work_item_id: str,
    role: str | None = None,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    project_root: Path | None = None,
    max_bundle_size: int = 100_000,
) -> dict:
    """Assemble a self-contained context bundle for *role* in *work_item_id*.

    Parameters
    ----------
    work_item_id:
        Work-item identifier (e.g. ``GCP-0049``).
    role:
        Target role name.  If ``None``, the current role from ``state.json``
        is used.
    work_items_dir:
        Absolute path to the ``WorkItems/`` directory.
    project_root:
        Workspace root (used to locate ``.github/roles/`` overrides).
    max_bundle_size:
        Maximum bundle size in bytes.  Artifacts are truncated when exceeded.

    Returns
    -------
    dict
        ``status`` is ``"ok"`` or ``"error"``.  On success the dict also
        contains ``bundle`` (str), ``artifact_count`` (int),
        ``total_size`` (int), and ``truncated`` (bool).
    """

    # ------------------------------------------------------------------
    # 1. Validate work item exists
    # ------------------------------------------------------------------
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "status": "error",
            "error": f"Work item '{work_item_id}' not found in {work_items_dir}",
        }

    # ------------------------------------------------------------------
    # 2. Load state & resolve role
    # ------------------------------------------------------------------
    try:
        state = load_state(work_item_id, work_items_dir)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": f"Failed to load state: {exc}"}

    effective_role = role or state.current_role

    # ------------------------------------------------------------------
    # 3. Load role instructions
    # ------------------------------------------------------------------
    role_content = load_role_instructions(effective_role, project_root)

    # ------------------------------------------------------------------
    # 4. Parse front-matter → inputs list
    # ------------------------------------------------------------------
    fm = _parse_front_matter(role_content)
    has_front_matter = fm is not None
    input_patterns: list[str] = (fm or {}).get("inputs", []) or []

    # ------------------------------------------------------------------
    # 5. Read input artifacts
    # ------------------------------------------------------------------
    artifacts: list[dict] = []  # {path, content, size, exists}
    for pattern in input_patterns:
        abs_path = _resolve_artifact_path(pattern, work_item_id, work_items_dir, project_root)
        if abs_path.exists():
            content = abs_path.read_text(encoding="utf-8")
            artifacts.append({
                "path": pattern.replace("{id}", work_item_id),
                "content": content,
                "size": len(content),
                "exists": True,
            })
        else:
            artifacts.append({
                "path": pattern.replace("{id}", work_item_id),
                "content": "[not yet created]",
                "size": 0,
                "exists": False,
            })

    # ------------------------------------------------------------------
    # 6. Load previous role notes
    # ------------------------------------------------------------------
    prev_role = _get_previous_role(effective_role)
    prev_notes_content: str
    if prev_role is None:
        prev_notes_content = "[no previous role]"
    else:
        prev_notes_path = get_role_notes_path(work_item_id, prev_role, work_items_dir)
        if prev_notes_path.exists():
            prev_notes_content = prev_notes_path.read_text(encoding="utf-8")
        else:
            prev_notes_content = f"[no notes found for {prev_role}]"

    # ------------------------------------------------------------------
    # 7. Build the state summary
    # ------------------------------------------------------------------
    state_summary = (
        f"- **Work Item:** {state.work_item_id}\n"
        f"- **Current Role:** {state.current_role}\n"
        f"- **Phase:** {state.current_phase}\n"
        f"- **Deviations:** {len(state.deviations)}\n"
    )

    # ------------------------------------------------------------------
    # 8. Assemble bundle (before truncation)
    # ------------------------------------------------------------------
    role_instructions_section = f"## Role Instructions\n\n{role_content}\n"
    state_section = f"## Current State\n\n{state_summary}\n"
    prev_notes_section = f"## Previous Role Notes\n\n{prev_notes_content}\n"

    # Build artifacts section
    if not has_front_matter:
        artifacts_section = (
            "## Input Artifacts\n\n"
            "> **Warning:** This role file has no front-matter `inputs:` declaration. "
            "No artifacts were loaded. Consider adding YAML front-matter to the role file.\n"
        )
    elif not artifacts:
        artifacts_section = "## Input Artifacts\n\n(none declared)\n"
    else:
        artifact_lines: list[str] = ["## Input Artifacts\n"]
        for art in artifacts:
            artifact_lines.append(f"### {art['path']}\n")
            if art["exists"]:
                artifact_lines.append(f"```\n{art['content']}\n```\n")
            else:
                artifact_lines.append(f"{art['content']}\n")
        artifacts_section = "\n".join(artifact_lines)

    # ------------------------------------------------------------------
    # 9. Size guard — truncate artifacts if needed
    # ------------------------------------------------------------------
    # Protected sections (never truncated)
    protected_size = len(role_instructions_section) + len(state_section) + len(prev_notes_section)
    truncated = False

    if protected_size + len(artifacts_section) > max_bundle_size:
        # Need to truncate artifacts
        budget = max(0, max_bundle_size - protected_size)
        if budget < 100:
            # Almost no room — just show paths
            artifact_lines_trunc: list[str] = ["## Input Artifacts\n"]
            for art in artifacts:
                artifact_lines_trunc.append(
                    f"### {art['path']}\n\n"
                    f"[truncated — full file at {art['path']}]\n"
                )
            artifacts_section = "\n".join(artifact_lines_trunc)
            truncated = True
        else:
            # Proportional truncation of large artifacts
            existing_artifacts = [a for a in artifacts if a["exists"]]
            total_artifact_content = sum(a["size"] for a in existing_artifacts)

            if total_artifact_content > budget:
                # Truncate proportionally
                artifact_lines_trunc = ["## Input Artifacts\n"]
                per_artifact_budget = max(50, budget // max(len(existing_artifacts), 1))

                for art in artifacts:
                    artifact_lines_trunc.append(f"### {art['path']}\n")
                    if not art["exists"]:
                        artifact_lines_trunc.append(f"{art['content']}\n")
                    elif art["size"] <= per_artifact_budget:
                        artifact_lines_trunc.append(f"```\n{art['content']}\n```\n")
                    else:
                        truncated_content = art["content"][:per_artifact_budget]
                        artifact_lines_trunc.append(
                            f"```\n{truncated_content}\n```\n"
                            f"[truncated — full file at {art['path']}]\n"
                        )
                        truncated = True

                artifacts_section = "\n".join(artifact_lines_trunc)

    # ------------------------------------------------------------------
    # 10. Final assembly
    # ------------------------------------------------------------------
    bundle = (
        role_instructions_section + "\n"
        + state_section + "\n"
        + artifacts_section + "\n"
        + prev_notes_section
    )

    return {
        "status": "ok",
        "bundle": bundle,
        "artifact_count": sum(1 for a in artifacts if a["exists"]),
        "total_size": len(bundle),
        "truncated": truncated,
        "role": effective_role,
        "work_item_id": work_item_id,
    }
