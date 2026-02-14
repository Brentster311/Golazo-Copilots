"""Tests for ees.models — v2 rule grammar."""
from __future__ import annotations

import pytest
from ees.models import (
    EvaluationResult,
    Fact,
    Rule,
    RuleConditions,
    RuleOutput,
    RuleThen,
    VALID_OUTPUT_KINDS,
)


# ============================================================================
# Fact
# ============================================================================

class TestFact:
    """Tests for Fact construction, parsing, serialisation."""

    def test_basic_construction(self):
        f = Fact(noun="CPU", instance="host1", property="Usage", operator=">=", value="90")
        assert f.noun == "CPU"
        assert f.instance == "host1"
        assert f.property == "Usage"
        assert f.operator == ">="
        assert f.value == "90"

    def test_default_status_scope(self):
        f = Fact(noun="N", instance="*", property="P", operator="==", value="V")
        assert f.status == "confirmed"
        assert f.scope == "rule"

    def test_to_display(self):
        f = Fact(noun="CPU", instance="host1", property="Usage", operator=">=", value="90")
        assert f.to_display() == "CPU(host1).Usage >= 90"

    def test_match_key_case_insensitive(self):
        f1 = Fact(noun="Cpu", instance="h1", property="Usage", operator="==", value="hi")
        f2 = Fact(noun="cpu", instance="h1", property="usage", operator="==", value="hi")
        assert f1.match_key() == f2.match_key()

    def test_match_key_value_case_sensitive(self):
        f1 = Fact(noun="N", instance="*", property="P", operator="==", value="Hi")
        f2 = Fact(noun="N", instance="*", property="P", operator="==", value="hi")
        assert f1.match_key() != f2.match_key()

    def test_parse_valid(self):
        f = Fact.parse("CPU(host1).Usage >= 90")
        assert f is not None
        assert f.noun == "CPU"
        assert f.instance == "host1"
        assert f.value == "90"

    def test_parse_invalid(self):
        assert Fact.parse("not a fact") is None

    def test_parse_all_operators(self):
        for op in ("==", "!=", ">", "<", ">=", "<=", "contains", "!contains"):
            f = Fact.parse(f"N(i).P {op} V")
            assert f is not None, f"Failed for operator {op}"
            assert f.operator == op

    def test_to_dict(self):
        f = Fact(noun="N", instance="i", property="P", operator="==", value="V")
        d = f.to_dict()
        assert d["status"] == "confirmed"
        assert d["scope"] == "rule"

    def test_from_dict(self):
        d = {"noun": "N", "instance": "i", "property": "P", "operator": "==", "value": "V"}
        f = Fact.from_dict(d)
        assert f.noun == "N"
        assert f.status == "confirmed"

    def test_round_trip(self):
        f = Fact(noun="N", instance="i", property="P", operator="contains", value="abc")
        assert Fact.from_dict(f.to_dict()).to_dict() == f.to_dict()

    def test_to_condition_dict(self):
        f = Fact(noun="N", instance="i", property="P", operator="==", value="V")
        d = f.to_condition_dict()
        assert "status" not in d
        assert "scope" not in d

    # ---- variable helpers ----

    def test_is_variable(self):
        assert Fact.is_variable("$x")
        assert not Fact.is_variable("x")
        assert not Fact.is_variable("$")  # too short

    def test_has_variables(self):
        f = Fact(noun="N", instance="$host", property="P", operator="==", value="V")
        assert f.has_variable_instance
        assert not f.has_variable_value
        assert f.has_variables


# ============================================================================
# RuleConditions
# ============================================================================

class TestRuleConditions:
    def test_and_conditions(self):
        rc = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="A", instance="*", property="P", operator="==", value="1"),
                Fact(noun="B", instance="*", property="Q", operator="==", value="2"),
            ],
        )
        assert rc.logic == "AND"
        assert len(rc.items) == 2

    def test_round_trip(self):
        rc = RuleConditions(
            logic="OR",
            items=[Fact(noun="X", instance="*", property="Y", operator="!=", value="Z")],
        )
        assert RuleConditions.from_dict(rc.to_dict()).to_dict() == rc.to_dict()


# ============================================================================
# RuleOutput  (TC1)
# ============================================================================

class TestRuleOutput:
    def test_rule_output_change_state(self):
        o = RuleOutput(kind="CHANGE_STATE", description="Mail.Send permission => true")
        assert o.kind == "CHANGE_STATE"
        assert o.description == "Mail.Send permission => true"

    def test_rule_output_ruled_out(self):
        o = RuleOutput(kind="RULED_OUT", description="Network latency is not the cause")
        assert o.kind == "RULED_OUT"
        assert o.description == "Network latency is not the cause"

    def test_rule_output_gap(self):
        o = RuleOutput(kind="GAP", description="Need disk I/O data")
        assert o.kind == "GAP"
        assert o.description == "Need disk I/O data"

    def test_to_dict(self):
        o = RuleOutput(kind="CHANGE_STATE", description="X")
        assert o.to_dict() == {"kind": "CHANGE_STATE", "description": "X"}

    def test_from_dict(self):
        o = RuleOutput.from_dict({"kind": "RULED_OUT", "description": "Y"})
        assert o.kind == "RULED_OUT"
        assert o.description == "Y"

    def test_to_fact(self):
        o = RuleOutput(kind="CHANGE_STATE", description="Enable feature X")
        f = o.to_fact()
        assert f.noun == "CHANGE_STATE"
        assert f.instance == "*"
        assert f.property == "description"
        assert f.operator == "=="
        assert f.value == "Enable feature X"

    def test_to_fact_ruled_out(self):
        o = RuleOutput(kind="RULED_OUT", description="DNS ruled out")
        f = o.to_fact()
        assert f.noun == "RULED_OUT"
        assert f.value == "DNS ruled out"

    def test_valid_output_kinds(self):
        assert VALID_OUTPUT_KINDS == ("CHANGE_STATE", "RULED_OUT", "GAP")


# ============================================================================
# RuleThen (deprecated alias)
# ============================================================================

class TestRuleThenDeprecated:
    def test_can_import_and_construct(self):
        rt = RuleThen(noun="RootCause", instance="*", property="Name", value="HighCPU")
        assert rt.noun == "RootCause"
        assert rt.value == "HighCPU"

    def test_to_dict(self):
        rt = RuleThen(noun="N", instance="i", property="P", value="V")
        d = rt.to_dict()
        assert d == {"noun": "N", "instance": "i", "property": "P", "value": "V"}

    def test_from_dict(self):
        rt = RuleThen.from_dict({"noun": "N", "instance": "i", "property": "P", "value": "V"})
        assert rt.noun == "N"


# ============================================================================
# Rule  (TC2, TC3)
# ============================================================================

def _make_cond(*pairs: tuple[str, str]) -> RuleConditions:
    """Helper: create AND conditions from (noun, value) pairs."""
    return RuleConditions(
        logic="AND",
        items=[
            Fact(noun=n, instance="*", property="Status", operator="==", value=v)
            for n, v in pairs
        ],
    )


class TestRule:
    def test_rule_without_else(self):
        r = Rule(
            rule_id="R1",
            conditions=_make_cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="Investigate CPU"),
        )
        assert r.else_ is None

    def test_rule_with_else(self):
        r = Rule(
            rule_id="R2",
            conditions=_make_cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU is root cause"),
            else_=RuleOutput(kind="RULED_OUT", description="CPU ruled out"),
        )
        assert r.else_ is not None
        assert r.else_.kind == "RULED_OUT"

    def test_to_dict_then_only(self):
        r = Rule(
            rule_id="R1",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="GAP", description="need data"),
        )
        d = r.to_dict()
        assert "then" in d
        assert "else" not in d
        assert d["then"]["kind"] == "GAP"

    def test_to_dict_with_else(self):
        r = Rule(
            rule_id="R1",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="y"),
        )
        d = r.to_dict()
        assert "then" in d
        assert "else" in d
        assert d["else"]["kind"] == "RULED_OUT"

    def test_from_dict_then_only(self):
        d = {
            "rule_id": "R1",
            "conditions": {"logic": "AND", "items": []},
            "then": {"kind": "CHANGE_STATE", "description": "x"},
        }
        r = Rule.from_dict(d)
        assert r.then.kind == "CHANGE_STATE"
        assert r.else_ is None

    def test_from_dict_with_else(self):
        d = {
            "rule_id": "R1",
            "conditions": {"logic": "AND", "items": []},
            "then": {"kind": "CHANGE_STATE", "description": "x"},
            "else": {"kind": "RULED_OUT", "description": "y"},
        }
        r = Rule.from_dict(d)
        assert r.else_ is not None
        assert r.else_.kind == "RULED_OUT"

    def test_rule_round_trip(self):
        r = Rule(
            rule_id="R1",
            status="CONFIRMED",
            sources=["incident-1"],
            conditions=_make_cond(("CPU", "High"), ("Memory", "Low")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU+Memory issue"),
            else_=RuleOutput(kind="RULED_OUT", description="Not CPU+Memory"),
        )
        d1 = r.to_dict()
        r2 = Rule.from_dict(d1)
        d2 = r2.to_dict()
        assert d1 == d2

    def test_is_duplicate_same(self):
        r1 = Rule(
            rule_id="R1",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        r2 = Rule(
            rule_id="R2",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        assert r1.is_duplicate_of(r2)

    def test_is_duplicate_different_then(self):
        r1 = Rule(
            rule_id="R1",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        r2 = Rule(
            rule_id="R2",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="RULED_OUT", description="x"),
        )
        assert not r1.is_duplicate_of(r2)

    def test_is_duplicate_different_else(self):
        r1 = Rule(
            rule_id="R1",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="y"),
        )
        r2 = Rule(
            rule_id="R2",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="z"),
        )
        assert not r1.is_duplicate_of(r2)

    def test_is_duplicate_null_else_vs_present(self):
        r1 = Rule(
            rule_id="R1",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        r2 = Rule(
            rule_id="R2",
            conditions=_make_cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="y"),
        )
        assert not r1.is_duplicate_of(r2)

    def test_default_status(self):
        r = Rule(rule_id="R1")
        assert r.status == "CONFIRMED"


# ============================================================================
# EvaluationResult  (TC11)
# ============================================================================

class TestEvaluationResult:
    def _make_result(self) -> EvaluationResult:
        """Build a result with one of each output kind."""
        cs = RuleOutput(kind="CHANGE_STATE", description="state A")
        ro = RuleOutput(kind="RULED_OUT", description="ruled B")
        gp = RuleOutput(kind="GAP", description="gap C")
        r1 = Rule(rule_id="R1", then=cs)
        r2 = Rule(rule_id="R2", then=ro)
        r3 = Rule(rule_id="R3", then=gp)
        return EvaluationResult(
            input_facts=[],
            derived_facts=[],
            fired_rules=[r1, r2, r3],
            outputs=[
                {"rule_id": "R1", "branch": "then", "output": cs},
                {"rule_id": "R2", "branch": "then", "output": ro},
                {"rule_id": "R3", "branch": "then", "output": gp},
            ],
            rule_trace=[],
        )

    def test_result_change_states(self):
        r = self._make_result()
        assert r.change_states == ["state A"]

    def test_result_ruled_outs(self):
        r = self._make_result()
        assert r.ruled_outs == ["ruled B"]

    def test_result_gaps(self):
        r = self._make_result()
        assert r.gaps == ["gap C"]

    def test_backward_compat_root_causes(self):
        r = self._make_result()
        assert r.root_causes == r.change_states

    def test_backward_compat_ruled_out(self):
        r = self._make_result()
        assert r.ruled_out == r.ruled_outs

    def test_backward_compat_gap_rules(self):
        r = self._make_result()
        gap_rules = r.gap_rules
        assert len(gap_rules) == 1
        assert gap_rules[0].rule_id == "R3"

    def test_to_dict(self):
        r = self._make_result()
        d = r.to_dict()
        assert len(d["outputs"]) == 3
        assert d["outputs"][0]["kind"] == "CHANGE_STATE"
        assert d["outputs"][0]["branch"] == "then"

    def test_empty_result(self):
        r = EvaluationResult(
            input_facts=[], derived_facts=[], fired_rules=[],
            outputs=[], rule_trace=[],
        )
        assert r.change_states == []
        assert r.ruled_outs == []
        assert r.gaps == []
