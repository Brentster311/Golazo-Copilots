"""Coverage tests for legacy pre-override code in server.py."""

from pathlib import Path

import pytest

import golazo_copilot.server as server_mod


def _load_legacy_server_namespace() -> dict:
    server_path = Path(server_mod.__file__)
    source = server_path.read_text(encoding="utf-8")
    marker = "Modular override bindings (GCP-0061)"
    prefix = source.split(marker, maxsplit=1)[0]

    namespace: dict = {
        "__name__": "golazo_copilot.server_legacy_for_tests",
        "__package__": "golazo_copilot",
        "__file__": str(server_path),
    }
    exec(compile(prefix, str(server_path), "exec"), namespace)
    return namespace


def test_legacy_formatter_branches():
    ns = _load_legacy_server_namespace()
    assert ns["resolve_work_items_dir"]("x")
    assert ns["has_orchestrator_instructions"](None) is False

    create_ok = ns["format_create_workitem_result"](
        {
            "success": True,
            "work_item_id": "GCP-1",
            "current_role": "project-owner-assistant",
            "role_instructions": "ri",
        }
    )
    assert "created" in create_ok.lower()
    assert "GCP-1" in create_ok
    assert "failed" in ns["format_create_workitem_result"]({"success": False, "error": "bad"}).lower()

    transition_ok = ns["format_transition_result"](
        {
            "success": True,
            "current_role": "program-manager",
            "current_phase": "definition",
            "role_instructions": "ri",
            "warning": "warn",
            "closure_pending": True,
        }
    )
    assert "Transitioned" in transition_ok
    assert "CLOSURE MODE" in transition_ok
    assert "failed" in ns["format_transition_result"]({"success": False, "error": "bad"}).lower()

    active_status = ns["format_status_result"](
        {
            "active": True,
            "version": "1.0",
            "work_item_id": "GCP-1",
            "current_role": "developer",
            "current_phase": "dev",
            "version_warning": "vw",
            "role_progress": {"roles_completed": 1, "roles_total": 9},
            "required_outputs": {
                "complete": False,
                "outputs": [{"path": "a.md", "valid": True}, {"path": "b.md", "valid": False}],
            },
            "registry_hint": "hint",
            "tooling_warnings": ["tw"],
            "deviations": [{"id": "d1", "action": "custom", "reason": "r", "consumed": True}],
            "next_steps": ["s1", "s2"],
            "role_instructions": "ri",
            "closure_pending": True,
        }
    )
    assert "Golazo Status" in active_status
    assert "Tooling self-check warnings" in active_status
    assert "Deviations" in active_status

    inactive_status = ns["format_status_result"](
        {"active": False, "version": "1.0", "message": "none", "tooling_warnings": ["tw2"]}
    )
    assert "none" in inactive_status
    assert "Tooling self-check" in inactive_status

    bootstrap_ok = ns["format_bootstrap_result"](
        {"success": True, "files_created": ["a"], "files_skipped": ["b"], "message": "ok"}
    )
    assert "bootstrapped" in bootstrap_ok.lower()
    bootstrap_fail = ns["format_bootstrap_result"](
        {"success": False, "error": "No workspace markers found in x"}
    )
    assert "Next step" in bootstrap_fail

    consent_ok = ns["format_consent_result"](
        {"success": True, "deviation_id": "dev-1", "action": "custom", "message": "ok"}
    )
    assert "Consent recorded" in consent_ok
    assert "failed" in ns["format_consent_result"]({"success": False, "error": "bad"}).lower()

    caps_list = ns["format_capabilities_result"](
        {"success": True, "capabilities": [{"name": "a", "description": "d"}]}, "list"
    )
    assert "Capability Registry" in caps_list
    caps_show = ns["format_capabilities_result"](
        {
            "success": True,
            "capability": {
                "name": "a",
                "description": "d",
                "key_files": ["f.py"],
                "contracts": ["c"],
                "depends_on": ["x"],
                "depended_on_by": ["y"],
            },
        },
        "show",
    )
    assert "Capability: a" in caps_show
    caps_impact = ns["format_capabilities_result"](
        {
            "success": True,
            "directly_affected": [{"name": "a", "description": "A"}],
            "transitively_affected": [{"name": "b", "description": "B"}],
        },
        "impact",
        ["f.py"],
    )
    assert "Impact Analysis" in caps_impact
    caps_validate = ns["format_capabilities_result"](
        {"success": True, "results": [{"name": "a", "valid": False, "missing_files": ["x"]}]}, "validate"
    )
    assert "missing" in caps_validate

    role_ctx_ok = ns["format_role_context_result"](
        {"status": "ok", "role": "dev", "artifact_count": 1, "total_size": 10, "bundle": "ctx"}
    )
    assert "Role context bundled" in role_ctx_ok
    assert "bad" in ns["format_role_context_result"]({"status": "error", "error": "bad"})

    git_ok = ns["format_git_propose_result"](
        {
            "success": True,
            "work_item_id": "GCP-1",
            "proposal_count": 1,
            "proposal": {
                "action": "add",
                "status": "proposed",
                "timestamp": "now",
                "files": ["a"],
                "message": "m",
                "branch": "b",
            },
        }
    )
    assert "Git proposal recorded" in git_ok
    assert "failed" in ns["format_git_propose_result"]({"success": False, "error": "bad"}).lower()

def test_legacy_has_orchestrator_instructions_accepts_user_scope(tmp_path, monkeypatch):
    ns = _load_legacy_server_namespace()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    user_home = tmp_path / "user-home"
    monkeypatch.setattr("pathlib.Path.home", lambda: user_home)
    agents = user_home / ".copilot" / "agents"
    agents.mkdir(parents=True)
    (agents / "Golazo-Copilot.md").write_text("# Instructions", encoding="utf-8")

    assert ns["has_orchestrator_instructions"](str(workspace)) is True


@pytest.mark.asyncio
async def test_legacy_dispatch_tool_branches(monkeypatch, tmp_path):
    ns = _load_legacy_server_namespace()
    dispatch = ns["_dispatch_tool"]

    workspace = tmp_path
    (workspace / "WorkItems").mkdir()
    agents = workspace / ".github" / "agents"
    agents.mkdir(parents=True)
    (agents / "Golazo-Copilot.md").write_text("# ok", encoding="utf-8")

    async def fake_create_workitem(**_kwargs):
        return {
            "success": True,
            "work_item_id": "GCP-1",
            "current_role": "project-owner-assistant",
            "role_instructions": "do work",
        }

    async def fake_transition(**_kwargs):
        return {
            "success": True,
            "current_role": "program-manager",
            "current_phase": "definition",
            "role_instructions": "pm",
        }

    async def fake_status(**_kwargs):
        return {
            "active": False,
            "version": "1.0",
            "message": "none",
        }

    async def fake_bootstrap(**_kwargs):
        return {
            "success": True,
            "files_created": [],
            "files_skipped": [],
            "message": "ok",
        }

    async def fake_consent(**_kwargs):
        return {
            "success": True,
            "deviation_id": "dev-1",
            "action": "custom",
            "message": "recorded",
        }

    async def fake_capabilities(**_kwargs):
        return {"success": True, "message": "caps"}

    async def fake_role_context(**_kwargs):
        return {"status": "ok", "bundle": "ctx", "artifact_count": 0, "total_size": 0}

    async def fake_git_propose(**_kwargs):
        return {
            "success": True,
            "work_item_id": "GCP-1",
            "proposal_count": 1,
            "proposal": {"action": "add", "status": "proposed", "timestamp": "now"},
        }

    monkeypatch.setitem(ns, "golazo_create_workitem", fake_create_workitem)
    monkeypatch.setitem(ns, "golazo_transition", fake_transition)
    monkeypatch.setitem(ns, "golazo_status", fake_status)
    monkeypatch.setitem(ns, "golazo_bootstrap", fake_bootstrap)
    monkeypatch.setitem(ns, "golazo_consent", fake_consent)
    monkeypatch.setitem(ns, "golazo_capabilities", fake_capabilities)
    monkeypatch.setitem(ns, "golazo_role_context", fake_role_context)
    monkeypatch.setitem(ns, "golazo_git_propose", fake_git_propose)

    common = {"workspace_path": str(workspace), "work_item_id": "GCP-1"}

    assert "created" in (await dispatch("golazo_create_workitem", common))[0].text.lower()
    assert "Transitioned" in (await dispatch("golazo_transition", {**common, "role": "program-manager"}))[0].text
    assert "Golazo Copilot" in (await dispatch("golazo_status", {"workspace_path": str(workspace)}))[0].text
    assert "none" in (await dispatch("golazo_status", common))[0].text
    assert "bootstrapped" in (await dispatch("golazo_bootstrap", {"workspace_path": str(workspace)}))[0].text.lower()
    assert "Consent recorded" in (await dispatch("golazo_consent", {**common, "action": "custom", "reason": "long enough"}))[0].text
    assert "caps" in (await dispatch("golazo_capabilities", {"workspace_path": str(workspace), "action": "list"}))[0].text
    assert "ctx" in (await dispatch("golazo_role_context", common))[0].text
    assert "Git proposal recorded" in (
        await dispatch("golazo_git_propose", {**common, "action": "add", "files": ["a.txt"]})
    )[0].text
    assert "Unknown tool" in (await dispatch("unknown", {}))[0].text


@pytest.mark.asyncio
async def test_legacy_runtime_tool_self_check_warnings(monkeypatch):
    ns = _load_legacy_server_namespace()
    runtime_tool_self_check = ns["_runtime_tool_self_check"]

    class _FakeTool:
        def __init__(self, name: str):
            self.name = name

    async def fake_dispatch(name, _arguments):
        return [type("_T", (), {"text": f"Unknown tool: {name}"})()]

    monkeypatch.setitem(ns, "_REQUIRED_TOOL_NAMES", {"required_only"})
    monkeypatch.setitem(ns, "_get_tool_definitions", lambda: [_FakeTool("tool_a")])
    monkeypatch.setitem(ns, "_dispatch_tool", fake_dispatch)

    warnings = await runtime_tool_self_check()
    assert any("Missing required tool registration" in warning for warning in warnings)
    assert any("missing dispatch branch" in warning for warning in warnings)
