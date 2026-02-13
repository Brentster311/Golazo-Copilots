"""Tests for data models."""
import pytest

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
