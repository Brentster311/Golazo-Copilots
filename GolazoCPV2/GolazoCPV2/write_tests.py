"""Write test file."""
TEST_CODE = """import pytest
from golazo.state import create_state, load_state, save_state, state_exists

def test_create(tmp_path):
    (tmp_path / "WorkItems").mkdir()
    state = create_state("T1", base_path=tmp_path)
    assert state.workItemId == "T1"

def test_load_missing(tmp_path):
    (tmp_path / "WorkItems").mkdir()
    assert load_state("X", base_path=tmp_path) is None

def test_persistence(tmp_path):
    (tmp_path / "WorkItems").mkdir()
    state = create_state("T2", base_path=tmp_path)
    state.currentRole = "developer"
    save_state(state, base_path=tmp_path)
    reloaded = load_state("T2", base_path=tmp_path)
    assert reloaded.currentRole == "developer"

def test_invalid_id(tmp_path):
    (tmp_path / "WorkItems").mkdir()
    with pytest.raises(ValueError):
        create_state("../bad", base_path=tmp_path)

def test_state_exists(tmp_path):
    (tmp_path / "WorkItems").mkdir()
    create_state("E1", base_path=tmp_path)
    assert state_exists("E1", base_path=tmp_path) is True
    assert state_exists("E2", base_path=tmp_path) is False

def test_schema_defaults(tmp_path):
    (tmp_path / "WorkItems").mkdir()
    state = create_state("T3", base_path=tmp_path)
    assert state.currentRole == "project-owner"
    assert state.currentPhase == "design"
"""

with open("tests/test_state.py", "w", encoding="utf-8") as f:
    f.write(TEST_CODE)
print("Done")
