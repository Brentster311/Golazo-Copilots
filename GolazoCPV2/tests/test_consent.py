import pytest
from pathlib import Path
from golazo.machine import GolazoStateMachine
from golazo.consent import ConsentEnforcer, RequestAnalysis, QUALITY_GATE_ROLES


class TestPatternDetection:
    def test_explicit_skip_role(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T1", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("skip the tester role")
        assert result.type == "explicit_skip"
        assert "tester" in result.detected_skips

    def test_explicit_skip_to(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T2", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("skip to developer")
        assert result.type == "explicit_skip"
        assert "developer" in result.detected_skips

    def test_explicit_fast_track_hyphen(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T3", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("fast-track this")
        assert result.type == "explicit_skip"

    def test_explicit_fast_track_space(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T4", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("fast track this")
        assert result.type == "explicit_skip"

    def test_ambiguous_just_fix(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T5", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("just fix this bug")
        assert result.type == "ambiguous"

    def test_ambiguous_quick_fix(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T6", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("quick fix please")
        assert result.type == "ambiguous"

    def test_normal_technical_request(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T7", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("Add null check to GetUser method")
        assert result.type == "normal"

    def test_case_insensitive(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T8", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("SKIP THE TESTER ROLE")
        assert result.type == "explicit_skip"
        assert "tester" in result.detected_skips


class TestClarificationPrompts:
    def test_ambiguous_generates_prompt(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T9", base_path=tmp_path)
        e = ConsentEnforcer(m)
        analysis = RequestAnalysis(type="ambiguous", detected_skips=[], matched_pattern="just fix")
        prompt = e.get_clarification_prompt(analysis)
        assert prompt is not None
        assert len(prompt) > 0

    def test_normal_no_prompt(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T10", base_path=tmp_path)
        e = ConsentEnforcer(m)
        analysis = RequestAnalysis(type="normal", detected_skips=[], matched_pattern=None)
        prompt = e.get_clarification_prompt(analysis)
        assert prompt is None or prompt == ""

    def test_explicit_no_prompt(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T11", base_path=tmp_path)
        e = ConsentEnforcer(m)
        analysis = RequestAnalysis(type="explicit_skip", detected_skips=["tester"], matched_pattern="skip")
        prompt = e.get_clarification_prompt(analysis)
        assert prompt is None or prompt == ""

    def test_quality_gate_warning(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T12", base_path=tmp_path)
        e = ConsentEnforcer(m)
        warning = e.get_quality_gate_warning("tester")
        assert warning is not None
        assert "quality gate" in warning.lower() or "tester" in warning.lower()


class TestDeviationRecording:
    def test_record_saves_to_state(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T13", base_path=tmp_path)
        e = ConsentEnforcer(m)
        e.record_deviation("skip_role", "just fix it", ["tester"])
        deviations = e.get_deviations()
        assert len(deviations) >= 1

    def test_deviation_has_timestamp(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T14", base_path=tmp_path)
        e = ConsentEnforcer(m)
        e.record_deviation("skip_role", "just fix it", ["tester"])
        deviations = e.get_deviations()
        assert "timestamp" in deviations[-1]

    def test_deviation_has_reason(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T15", base_path=tmp_path)
        e = ConsentEnforcer(m)
        e.record_deviation("skip_role", "just fix it", ["tester"])
        deviations = e.get_deviations()
        assert deviations[-1]["reason"] == "just fix it"

    def test_deviation_has_consent_type(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T16", base_path=tmp_path)
        e = ConsentEnforcer(m)
        e.record_deviation("skip_role", "skip tester", ["tester"], consent_type="explicit")
        deviations = e.get_deviations()
        assert deviations[-1].get("consent_type") == "explicit"

    def test_get_deviations_returns_all(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T17", base_path=tmp_path)
        e = ConsentEnforcer(m)
        e.record_deviation("skip_role", "reason1", ["tester"])
        e.record_deviation("skip_role", "reason2", ["architect"])
        e.record_deviation("skip_dor", "reason3", [])
        deviations = e.get_deviations()
        assert len(deviations) == 3


class TestQualityGates:
    def test_tester_is_quality_gate(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T18", base_path=tmp_path)
        e = ConsentEnforcer(m)
        assert e.is_quality_gate("tester") is True

    def test_architect_is_quality_gate(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T19", base_path=tmp_path)
        e = ConsentEnforcer(m)
        assert e.is_quality_gate("architect") is True

    def test_developer_not_quality_gate(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T20", base_path=tmp_path)
        e = ConsentEnforcer(m)
        assert e.is_quality_gate("developer") is False


class TestForceTransition:
    def test_force_skips_dor_check(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T21", base_path=tmp_path)
        # Get to architect without completing DoR
        m.transition("program-manager")
        m.transition("tester")
        m.transition("architect")
        # Normal transition should fail
        allowed, _ = m.can_transition("developer")
        assert allowed is False
        # Force should succeed
        success, _ = m.transition("developer", force=True)
        assert success is True
        assert m.current_role == "developer"


class TestEdgeCases:
    def test_empty_message(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T22", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("")
        assert result.type == "normal"

    def test_explicit_takes_precedence(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T23", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("just fix this, skip to developer")
        assert result.type == "explicit_skip"

    def test_unknown_role_in_skip(self, tmp_path):
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T24", base_path=tmp_path)
        e = ConsentEnforcer(m)
        result = e.analyze_request("skip the foo role")
        assert result.type == "explicit_skip"
        assert "foo" in result.detected_skips
