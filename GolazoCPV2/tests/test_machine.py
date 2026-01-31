import pytest
from pathlib import Path
from golazo.state import create_state, load_state, save_state
from golazo.machine import GolazoStateMachine, VALID_ROLES


class TestConstructor:
    def test_new_work_item(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("NEW-001", base_path=tmp_path)
        assert m.current_role == "project-owner"

    def test_existing_state(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        state = create_state("EXIST-001", base_path=tmp_path)
        state.currentRole = "developer"
        save_state(state, base_path=tmp_path)
        m = GolazoStateMachine("EXIST-001", base_path=tmp_path)
        assert m.current_role == "developer"


class TestProperties:
    def test_current_role(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T1", base_path=tmp_path)
        assert m.current_role == "project-owner"

    def test_current_phase(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T2", base_path=tmp_path)
        assert m.current_phase == "design"

    def test_profile(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T3", profile="express", base_path=tmp_path)
        assert m.profile == "express"


class TestCanTransition:
    def test_valid_next(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T4", base_path=tmp_path)
        allowed, reason = m.can_transition("program-manager")
        assert allowed is True

    def test_skip_role(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T5", base_path=tmp_path)
        allowed, reason = m.can_transition("developer")
        assert allowed is False

    def test_invalid_role(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T6", base_path=tmp_path)
        allowed, reason = m.can_transition("invalid-role")
        assert allowed is False
        assert "unknown" in reason.lower()

    def test_dor_gate_blocks(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T7", base_path=tmp_path)
        m.transition("program-manager")
        m.transition("tester")
        m.transition("architect")
        allowed, reason = m.can_transition("developer")
        assert allowed is False
        assert "dor" in reason.lower()

    def test_dor_gate_allows(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T8", base_path=tmp_path)
        m.transition("program-manager")
        m.transition("tester")
        m.transition("architect")
        m.mark_dor("userStory", True)
        m.mark_dor("designDoc", True)
        m.mark_dor("reviewComments", True)
        m.mark_dor("testCases", True)
        allowed, reason = m.can_transition("developer")
        assert allowed is True


class TestTransition:
    def test_valid_transition(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T9", base_path=tmp_path)
        success, msg = m.transition("program-manager")
        assert success is True
        assert m.current_role == "program-manager"

    def test_invalid_transition(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T10", base_path=tmp_path)
        success, msg = m.transition("developer")
        assert success is False
        assert m.current_role == "project-owner"

    def test_updates_history(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T11", base_path=tmp_path)
        m.transition("program-manager")
        state = load_state("T11", base_path=tmp_path)
        assert len(state.roleHistory) == 2
        assert state.roleHistory[0]["exitedAt"] is not None

    def test_persists(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m1 = GolazoStateMachine("T12", base_path=tmp_path)
        m1.transition("program-manager")
        m2 = GolazoStateMachine("T12", base_path=tmp_path)
        assert m2.current_role == "program-manager"


class TestDorDod:
    def test_check_dor(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T13", base_path=tmp_path)
        dor = m.check_dor()
        assert dor["userStory"] is False

    def test_check_dod(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T14", base_path=tmp_path)
        dod = m.check_dod()
        assert dod["testsPass"] is False

    def test_mark_dor(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T15", base_path=tmp_path)
        m.mark_dor("userStory", True)
        assert m.check_dor()["userStory"] is True

    def test_mark_dod(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T16", base_path=tmp_path)
        m.mark_dod("testsPass", True)
        assert m.check_dod()["testsPass"] is True

    def test_mark_dor_persists(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m1 = GolazoStateMachine("T17", base_path=tmp_path)
        m1.mark_dor("userStory", True)
        m2 = GolazoStateMachine("T17", base_path=tmp_path)
        assert m2.check_dor()["userStory"] is True

    def test_mark_dor_invalid_item(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T18", base_path=tmp_path)
        with pytest.raises(ValueError):
            m.mark_dor("invalidItem", True)


class TestHelpers:
    def test_is_dor_complete(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T19", base_path=tmp_path)
        assert m.is_dor_complete() is False
        for item in ["userStory", "designDoc", "reviewComments", "testCases"]:
            m.mark_dor(item, True)
        assert m.is_dor_complete() is True
