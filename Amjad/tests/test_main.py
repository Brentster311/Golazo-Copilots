"""Tests for main.py — CLI orchestration and helper functions."""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from ees.exceptions import ConfigError, IncidentLoadError, LLMError
from ees.main import (
    _confirm_facts,
    _confirm_root_cause,
    _confirm_rules,
    _edit_fact,
    _format_rule_conditions,
    _specialize_fact,
    main,
    process_incident,
)
from ees.models import (
    Fact,
    Incident,
    LLMResponse,
    OntologyNoun,
    OntologyProperty,
    RootCause,
    Rule,
    RuleConditions,
    RuleThen,
)


# ---------------------------------------------------------------------------
# _confirm_facts
# ---------------------------------------------------------------------------
class TestConfirmFacts:
    def test_confirm_action(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "c")
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].status == "confirmed"

    def test_reject_action(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "r")
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].status == "rejected"

    def test_edit_valid(self, monkeypatch):
        inputs = iter(["e", "Server(*).CPU > 90"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].noun == "Server"
        assert result[0].status == "confirmed"

    def test_edit_all_invalid_falls_to_rejected(self, monkeypatch):
        # 3 invalid edits → fact rejected
        inputs = iter(["e", "bad", "bad", "bad"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].status == "rejected"

    def test_specialize_confirm(self, monkeypatch):
        inputs = iter(["s", "WebApp01", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].instance == "WebApp01"
        assert result[0].status == "confirmed"

    def test_specialize_reject(self, monkeypatch):
        inputs = iter(["s", "WebApp01", "r"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].status == "rejected"

    def test_specialize_empty_retries(self, monkeypatch):
        # Empty instance → keeps original (returns None), loops back, then confirm
        inputs = iter(["s", "", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].instance == "*"

    def test_invalid_action_retries(self, monkeypatch):
        inputs = iter(["x", "z", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        facts = [Fact("S", "*", "P", ">", "1")]
        result = _confirm_facts(facts)
        assert len(result) == 1
        assert result[0].status == "confirmed"


# ---------------------------------------------------------------------------
# _edit_fact
# ---------------------------------------------------------------------------
class TestEditFact:
    def test_valid_edit(self, monkeypatch):
        inputs = iter(["Server(*).CPU > 90"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        f = Fact("S", "*", "P", ">", "1")
        result = _edit_fact(f)
        assert result is not None
        assert result.noun == "Server"

    def test_three_failures_returns_none(self, monkeypatch):
        inputs = iter(["bad", "bad", "bad"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        f = Fact("S", "*", "P", ">", "1")
        result = _edit_fact(f)
        assert result is None


# ---------------------------------------------------------------------------
# _confirm_rules
# ---------------------------------------------------------------------------
class TestConfirmRules:
    def _make_rule(self, rule_id="R-001"):
        return Rule(
            rule_id=rule_id,
            conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="reason",
        )

    def test_confirm_rule(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "c")
        result = _confirm_rules([self._make_rule()])
        assert len(result) == 1

    def test_reject_rule(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "r")
        result = _confirm_rules([self._make_rule()])
        assert len(result) == 0

    def test_edit_because_clause(self, monkeypatch):
        inputs = iter(["e", "updated reason"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = _confirm_rules([self._make_rule()])
        assert len(result) == 1
        assert result[0].because == "updated reason"

    def test_edit_empty_because_keeps_original(self, monkeypatch):
        inputs = iter(["e", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = _confirm_rules([self._make_rule()])
        assert len(result) == 1
        assert result[0].because == "reason"


# ---------------------------------------------------------------------------
# _confirm_root_cause
# ---------------------------------------------------------------------------
class TestConfirmRootCause:
    def test_none_proposed(self):
        assert _confirm_root_cause(None) is None

    def test_confirm(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "c")
        assert _confirm_root_cause("Disk Failure") == "Disk Failure"

    def test_edit(self, monkeypatch):
        inputs = iter(["e", "Network Issue"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        assert _confirm_root_cause("Disk Failure") == "Network Issue"

    def test_edit_empty(self, monkeypatch):
        inputs = iter(["e", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        assert _confirm_root_cause("Disk Failure") is None

    def test_reject(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "r")
        assert _confirm_root_cause("Disk Failure") is None


# ---------------------------------------------------------------------------
# _format_rule_conditions
# ---------------------------------------------------------------------------
class TestFormatRuleConditions:
    def test_single_condition(self):
        rule = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
        )
        assert _format_rule_conditions(rule) == "S(*).P > 1"

    def test_multiple_conditions_and(self):
        rule = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [
                Fact("S", "*", "A", ">", "1"),
                Fact("S", "*", "B", "<", "2"),
            ]),
            then=RuleThen("S", "*", "X", "TRUE"),
        )
        result = _format_rule_conditions(rule)
        assert " AND " in result
        assert "S(*).A > 1" in result
        assert "S(*).B < 2" in result


# ---------------------------------------------------------------------------
# process_incident — integration tests with mocked LLM and I/O
# ---------------------------------------------------------------------------
class TestProcessIncident:
    def _mock_llm_response(self):
        return LLMResponse(
            facts=[Fact("Server", "*", "CPUUsage", ">", "90")],
            rules=[
                Rule(
                    rule_id="",
                    conditions=RuleConditions("AND", [Fact("Server", "*", "CPUUsage", ">", "90")]),
                    then=RuleThen("Server", "*", "HighLoad", "TRUE"),
                    because="High CPU",
                )
            ],
            root_cause="Resource Exhaustion",
        )

    def test_full_happy_path(self, tmp_path, monkeypatch):
        """Full workflow: load → extract → confirm all → persist."""
        # Create incident file
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Server WebApp01 CPU at 95%")

        data_dir = tmp_path / "data"

        # Mock FactExtractor
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = self._mock_llm_response()

        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # User confirms everything: fact=c, root_cause=c, rule=c
        inputs = iter(["c", "c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        # Verify files were created
        assert (data_dir / "incidents").exists()
        assert len(list((data_dir / "incidents").glob("*.yaml"))) == 1
        assert len(list((data_dir / "rules").glob("*.yaml"))) == 1
        assert (data_dir / "ontology.yaml").exists()
        assert (data_dir / "rootcauses.yaml").exists()

    def test_no_facts_extracted(self, tmp_path, monkeypatch, capsys):
        """LLM returns no facts → early exit, no files created."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Nothing useful here")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = LLMResponse(facts=[], rules=[], root_cause=None)
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        process_incident(str(incident_file), str(data_dir))

        captured = capsys.readouterr()
        assert "No facts extracted" in captured.out
        assert len(list((data_dir / "incidents").glob("*.yaml"))) == 0

    def test_all_facts_rejected(self, tmp_path, monkeypatch, capsys):
        """All facts rejected → incident saved but no rules."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Some incident text")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = self._mock_llm_response()
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        monkeypatch.setattr("builtins.input", lambda _: "r")

        process_incident(str(incident_file), str(data_dir))

        captured = capsys.readouterr()
        assert "All facts rejected" in captured.out
        assert len(list((data_dir / "incidents").glob("*.yaml"))) == 1
        assert len(list((data_dir / "rules").glob("*.yaml"))) == 0

    def test_incident_load_error_propagates(self, tmp_path, monkeypatch):
        """IncidentLoadError propagates from process_incident."""
        data_dir = tmp_path / "data"
        with pytest.raises(IncidentLoadError):
            process_incident("nonexistent_file.txt", str(data_dir))


# ---------------------------------------------------------------------------
# main() — CLI entry point
# ---------------------------------------------------------------------------
class TestMainCLI:
    def test_no_command_exits(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["ees"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    def test_process_command_incident_load_error(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("sys.argv", [
            "ees", "process", "--incident", "no_such_file.txt",
            "--data-dir", str(tmp_path / "data"),
        ])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_process_command_config_error(self, tmp_path, monkeypatch, capsys):
        incident = tmp_path / "inc.txt"
        incident.write_text("text")
        monkeypatch.setattr("sys.argv", [
            "ees", "process", "--incident", str(incident),
            "--data-dir", str(tmp_path / "data"),
        ])
        # FactExtractor.__init__ will raise ConfigError since env vars aren't set
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
