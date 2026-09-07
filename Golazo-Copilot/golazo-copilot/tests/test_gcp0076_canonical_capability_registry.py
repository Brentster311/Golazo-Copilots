"""GCP-0076 policy tests for one canonical capability registry."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.golazo_bootstrap import golazo_bootstrap
from golazo_copilot.tools.golazo_capabilities import golazo_capabilities
from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_status import _get_registry_hint

REPOSITORY_ROOT = Path(__file__).parents[2]
CANONICAL_RELATIVE_PATH = Path("WorkItems") / "capabilities.yaml"
EXPECTED_CAPABILITIES = {
    "workflow-orchestration",
    "capability-registry-management",
    "bootstrap-skill-installation",
    "project-finalization",
    "release-policy-guidance",
}


@pytest.mark.asyncio
async def test_bootstrap_creates_only_canonical_registry(tmp_path: Path):
    (tmp_path / "WorkItems").mkdir()
    result = await golazo_bootstrap(workspace_path=tmp_path)

    assert result["success"] is True
    assert (tmp_path / CANONICAL_RELATIVE_PATH).exists()
    assert not (tmp_path / "capabilities.yaml").exists()
    assert CANONICAL_RELATIVE_PATH.as_posix() in result["files_created"]


@pytest.mark.asyncio
async def test_create_workitem_creates_only_canonical_registry(tmp_path: Path):
    result = await golazo_create_workitem(
        work_item_id="CAP-076",
        work_items_dir=tmp_path / "WorkItems",
    )

    assert result["success"] is True
    assert (tmp_path / CANONICAL_RELATIVE_PATH).exists()
    assert not (tmp_path / "capabilities.yaml").exists()


@pytest.mark.asyncio
async def test_bootstrap_migrates_legacy_registry_without_data_loss(tmp_path: Path):
    (tmp_path / "WorkItems").mkdir()
    legacy = tmp_path / "capabilities.yaml"
    content = "capabilities:\n  - name: preserved\n"
    legacy.write_text(content, encoding="utf-8")

    result = await golazo_bootstrap(workspace_path=tmp_path)

    assert result["success"] is True
    assert (tmp_path / CANONICAL_RELATIVE_PATH).read_text(encoding="utf-8") == content
    assert not legacy.exists()


def test_status_prefers_canonical_and_is_read_only(tmp_path: Path):
    canonical = tmp_path / CANONICAL_RELATIVE_PATH
    canonical.parent.mkdir()
    canonical.write_text("capabilities:\n  - name: canonical\n", encoding="utf-8")
    legacy = tmp_path / "capabilities.yaml"
    legacy.write_text("capabilities:\n  - name: one\n  - name: two\n", encoding="utf-8")

    hint = _get_registry_hint(tmp_path)

    assert hint is not None and "1 capability(ies)" in hint
    assert legacy.exists()
    assert canonical.exists()


def test_status_reads_legacy_without_moving_it(tmp_path: Path):
    legacy = tmp_path / "capabilities.yaml"
    legacy.write_text("capabilities:\n  - name: legacy\n", encoding="utf-8")

    hint = _get_registry_hint(tmp_path)

    assert hint is not None and "1 capability(ies)" in hint
    assert legacy.exists()
    assert not (tmp_path / CANONICAL_RELATIVE_PATH).exists()


@pytest.mark.asyncio
async def test_real_registry_is_populated_valid_and_impactful():
    registry_path = REPOSITORY_ROOT / CANONICAL_RELATIVE_PATH
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    capabilities = data["capabilities"]

    assert {capability["name"] for capability in capabilities} == EXPECTED_CAPABILITIES
    assert all(capability.get("description") for capability in capabilities)
    assert all(capability.get("key_files") for capability in capabilities)
    assert all(capability.get("contracts") for capability in capabilities)
    assert all("depends_on" in capability for capability in capabilities)

    validation = await golazo_capabilities(action="validate", workspace_path=REPOSITORY_ROOT)
    assert validation["success"] is True
    assert all(result["valid"] for result in validation["results"])

    impact = await golazo_capabilities(
        action="impact",
        files=[
            "golazo-copilot/src/golazo_copilot/tools/golazo_status.py",
            "golazo-copilot/src/golazo_copilot/roles/defaults/builder.md",
        ],
        workspace_path=REPOSITORY_ROOT,
    )
    affected = {
        item["name"]
        for key in ("directly_affected", "transitively_affected")
        for item in impact[key]
    }
    assert "capability-registry-management" in affected
    assert "release-policy-guidance" in affected


def test_repository_has_one_top_level_registry_and_preserves_test_registry():
    assert (REPOSITORY_ROOT / CANONICAL_RELATIVE_PATH).exists()
    assert not (REPOSITORY_ROOT / "capabilities.yaml").exists()
    assert not (REPOSITORY_ROOT / "golazo-copilot" / "capabilities.yaml").exists()
    assert (REPOSITORY_ROOT / "golazo-copilot" / "tests" / CANONICAL_RELATIVE_PATH).exists()
