"""Tests for data models."""
import pytest

from ees.models import (
    EvaluationResult,
    Fact,
    GapRefinement,
    Incident,
    LLMResponse,
    OntologyNoun,
    OntologyProperty,
    RootCause,
    Rule,
    RuleConditions,
    RuleThen,
    VALID_OPERATORS,
)


class TestFactParse:
    """Test Fact.parse() for valid and invalid inputs."""

    def test_parse_basic(self):
        f = Fact.parse("Server(*).CPUUsage > 90")
        assert f is not None
        assert f.noun == "Server"
        assert f.instance == "*"
        assert f.property == "CPUUsage"
        assert f.operator == ">"
        assert f.value == "90"

    def test_parse_specific_instance(self):
        f = Fact.parse("Server(WebApp01).CPUUsage > 90")
        assert f is not None
        assert f.instance == "WebApp01"

    def test_parse_all_operators(self):
        for op in VALID_OPERATORS:
            f = Fact.parse(f"Server(*).Prop {op} val")
            assert f is not None, f"Failed to parse operator: {op}"
            assert f.operator == op

    def test_parse_contains_operator(self):
        f = Fact.parse("Log(*).Message contains OutOfMemory")
        assert f is not None
        assert f.operator == "contains"
        assert f.value == "OutOfMemory"

    def test_parse_not_contains_operator(self):
        f = Fact.parse("Log(*).Message !contains Success")
        assert f is not None
        assert f.operator == "!contains"

    def test_parse_value_with_percent(self):
        f = Fact.parse("Server(*).MemoryFree < 5%")
        assert f is not None
        assert f.value == "5%"

    def test_parse_value_with_unit(self):
        f = Fact.parse("App(*).ResponseTime > 10s")
        assert f is not None
        assert f.value == "10s"

    def test_parse_invalid_no_parens(self):
        assert Fact.parse("Server.CPUUsage > 90") is None

    def test_parse_invalid_no_operator(self):
        assert Fact.parse("Server(*).CPUUsage 90") is None

    def test_parse_invalid_empty(self):
        assert Fact.parse("") is None

    def test_parse_invalid_garbage(self):
        assert Fact.parse("blah blah") is None

    def test_parse_invalid_missing_property(self):
        assert Fact.parse("Server(*) > 90") is None

    def test_parse_strips_whitespace(self):
        f = Fact.parse("  Server(*).CPUUsage  >  90  ")
        assert f is not None
        assert f.value == "90"


class TestFactDisplay:
    def test_to_display(self):
        f = Fact(noun="Server", instance="*", property="CPUUsage", operator=">", value="90")
        assert f.to_display() == "Server(*).CPUUsage > 90"

    def test_to_display_specific(self):
        f = Fact(noun="Server", instance="WebApp01", property="CPUUsage", operator=">", value="90")
        assert f.to_display() == "Server(WebApp01).CPUUsage > 90"


class TestFactMatchKey:
    def test_match_key_normalizes_case(self):
        f = Fact(noun="Server", instance="*", property="CPUUsage", operator=">", value="90")
        assert f.match_key() == ("server", "*", "cpuusage", ">", "90")

    def test_match_key_preserves_instance(self):
        f = Fact(noun="Server", instance="WebApp01", property="CPUUsage", operator=">", value="90")
        assert f.match_key()[1] == "WebApp01"

    def test_match_key_equality(self):
        f1 = Fact(noun="Server", instance="*", property="CPUUsage", operator=">", value="90")
        f2 = Fact(noun="server", instance="*", property="cpuusage", operator=">", value="90")
        assert f1.match_key() == f2.match_key()


class TestFactSerialization:
    def test_roundtrip(self):
        f = Fact(noun="Server", instance="*", property="CPUUsage", operator=">", value="90", status="confirmed")
        d = f.to_dict()
        f2 = Fact.from_dict(d)
        assert f == f2

    def test_from_dict_default_status(self):
        d = {"noun": "A", "instance": "*", "property": "B", "operator": "==", "value": "1"}
        f = Fact.from_dict(d)
        assert f.status == "confirmed"


class TestRuleConditions:
    def test_roundtrip(self):
        rc = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="Server", instance="*", property="CPU", operator=">", value="90"),
                Fact(noun="Server", instance="*", property="Mem", operator="<", value="5%"),
            ],
        )
        d = rc.to_dict()
        assert d["logic"] == "AND"
        assert len(d["items"]) == 2
        rc2 = RuleConditions.from_dict(d)
        assert rc2.logic == "AND"
        assert len(rc2.items) == 2


class TestRule:
    def test_roundtrip(self):
        r = Rule(
            rule_id="R-001",
            sources=["INC-001"],
            conditions=RuleConditions(
                logic="AND",
                items=[Fact(noun="S", instance="*", property="P", operator=">", value="1")],
            ),
            then=RuleThen(noun="S", instance="*", property="X", value="TRUE"),
            because="test reason",
        )
        d = r.to_dict()
        r2 = Rule.from_dict(d)
        assert r2.rule_id == "R-001"
        assert r2.because == "test reason"
        assert len(r2.conditions.items) == 1

    def test_is_duplicate(self):
        r1 = Rule(
            rule_id="R-001",
            conditions=RuleConditions(logic="AND", items=[Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
        )
        r2 = Rule(
            rule_id="R-002",
            conditions=RuleConditions(logic="AND", items=[Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
        )
        assert r1.is_duplicate_of(r2)

    def test_is_not_duplicate_different_conditions(self):
        r1 = Rule(
            rule_id="R-001",
            conditions=RuleConditions(logic="AND", items=[Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
        )
        r2 = Rule(
            rule_id="R-002",
            conditions=RuleConditions(logic="AND", items=[Fact("S", "*", "P", ">", "2")]),
            then=RuleThen("S", "*", "X", "TRUE"),
        )
        assert not r1.is_duplicate_of(r2)


class TestIncident:
    def test_roundtrip(self):
        inc = Incident(
            incident_id="INC-001",
            source_text="Some incident text",
            facts=[Fact("S", "*", "P", ">", "1")],
            root_cause_identified="Resource Exhaustion",
            processed_at="2026-02-12T10:00:00",
        )
        d = inc.to_dict()
        inc2 = Incident.from_dict(d)
        assert inc2.incident_id == "INC-001"
        assert inc2.root_cause_identified == "Resource Exhaustion"
        assert len(inc2.facts) == 1

    def test_auto_timestamp(self):
        inc = Incident(incident_id="INC-001", source_text="text")
        assert inc.processed_at  # should be non-empty


class TestOntologyNoun:
    def test_has_property_case_insensitive(self):
        noun = OntologyNoun(name="Server", properties=[OntologyProperty(name="CPUUsage")])
        assert noun.has_property("cpuusage")
        assert noun.has_property("CPUUsage")
        assert noun.has_property("CPUUSAGE")
        assert not noun.has_property("DiskIO")

    def test_roundtrip(self):
        noun = OntologyNoun(name="Server", properties=[OntologyProperty(name="CPU", type="numeric")])
        d = noun.to_dict()
        noun2 = OntologyNoun.from_dict(d)
        assert noun2.name == "Server"
        assert noun2.properties[0].type == "numeric"


class TestRootCause:
    def test_roundtrip(self):
        rc = RootCause(name="Resource Exhaustion", action_plan=None)
        d = rc.to_dict()
        rc2 = RootCause.from_dict(d)
        assert rc2.name == "Resource Exhaustion"
        assert rc2.action_plan is None


# ── GAP Rule Model Tests (EES-00002) ──────────────────────────────────


class TestRuleGapFields:
    """TC-07, TC-08, TC-09, TC-10: GAP rule model extensions."""

    def test_gap_rule_required_fields(self):
        """TC-07: GAP rule has requires, produces, note fields."""
        r = Rule(
            rule_id="R-010",
            status="GAP",
            sources=["INC-001"],
            requires=[Fact("Server", "*", "CPUUsage", ">", "90")],
            produces=[Fact("RootCause", "*", "Name", "==", "Resource Exhaustion")],
            note="Unknown intermediate steps",
            because="Orphaned facts detected",
        )
        assert isinstance(r.requires, list)
        assert isinstance(r.produces, list)
        assert isinstance(r.note, str)
        assert len(r.requires) == 1
        assert len(r.produces) == 1
        assert r.note == "Unknown intermediate steps"

    def test_gap_rule_status(self):
        """TC-08: GAP rule status is 'GAP'."""
        r = Rule(rule_id="R-010", status="GAP")
        assert r.status == "GAP"

    def test_gap_rule_roundtrip(self):
        """TC-09: GAP rule roundtrip serialization."""
        r = Rule(
            rule_id="R-010",
            status="GAP",
            sources=["INC-001"],
            requires=[Fact("Server", "*", "CPUUsage", ">", "90")],
            produces=[Fact("RootCause", "*", "Name", "==", "Resource Exhaustion")],
            note="Unknown intermediate steps",
            because="Orphaned facts detected",
        )
        d = r.to_dict()
        r2 = Rule.from_dict(d)
        assert r2.status == "GAP"
        assert len(r2.requires) == 1
        assert r2.requires[0].noun == "Server"
        assert len(r2.produces) == 1
        assert r2.produces[0].value == "Resource Exhaustion"
        assert r2.note == "Unknown intermediate steps"

    def test_confirmed_rule_backward_compat(self):
        """TC-10: Existing CONFIRMED rule YAML (no requires/produces) loads cleanly."""
        d = {
            "rule_id": "R-001",
            "status": "CONFIRMED",
            "type": "positive",
            "sources": ["INC-001"],
            "conditions": {"logic": "AND", "items": [
                {"noun": "S", "instance": "*", "property": "P", "operator": ">", "value": "1"}
            ]},
            "then": {"noun": "S", "instance": "*", "property": "X", "value": "TRUE"},
            "because": "reason",
        }
        r = Rule.from_dict(d)
        assert r.requires == []
        assert r.produces == []
        assert r.note == ""

    def test_resolved_status(self):
        """RESOLVED status is accepted."""
        r = Rule(rule_id="R-010", status="RESOLVED")
        assert r.status == "RESOLVED"

    def test_to_dict_omits_empty_gap_fields(self):
        """CONFIRMED rule to_dict omits requires/produces/note when default."""
        r = Rule(rule_id="R-001", status="CONFIRMED", because="reason")
        d = r.to_dict()
        assert "requires" not in d
        assert "produces" not in d
        assert "note" not in d

    def test_to_dict_includes_gap_fields_when_set(self):
        """GAP rule to_dict includes requires/produces/note."""
        r = Rule(
            rule_id="R-010",
            status="GAP",
            requires=[Fact("S", "*", "P", ">", "1")],
            produces=[Fact("RootCause", "*", "Name", "==", "X")],
            note="Some note",
        )
        d = r.to_dict()
        assert "requires" in d
        assert "produces" in d
        assert "note" in d
        assert len(d["requires"]) == 1
        assert d["requires"][0]["noun"] == "S"
        # requires/produces items should NOT include status
        assert "status" not in d["requires"][0]


class TestGapRefinement:
    """TC-14 related: GapRefinement dataclass."""

    def test_creation(self):
        gap = Rule(rule_id="R-010", status="GAP")
        ref = GapRefinement(
            gap_rule_id="R-010",
            action="resolved",
            updated_rule=gap,
        )
        assert ref.gap_rule_id == "R-010"
        assert ref.action == "resolved"
        assert ref.updated_rule is gap

    def test_narrowed_action(self):
        gap = Rule(rule_id="R-011", status="GAP")
        ref = GapRefinement(gap_rule_id="R-011", action="narrowed", updated_rule=gap)
        assert ref.action == "narrowed"


# ── RULEOUT Rule Model Tests (EES-00003) ──────────────────────────────


class TestRuleRuleoutType:
    """Tests for RULEOUT rule type support."""

    def test_ruleout_type_accepted(self):
        """TC-07: Rule with type='ruleout' is valid."""
        r = Rule(
            rule_id="R-020",
            status="CONFIRMED",
            type="ruleout",
            sources=["INC-001"],
            conditions=RuleConditions("AND", [Fact("S", "*", "Latency", "==", "normal")]),
            then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
            because="Normal latency rules out network issue",
        )
        assert r.type == "ruleout"
        assert r.then.noun == "RULEOUT"
        assert r.then.value == "Network Issue"

    def test_ruleout_to_dict(self):
        """TC-07: RULEOUT rule serializes with type='ruleout'."""
        r = Rule(
            rule_id="R-020",
            type="ruleout",
            conditions=RuleConditions("AND", [Fact("S", "*", "P", "==", "v")]),
            then=RuleThen("RULEOUT", "*", "Target", "SomeRC"),
            because="reason",
        )
        d = r.to_dict()
        assert d["type"] == "ruleout"
        assert d["then"]["noun"] == "RULEOUT"
        assert d["then"]["value"] == "SomeRC"

    def test_ruleout_roundtrip(self):
        """TC-08: RULEOUT rule round-trips through to_dict/from_dict."""
        r = Rule(
            rule_id="R-020",
            status="CONFIRMED",
            type="ruleout",
            sources=["INC-002"],
            conditions=RuleConditions("AND", [Fact("Net", "*", "Latency", "==", "normal")]),
            then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
            because="Normal latency rules out network issue",
        )
        d = r.to_dict()
        r2 = Rule.from_dict(d)
        assert r2.type == "ruleout"
        assert r2.then.noun == "RULEOUT"
        assert r2.then.value == "Network Issue"
        assert r2.because == "Normal latency rules out network issue"
        assert r2.sources == ["INC-002"]

    def test_from_dict_no_type_defaults_positive(self):
        """TC-09: from_dict without type key defaults to 'positive'."""
        d = {
            "rule_id": "R-001",
            "sources": [],
            "conditions": {"logic": "AND", "items": []},
            "then": {"noun": "S", "instance": "*", "property": "X", "value": "Y"},
            "because": "r",
        }
        r = Rule.from_dict(d)
        assert r.type == "positive"

    def test_ruleout_with_gap_status(self):
        """TC-12: RULEOUT rule with GAP status is valid combination."""
        r = Rule(
            rule_id="R-030",
            status="GAP",
            type="ruleout",
            sources=["INC-003"],
            requires=[Fact("S", "*", "P", ">", "1")],
            produces=[Fact("RULEOUT", "*", "Target", "==", "SomeRC")],
            note="Unknown RULEOUT reasoning",
        )
        d = r.to_dict()
        r2 = Rule.from_dict(d)
        assert r2.type == "ruleout"
        assert r2.status == "GAP"
        assert len(r2.requires) == 1

    def test_ruleout_with_confirmed_status(self):
        """TC-11: RULEOUT rule with CONFIRMED status and sources."""
        r = Rule(
            rule_id="R-020",
            status="CONFIRMED",
            type="ruleout",
            sources=["INC-001", "INC-002"],
            conditions=RuleConditions("AND", [Fact("S", "*", "P", "==", "v")]),
            then=RuleThen("RULEOUT", "*", "Target", "RC1"),
            because="Explanation",
        )
        assert r.status == "CONFIRMED"
        assert r.sources == ["INC-001", "INC-002"]
        assert r.because == "Explanation"


# ── EvaluationResult tests ────────────────────────────────────

class TestEvaluationResult:
    """Tests for EvaluationResult dataclass."""

    def test_empty_result(self):
        """EvaluationResult with defaults is all empty."""
        result = EvaluationResult(
            input_facts=[],
            derived_facts=[],
            fired_rules=[],
            root_causes=[],
            ruled_out=[],
            gap_rules=[],
            rule_trace=[],
        )
        assert result.input_facts == []
        assert result.root_causes == []

    def test_to_dict_all_keys(self):
        """to_dict returns all expected keys."""
        f = Fact("Server", "*", "CPUUsage", ">", "90")
        r = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [f]),
            then=RuleThen("RootCause", "*", "Name", "HighCPU"),
            because="test",
        )
        result = EvaluationResult(
            input_facts=[f],
            derived_facts=[Fact("RootCause", "*", "Name", "==", "HighCPU")],
            fired_rules=[r],
            root_causes=["HighCPU"],
            ruled_out=[],
            gap_rules=[],
            rule_trace=[{"rule_id": "R-001", "iteration": 1, "derived": "RootCause(*).Name == HighCPU"}],
        )
        d = result.to_dict()
        expected_keys = {"input_facts", "derived_facts", "fired_rules",
                         "root_causes", "ruled_out", "gap_rules", "rule_trace"}
        assert set(d.keys()) == expected_keys

    def test_to_dict_serializes_facts(self):
        """to_dict serializes facts via to_condition_dict."""
        f = Fact("Server", "*", "CPUUsage", ">", "90")
        result = EvaluationResult(
            input_facts=[f],
            derived_facts=[],
            fired_rules=[],
            root_causes=[],
            ruled_out=[],
            gap_rules=[],
            rule_trace=[],
        )
        d = result.to_dict()
        assert d["input_facts"][0]["noun"] == "Server"

    def test_to_dict_serializes_rules(self):
        """to_dict serializes fired_rules via Rule.to_dict."""
        r = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [Fact("S", "*", "P", "==", "v")]),
            then=RuleThen("RootCause", "*", "Name", "X"),
            because="test",
        )
        result = EvaluationResult(
            input_facts=[],
            derived_facts=[],
            fired_rules=[r],
            root_causes=["X"],
            ruled_out=[],
            gap_rules=[],
            rule_trace=[],
        )
        d = result.to_dict()
        assert d["fired_rules"][0]["rule_id"] == "R-001"
