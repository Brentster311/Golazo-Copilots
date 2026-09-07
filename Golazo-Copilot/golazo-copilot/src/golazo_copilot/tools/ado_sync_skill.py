"""Package-resource installation for the Golazo ADO Sync skill."""

import shutil
import tempfile
from importlib import resources
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

ADO_SYNC_SKILL_NAME = "golazo-ado-sync"
ADO_SYNC_CONFIG_LABELS = {
    "organization": "Organization",
    "project": "Project",
    "team": "Team",
    "board": "Board",
    "work_item_type": "Work item type",
    "area": "Area",
    "iteration": "Iteration",
    "assignee": "Assignee",
    "planned_swimlane_field": "Planned swimlane field",
    "board_column_field": "Board column field",
    "board_done_field": "Board done field",
}


def get_ado_sync_default_config() -> dict[str, str]:
    """Load the canonical packaged Golazo ADO Sync defaults."""
    skill_root = resources.files("golazo_copilot").joinpath("skills").joinpath(ADO_SYNC_SKILL_NAME)
    raw = skill_root.joinpath("defaults.yaml").read_text(encoding="utf-8")
    loaded = yaml.safe_load(raw)
    if not isinstance(loaded, dict):
        raise ValueError("Packaged golazo-ado-sync defaults must be a mapping")
    return {str(key): value for key, value in loaded.items()}


def effective_ado_sync_config(overrides: dict[str, Any] | None) -> tuple[dict[str, str], str]:
    """Merge and validate caller overrides against packaged defaults."""
    defaults = get_ado_sync_default_config()
    unknown = set(overrides or {}) - set(defaults)
    if unknown:
        raise ValueError(f"Unknown golazo-ado-sync configuration field: {sorted(unknown)[0]}")

    effective: dict[str, Any] = {**defaults, **(overrides or {})}
    for name in ADO_SYNC_CONFIG_LABELS:
        value = effective.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"golazo-ado-sync configuration field '{name}' must be a non-empty string")
    source = "defaults" if effective == defaults else "customized"
    return effective, source


def _render_skill_config(skill_markdown: str, config: dict[str, str]) -> str:
    lines = skill_markdown.splitlines()
    try:
        section_start = lines.index("## Fixed Configuration") + 1
        section_end = next(
            index
            for index in range(section_start, len(lines))
            if lines[index].startswith("## ")
        )
    except (ValueError, StopIteration) as exc:
        raise ValueError("Packaged golazo-ado-sync skill has no bounded Fixed Configuration section") from exc

    label_to_key = {label: key for key, label in ADO_SYNC_CONFIG_LABELS.items()}
    rendered_keys: set[str] = set()
    for index in range(section_start, section_end):
        line = lines[index]
        if not line.startswith("- ") or ": `" not in line:
            continue
        label = line[2:].split(": `", 1)[0]
        key = label_to_key.get(label)
        if key is not None:
            lines[index] = f"- {label}: `{config[key]}`"
            rendered_keys.add(key)

    missing = set(ADO_SYNC_CONFIG_LABELS) - rendered_keys
    if missing:
        raise ValueError(f"Packaged golazo-ado-sync skill is missing configuration field: {sorted(missing)[0]}")
    suffix = "\n" if skill_markdown.endswith("\n") else ""
    return "\n".join(lines) + suffix


def _copy_resource_tree(source: Any, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            _copy_resource_tree(item, target)
        else:
            target.write_bytes(item.read_bytes())


def _validate_staged_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) != 3:
        raise ValueError("Installed golazo-ado-sync skill has invalid YAML frontmatter")
    frontmatter = yaml.safe_load(parts[1])
    if not isinstance(frontmatter, dict) or frontmatter.get("name") != ADO_SYNC_SKILL_NAME:
        raise ValueError("Installed golazo-ado-sync skill name must match its folder")


def install_ado_sync_skill(
    destination: Path,
    config: dict[str, str],
    force: bool,
) -> str:
    """Install a validated skill tree and return its outcome status."""
    if destination.exists() and not force:
        return "skipped"

    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{ADO_SYNC_SKILL_NAME}-", dir=destination.parent))
    backup: Path | None = None
    try:
        source = resources.files("golazo_copilot").joinpath("skills").joinpath(ADO_SYNC_SKILL_NAME)
        _copy_resource_tree(source, stage)
        skill_file = stage / "SKILL.md"
        skill_file.write_text(
            _render_skill_config(skill_file.read_text(encoding="utf-8"), config),
            encoding="utf-8",
        )
        (stage / "defaults.yaml").write_text(
            yaml.safe_dump(config, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )
        _validate_staged_skill(stage)

        status = "created"
        if destination.exists():
            status = "replaced"
            backup = destination.with_name(f".{destination.name}-backup-{uuid4().hex}")
            destination.replace(backup)
        try:
            stage.replace(destination)
        except Exception:
            if backup is not None and backup.exists():
                backup.replace(destination)
            raise
        if backup is not None:
            shutil.rmtree(backup)
        return status
    finally:
        if stage.exists():
            shutil.rmtree(stage)