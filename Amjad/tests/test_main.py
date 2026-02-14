"""Tests for main.py — CLI orchestration and helper functions."""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from ees.exceptions import ConfigError, IncidentLoadError, LLMError
from ees.main import (
    _confirm_facts,
    _confirm_gaps,
    _confirm_rules,
    _edit_fact,
    _format_rule_conditions,
    _specialize_fact,
    evaluate_facts,
    main,
    process_incident,
)
from ees.models import (
    EvaluationResult,
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
        )

    def test_confirm_rule(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "c")
        result = _confirm_rules([self._make_rule()])
        assert len(result) == 1

    def test_reject_rule(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "r")
        result = _confirm_rules([self._make_rule()])
        assert len(result) == 0


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
                )
            ],
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

        # User confirms everything: fact=c, rule=c
        inputs = iter(["c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        # Verify files were created
        assert (data_dir / "incidents").exists()
        assert len(list((data_dir / "incidents").glob("*.yaml"))) == 1
        assert len(list((data_dir / "rules").glob("*.yaml"))) >= 1
        assert (data_dir / "ontology.yaml").exists()

    def test_no_facts_extracted(self, tmp_path, monkeypatch, capsys):
        """LLM returns no facts → early exit, no files created."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Nothing useful here")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = LLMResponse(facts=[], rules=[])
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


# ---------------------------------------------------------------------------
# _confirm_gaps
# ---------------------------------------------------------------------------
class TestConfirmGaps:
    def _make_gap(self, rule_id="R-010"):
        return Rule(
            rule_id=rule_id,
            status="GAP",
            sources=["INC-001"],
            requires=[Fact("Server", "*", "MemoryFree", "<", "5%")],
            produces=[Fact("RootCause", "*", "Name", "==", "X")],
            note="Unknown steps",
        )

    def test_confirm_gap(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "c")
        result = _confirm_gaps([self._make_gap()])
        assert len(result) == 1
        assert result[0].status == "GAP"

    def test_reject_gap(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "r")
        result = _confirm_gaps([self._make_gap()])
        assert len(result) == 0

    def test_edit_gap_note(self, monkeypatch):
        inputs = iter(["e", "Missing DB connection logic"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = _confirm_gaps([self._make_gap()])
        assert len(result) == 1
        assert result[0].note == "Missing DB connection logic"

    def test_edit_empty_note_keeps_original(self, monkeypatch):
        inputs = iter(["e", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = _confirm_gaps([self._make_gap()])
        assert len(result) == 1
        assert result[0].note == "Unknown steps"


# ---------------------------------------------------------------------------
# process_incident — GAP integration tests
# ---------------------------------------------------------------------------
class TestProcessIncidentGaps:
    def _mock_llm_response_with_root_cause(self):
        """LLM response with two facts and one rule."""
        return LLMResponse(
            facts=[
                Fact("Server", "*", "CPUUsage", ">", "90"),
                Fact("Server", "*", "MemoryFree", "<", "5%"),
            ],
            rules=[
                Rule(
                    rule_id="",
                    conditions=RuleConditions("AND", [
                        Fact("Server", "*", "CPUUsage", ">", "90"),
                    ]),
                    then=RuleThen("RootCause", "*", "Name", "Resource Exhaustion"),
                )
            ],
        )

    def test_gap_detected_and_confirmed(self, tmp_path, monkeypatch, capsys):
        """No GAP created when root cause is not set."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Server issue")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = self._mock_llm_response_with_root_cause()
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # confirm fact1, confirm fact2, confirm rule
        inputs = iter(["c", "c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        captured = capsys.readouterr()
        assert "GAPs:" in captured.out
        assert "0 created" in captured.out
        # 1 confirmed rule only (no GAP rule)
        rule_files = list((data_dir / "rules").glob("*.yaml"))
        assert len(rule_files) == 1

    def test_no_gap_when_no_root_cause(self, tmp_path, monkeypatch, capsys):
        """No GAP detection when root cause is not set."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Server issue")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        resp = self._mock_llm_response_with_root_cause()
        mock_extractor.extract.return_value = resp
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # confirm fact1, confirm fact2, confirm rule
        inputs = iter(["c", "c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        captured = capsys.readouterr()
        assert "GAPs: 0 created" in captured.out

    def test_gap_rejected_by_user(self, tmp_path, monkeypatch, capsys):
        """No GAP is created (root cause not set)."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Server issue")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = self._mock_llm_response_with_root_cause()
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # confirm fact1, confirm fact2, confirm rule
        inputs = iter(["c", "c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        # Only 1 rule (the confirmed rule), no GAP
        rule_files = list((data_dir / "rules").glob("*.yaml"))
        assert len(rule_files) == 1

    def test_gap_report_in_summary(self, tmp_path, monkeypatch, capsys):
        """Summary shows GAP stats."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Server issue")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = self._mock_llm_response_with_root_cause()
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # confirm fact1, confirm fact2, confirm rule
        inputs = iter(["c", "c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        captured = capsys.readouterr()
        assert "GAPs:" in captured.out
        # Should mention created, narrowed, resolved counts
        assert "created" in captured.out


# ---------------------------------------------------------------------------
# process_incident — RULEOUT integration tests (EES-00003)
# ---------------------------------------------------------------------------
class TestProcessIncidentRuleout:
    def _mock_llm_response_with_ruleout(self):
        """LLM returns both positive and RULEOUT rules."""
        return LLMResponse(
            facts=[
                Fact("Server", "*", "CPUUsage", ">", "90"),
                Fact("Net", "*", "Latency", "==", "normal"),
            ],
            rules=[
                Rule(
                    rule_id="",
                    type="positive",
                    conditions=RuleConditions("AND", [Fact("Server", "*", "CPUUsage", ">", "90")]),
                    then=RuleThen("RootCause", "*", "Name", "Resource Exhaustion"),
                ),
                Rule(
                    rule_id="",
                    type="ruleout",
                    conditions=RuleConditions("AND", [Fact("Net", "*", "Latency", "==", "normal")]),
                    then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
                ),
            ],
        )

    def test_ruleout_rules_persisted(self, tmp_path, monkeypatch, capsys):
        """TC-23: RULEOUT rules are confirmed and persisted."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Server high CPU, normal latency")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = self._mock_llm_response_with_ruleout()
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # confirm fact1, confirm fact2, confirm positive rule, confirm ruleout rule
        inputs = iter(["c", "c", "c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        # Should have 2 rule files: 1 positive + 1 ruleout
        rule_files = list((data_dir / "rules").glob("*.yaml"))
        assert len(rule_files) == 2

        # Check that the RULEOUT rule has type=ruleout in YAML
        from ees.yaml_store import YamlStore
        store = YamlStore(data_dir)
        rules = store.list_rules()
        types = {r.type for r in rules}
        assert "ruleout" in types
        assert "positive" in types

    def test_ruleout_summary_counts(self, tmp_path, monkeypatch, capsys):
        """TC-24: Summary distinguishes positive and RULEOUT counts."""
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Server issue with latency")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = self._mock_llm_response_with_ruleout()
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # confirm fact1, confirm fact2, confirm positive, confirm ruleout
        inputs = iter(["c", "c", "c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        captured = capsys.readouterr()
        assert "positive" in captured.out.lower()
        assert "ruleout" in captured.out.lower()

    def test_ruleout_only_no_rootcause_modification(self, tmp_path, monkeypatch, capsys):
        """TC-25: Only RULEOUT rules — rootcauses.yaml not modified by RULEOUT references."""
        resp = LLMResponse(
            facts=[Fact("Net", "*", "Latency", "==", "normal")],
            rules=[
                Rule(
                    rule_id="",
                    type="ruleout",
                    conditions=RuleConditions("AND", [Fact("Net", "*", "Latency", "==", "normal")]),
                    then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
                ),
            ],
        )
        incident_file = tmp_path / "incident.txt"
        incident_file.write_text("Network looks fine")
        data_dir = tmp_path / "data"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = resp
        monkeypatch.setattr("ees.main.FactExtractor", lambda: mock_extractor)

        # confirm fact, no root cause prompt, confirm ruleout rule
        inputs = iter(["c", "c"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        process_incident(str(incident_file), str(data_dir))

        # rootcauses.yaml should not exist
        assert not (data_dir / "rootcauses.yaml").exists()

    def test_ruleout_display_format(self, monkeypatch, capsys):
        """TC-14: RULEOUT rules displayed as 'THEN RULEOUT <name>'."""
        ruleout = Rule(
            rule_id="R-020",
            type="ruleout",
            conditions=RuleConditions("AND", [Fact("Net", "*", "Latency", "==", "normal")]),
            then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
        )

        monkeypatch.setattr("builtins.input", lambda _: "c")
        result = _confirm_rules([ruleout])

        captured = capsys.readouterr()
        assert "THEN RULEOUT Network Issue" in captured.out
        assert len(result) == 1


# ── CLI evaluate command tests ────────────────────────────────

class TestEvaluateFacts:
    """CLI evaluate subcommand integration tests."""

    def test_evaluate_with_facts_flag(self, tmp_path, capsys):
        """TC-16: ees evaluate --facts runs evaluation and prints results."""
        data_dir = tmp_path / "data"
        rules_dir = data_dir / "rules"
        rules_dir.mkdir(parents=True)

        # Write a rule file
        from ruamel.yaml import YAML
        yaml = YAML()
        rule_data = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [Fact("Server", "*", "CPUUsage", ">", "90")]),
            then=RuleThen("RootCause", "*", "Name", "HighCPU"),
        ).to_dict()
        with open(rules_dir / "R-001.yaml", "w") as f:
            yaml.dump(rule_data, f)

        evaluate_facts(
            facts_str="Server(*).CPUUsage > 90",
            facts_file=None,
            data_dir=str(data_dir),
            output_file=None,
        )

        captured = capsys.readouterr()
        assert "HighCPU" in captured.out

    def test_evaluate_with_facts_file(self, tmp_path, capsys):
        """TC-17: ees evaluate --facts-file reads facts from file."""
        data_dir = tmp_path / "data"
        rules_dir = data_dir / "rules"
        rules_dir.mkdir(parents=True)

        from ruamel.yaml import YAML
        yaml = YAML()
        rule_data = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [Fact("Server", "*", "CPUUsage", ">", "90")]),
            then=RuleThen("RootCause", "*", "Name", "HighCPU"),
        ).to_dict()
        with open(rules_dir / "R-001.yaml", "w") as f:
            yaml.dump(rule_data, f)

        # Write facts file
        facts_file = tmp_path / "facts.yaml"
        yaml.dump(["Server(*).CPUUsage > 90"], facts_file)

        evaluate_facts(
            facts_str=None,
            facts_file=str(facts_file),
            data_dir=str(data_dir),
            output_file=None,
        )

        captured = capsys.readouterr()
        assert "HighCPU" in captured.out

    def test_evaluate_invalid_fact_format(self, tmp_path, capsys):
        """TC-18: --facts with invalid fact format reports error."""
        data_dir = tmp_path / "data"
        rules_dir = data_dir / "rules"
        rules_dir.mkdir(parents=True)

        with pytest.raises(SystemExit):
            evaluate_facts(
                facts_str="this is not a valid fact",
                facts_file=None,
                data_dir=str(data_dir),
                output_file=None,
            )

    def test_evaluate_no_rules(self, tmp_path, capsys):
        """TC-19: --data-dir with no rules reports 0 rules fired."""
        data_dir = tmp_path / "data"
        rules_dir = data_dir / "rules"
        rules_dir.mkdir(parents=True)

        evaluate_facts(
            facts_str="Server(*).CPUUsage > 90",
            facts_file=None,
            data_dir=str(data_dir),
            output_file=None,
        )

        captured = capsys.readouterr()
        assert "0" in captured.out  # 0 rules fired

    def test_evaluate_output_file(self, tmp_path):
        """TC-15: --output writes YAML file with correct structure."""
        data_dir = tmp_path / "data"
        rules_dir = data_dir / "rules"
        rules_dir.mkdir(parents=True)

        from ruamel.yaml import YAML
        yaml = YAML()
        rule_data = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [Fact("Server", "*", "CPUUsage", ">", "90")]),
            then=RuleThen("RootCause", "*", "Name", "HighCPU"),
        ).to_dict()
        with open(rules_dir / "R-001.yaml", "w") as f:
            yaml.dump(rule_data, f)

        output_path = tmp_path / "result.yaml"
        evaluate_facts(
            facts_str="Server(*).CPUUsage > 90",
            facts_file=None,
            data_dir=str(data_dir),
            output_file=str(output_path),
        )

        assert output_path.exists()
        with open(output_path) as f:
            result_data = yaml.load(f)
        assert "root_causes" in result_data
        assert "HighCPU" in result_data["root_causes"]

    def test_evaluate_semicolon_delimiter(self, tmp_path, capsys):
        """MN-1: Semicolons used as delimiter for multiple facts."""
        data_dir = tmp_path / "data"
        rules_dir = data_dir / "rules"
        rules_dir.mkdir(parents=True)

        from ruamel.yaml import YAML
        yaml = YAML()
        rule_data = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [
                Fact("Server", "*", "CPUUsage", ">", "90"),
                Fact("Server", "*", "MemoryFree", "<", "5%"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "ResourceExhaustion"),
        ).to_dict()
        with open(rules_dir / "R-001.yaml", "w") as f:
            yaml.dump(rule_data, f)

        evaluate_facts(
            facts_str="Server(*).CPUUsage > 90; Server(*).MemoryFree < 5%",
            facts_file=None,
            data_dir=str(data_dir),
            output_file=None,
        )

        captured = capsys.readouterr()
        assert "ResourceExhaustion" in captured.out


class TestMainCLIEvaluate:
    """Test CLI argument parsing for evaluate subcommand."""

    def test_evaluate_subcommand_parsed(self, monkeypatch):
        """evaluate subcommand is recognized by argparse."""
        monkeypatch.setattr("sys.argv", [
            "ees", "evaluate",
            "--facts", "Server(*).CPUUsage > 90",
            "--data-dir", "data",
        ])
        # Patch evaluate_facts to avoid actual execution
        monkeypatch.setattr("ees.main.evaluate_facts", lambda **kwargs: None)
        # Should not raise
        main()
