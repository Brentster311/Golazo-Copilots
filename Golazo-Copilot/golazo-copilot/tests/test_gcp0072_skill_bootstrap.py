"""GCP-0072 tests for scope-aware Golazo ADO Sync skill installation."""

import importlib
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.dispatch.registry import get_tool_definitions
from golazo_copilot.formatters.results import format_bootstrap_result
from golazo_copilot.handlers.tools import handle_registered_tool
from golazo_copilot.tools.ado_sync_skill import (
    ADO_SYNC_CONFIG_LABELS,
    get_ado_sync_default_config,
)
from golazo_copilot.tools.golazo_bootstrap import golazo_bootstrap

DEFAULT_CONFIG = {
    "organization": "https://dev.azure.com/msazure",
    "project": "One",
    "team": "EngOps Supportability DS",
    "board": "Backlog items",
    "work_item_type": "Product Backlog Item",
    "area": r"One\Azure CXP\Product and Platform\Data\Data Science\SupportabilityDS",
    "iteration": r"One\FY27",
    "assignee": "brentj@microsoft.com",
    "planned_swimlane_field": "WEF_3685ECC254584507922BD78681CF0942_Kanban.Lane",
    "board_column_field": "WEF_3685ECC254584507922BD78681CF0942_Kanban.Column",
    "board_done_field": "WEF_3685ECC254584507922BD78681CF0942_Kanban.Column.Done",
}


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "WorkItems").mkdir()
    return tmp_path


def _skill_path(root: Path) -> Path:
    return root / ".github" / "skills" / "golazo-ado-sync"


def _frontmatter(skill_markdown: str) -> dict:
    _, raw, _ = skill_markdown.split("---", 2)
    return yaml.safe_load(raw)


def test_bootstrap_schema_exposes_skill_defaults_and_confirmation():
    tool = next(tool for tool in get_tool_definitions() if tool.name == "golazo_bootstrap")
    properties = tool.inputSchema["properties"]

    assert properties["install_ado_sync_skill"]["default"] is False
    assert properties["ado_sync_config_confirmed"]["default"] is False
    config_schema = properties["ado_sync_config"]
    assert set(config_schema["properties"]) == set(DEFAULT_CONFIG)
    assert {
        name: definition["default"]
        for name, definition in config_schema["properties"].items()
    } == DEFAULT_CONFIG


@pytest.mark.asyncio
async def test_install_requires_explicit_configuration_confirmation(workspace: Path):
    result = await golazo_bootstrap(
        workspace_path=workspace,
        install_ado_sync_skill=True,
    )

    assert result["success"] is False
    assert "confirm" in result["error"].lower()
    assert not _skill_path(workspace).exists()


@pytest.mark.asyncio
async def test_workspace_install_copies_discoverable_skill_with_defaults(workspace: Path):
    result = await golazo_bootstrap(
        workspace_path=workspace,
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
    )

    destination = _skill_path(workspace)
    content = (destination / "SKILL.md").read_text(encoding="utf-8")
    assert result["success"] is True
    assert result["skills"] == [
        {
            "name": "golazo-ado-sync",
            "scope": "Workspace",
            "target_path": str(destination),
            "status": "created",
            "configuration_source": "defaults",
        }
    ]
    assert _frontmatter(content)["name"] == "golazo-ado-sync"
    assert "- Project: `One`" in content
    assert f"- Area: `{DEFAULT_CONFIG['area']}`" in content


@pytest.mark.asyncio
async def test_custom_configuration_is_rendered_without_mutating_package_source(workspace: Path):
    package_skill = (
        Path(__file__).parent.parent
        / "src"
        / "golazo_copilot"
        / "skills"
        / "golazo-ado-sync"
        / "SKILL.md"
    )
    original = package_skill.read_text(encoding="utf-8")

    result = await golazo_bootstrap(
        workspace_path=workspace,
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
        ado_sync_config={"project": "Custom Project", "area": r"Custom\Area"},
    )

    installed = (_skill_path(workspace) / "SKILL.md").read_text(encoding="utf-8")
    assert result["success"] is True
    assert result["skills"][0]["configuration_source"] == "customized"
    assert "- Project: `Custom Project`" in installed
    assert r"- Area: `Custom\Area`" in installed
    assert package_skill.read_text(encoding="utf-8") == original


@pytest.mark.asyncio
async def test_user_scope_installs_under_active_home(workspace: Path, tmp_path: Path, monkeypatch):
    user_home = tmp_path / "home"
    monkeypatch.setattr("golazo_copilot.dispatch.paths.Path.home", lambda: user_home)

    result = await golazo_bootstrap(
        workspace_path=workspace,
        scope="User",
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
    )

    destination = user_home / ".copilot" / "skills" / "golazo-ado-sync"
    assert result["success"] is True
    assert (destination / "SKILL.md").exists()
    assert result["skills"][0]["target_path"] == str(destination)
    assert not _skill_path(workspace).exists()


@pytest.mark.asyncio
async def test_existing_skill_is_skipped_without_force(workspace: Path):
    arguments = {
        "workspace_path": workspace,
        "install_ado_sync_skill": True,
        "ado_sync_config_confirmed": True,
    }
    await golazo_bootstrap(**arguments)
    skill_file = _skill_path(workspace) / "SKILL.md"
    skill_file.write_text("sentinel", encoding="utf-8")

    result = await golazo_bootstrap(**arguments)

    assert result["success"] is True
    assert result["skills"][0]["status"] == "skipped"
    assert skill_file.read_text(encoding="utf-8") == "sentinel"


@pytest.mark.asyncio
async def test_force_replaces_existing_skill(workspace: Path):
    destination = _skill_path(workspace)
    destination.mkdir(parents=True)
    (destination / "SKILL.md").write_text("sentinel", encoding="utf-8")

    result = await golazo_bootstrap(
        workspace_path=workspace,
        force=True,
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
    )

    assert result["success"] is True
    assert result["skills"][0]["status"] == "replaced"
    assert _frontmatter((destination / "SKILL.md").read_text(encoding="utf-8"))["name"] == "golazo-ado-sync"


@pytest.mark.asyncio
async def test_empty_configuration_value_fails_without_partial_install(workspace: Path):
    result = await golazo_bootstrap(
        workspace_path=workspace,
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
        ado_sync_config={"organization": ""},
    )

    assert result["success"] is False
    assert "organization" in result["error"]
    assert not _skill_path(workspace).exists()


@pytest.mark.asyncio
async def test_orchestrator_only_rejects_skill_install_before_writing(workspace: Path):
    result = await golazo_bootstrap(
        workspace_path=workspace,
        mode="orchestrator-only",
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
    )

    assert result["success"] is False
    assert "orchestrator-only" in result["error"]
    assert not (workspace / ".github").exists()


def test_packaged_markdown_and_structured_defaults_remain_in_parity():
    package_skill = (
        Path(__file__).parent.parent
        / "src"
        / "golazo_copilot"
        / "skills"
        / "golazo-ado-sync"
        / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert get_ado_sync_default_config() == DEFAULT_CONFIG
    for name, label in ADO_SYNC_CONFIG_LABELS.items():
        assert f"- {label}: `{DEFAULT_CONFIG[name]}`" in package_skill


@pytest.mark.asyncio
async def test_install_copies_complete_packaged_resource_tree(workspace: Path):
    await golazo_bootstrap(
        workspace_path=workspace,
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
    )

    installed_defaults = yaml.safe_load(
        (_skill_path(workspace) / "defaults.yaml").read_text(encoding="utf-8")
    )
    assert installed_defaults == DEFAULT_CONFIG


@pytest.mark.asyncio
async def test_failed_forced_install_preserves_existing_skill(workspace: Path, monkeypatch):
    destination = _skill_path(workspace)
    destination.mkdir(parents=True)
    skill_file = destination / "SKILL.md"
    skill_file.write_text("sentinel", encoding="utf-8")

    def fail_validation(_skill_dir: Path) -> None:
        raise ValueError("simulated validation failure")

    installer_module = importlib.import_module("golazo_copilot.tools.ado_sync_skill")
    monkeypatch.setattr(installer_module, "_validate_staged_skill", fail_validation)
    result = await golazo_bootstrap(
        workspace_path=workspace,
        force=True,
        install_ado_sync_skill=True,
        ado_sync_config_confirmed=True,
    )

    assert result["success"] is False
    assert "simulated validation failure" in result["error"]
    assert skill_file.read_text(encoding="utf-8") == "sentinel"


@pytest.mark.asyncio
async def test_modular_dispatch_forwards_skill_arguments(monkeypatch, workspace: Path):
    captured = {}

    async def fake_bootstrap(**kwargs):
        captured.update(kwargs)
        return {
            "success": True,
            "scope": "Workspace",
            "target_path": "instructions",
            "files_created": [],
            "files_skipped": [],
            "skills": [],
            "message": "done",
        }

    monkeypatch.setattr("golazo_copilot.handlers.tools.golazo_bootstrap", fake_bootstrap)
    await handle_registered_tool(
        "golazo_bootstrap",
        {
            "workspace_path": str(workspace),
            "install_ado_sync_skill": True,
            "ado_sync_config_confirmed": True,
            "ado_sync_config": {"project": "Custom"},
        },
        [],
    )

    assert captured["install_ado_sync_skill"] is True
    assert captured["ado_sync_config_confirmed"] is True
    assert captured["ado_sync_config"] == {"project": "Custom"}


@pytest.mark.asyncio
async def test_legacy_server_schema_exposes_skill_contract():
    from golazo_copilot import server as server_module

    tool = next(tool for tool in await server_module.list_tools() if tool.name == "golazo_bootstrap")
    properties = tool.inputSchema["properties"]

    assert properties["install_ado_sync_skill"]["default"] is False
    assert properties["ado_sync_config_confirmed"]["default"] is False
    assert set(properties["ado_sync_config"]["properties"]) == set(DEFAULT_CONFIG)


def test_formatter_reports_skill_outcome_without_dumping_configuration():
    result = {
        "success": True,
        "scope": "Workspace",
        "target_path": "instructions",
        "files_created": [],
        "files_skipped": [],
        "skills": [
            {
                "name": "golazo-ado-sync",
                "scope": "Workspace",
                "target_path": ".github/skills/golazo-ado-sync",
                "status": "created",
                "configuration_source": "customized",
            }
        ],
        "message": "done",
    }

    text = format_bootstrap_result(result)

    assert "golazo-ado-sync: created" in text
    assert ".github/skills/golazo-ado-sync" in text
    assert "customized" in text
    assert "organization" not in text