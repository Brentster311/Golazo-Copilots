"""Tests for ees.models — v2 rule grammar."""
from __future__ import annotations

import pytest
from ees.models import (
    EvaluationResult,
    Fact,
    Goal,
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
        assert f.property == "Enable feature X"
        assert f.operator == "=="
        assert f.value == "true"

    def test_to_fact_ruled_out(self):
        o = RuleOutput(kind="RULED_OUT", description="DNS ruled out")
        f = o.to_fact()
        assert f.noun == "RULED_OUT"
        assert f.property == "DNS ruled out"
        assert f.value == "true"

    def test_valid_output_kinds(self):
        assert VALID_OUTPUT_KINDS == ("CHANGE_STATE", "RULED_OUT", "GAP")


# ============================================================================
# EES-00017: Structured RuleOutput with typed state transitions
# ============================================================================


class TestRuleOutputStructuredToFact:
    """TC-17-01 through TC-17-05: RuleOutput.to_fact() — structured path."""

    def test_structured_change_state_produces_correct_fact(self):
        """TC-17-01: Structured CHANGE_STATE produces real ontology fact."""
        o = RuleOutput(
            kind="CHANGE_STATE", description="",
            target_noun="User", target_instance="$u",
            target_property="adminRole", value="confirmed",
        )
        f = o.to_fact()
        assert f.noun == "User"
        assert f.instance == "$u"
        assert f.property == "adminRole"
        assert f.operator == "=="
        assert f.value == "confirmed"

    def test_structured_change_state_wildcard_instance(self):
        """TC-17-02: None instance defaults to wildcard '*'."""
        o = RuleOutput(
            kind="CHANGE_STATE", description="",
            target_noun="Tenant", target_instance=None,
            target_property="status", value="active",
        )
        f = o.to_fact()
        assert f.noun == "Tenant"
        assert f.instance == "*"
        assert f.property == "status"
        assert f.value == "active"

    def test_legacy_change_state_produces_pseudo_fact(self):
        """TC-17-03: Legacy CHANGE_STATE unchanged."""
        o = RuleOutput("CHANGE_STATE", "User.adminRole => confirmed")
        f = o.to_fact()
        assert f.noun == "CHANGE_STATE"
        assert f.instance == "*"
        assert f.property == "User.adminRole => confirmed"
        assert f.value == "true"

    def test_ruled_out_to_fact_unchanged(self):
        """TC-17-04: RULED_OUT to_fact unchanged."""
        o = RuleOutput("RULED_OUT", "User.adminRole")
        f = o.to_fact()
        assert f.noun == "RULED_OUT"
        assert f.property == "User.adminRole"
        assert f.value == "true"

    def test_gap_to_fact_unchanged(self):
        """TC-17-05: GAP to_fact unchanged."""
        o = RuleOutput("GAP", "NeedMemoryData")
        f = o.to_fact()
        assert f.noun == "GAP"
        assert f.property == "NeedMemoryData"
        assert f.value == "true"


class TestRuleOutputValidate:
    """TC-17-06 through TC-17-13: RuleOutput.validate()."""

    def _make_ontology_mgr(self):
        from ees.ontology_manager import OntologyManager
        from ees.models import OntologyNoun, OntologyProperty
        return OntologyManager([
            OntologyNoun("User", [
                OntologyProperty("adminRole", "enum",
                                 values=["confirmed", "denied", "pending"],
                                 default="pending"),
            ]),
        ])

    def test_valid_structured_output(self):
        """TC-17-06: Valid structured CHANGE_STATE — no errors."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput(
            kind="CHANGE_STATE", description="",
            target_noun="User", target_instance="$u",
            target_property="adminRole", value="confirmed",
        )
        assert o.validate(mgr) == []

    def test_unknown_target_noun(self):
        """TC-17-07: Unknown target noun → error."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput(
            kind="CHANGE_STATE", description="",
            target_noun="Server", target_instance="*",
            target_property="cpu", value="high",
        )
        errors = o.validate(mgr)
        assert len(errors) == 1
        assert "Server" in errors[0]

    def test_unknown_target_property(self):
        """TC-17-08: Unknown target property → error."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput(
            kind="CHANGE_STATE", description="",
            target_noun="User", target_instance="$u",
            target_property="email", value="test",
        )
        errors = o.validate(mgr)
        assert len(errors) == 1
        assert "email" in errors[0]

    def test_invalid_target_value(self):
        """TC-17-09: Invalid value → error."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput(
            kind="CHANGE_STATE", description="",
            target_noun="User", target_instance="$u",
            target_property="adminRole", value="superadmin",
        )
        errors = o.validate(mgr)
        assert len(errors) == 1
        assert "superadmin" in errors[0]

    def test_legacy_change_state_no_validation(self):
        """TC-17-10: Legacy CHANGE_STATE — no validation."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput("CHANGE_STATE", "User.adminRole => confirmed")
        assert o.validate(mgr) == []

    def test_ruled_out_no_validation(self):
        """TC-17-11: RULED_OUT — no validation."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput("RULED_OUT", "User.adminRole")
        assert o.validate(mgr) == []

    def test_gap_no_validation(self):
        """TC-17-12: GAP — no validation."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput("GAP", "NeedMemoryData")
        assert o.validate(mgr) == []

    def test_partial_structured_fields_error(self):
        """TC-17-13: Partial structured fields → error."""
        mgr = self._make_ontology_mgr()
        o = RuleOutput(
            kind="CHANGE_STATE", description="",
            target_noun="User", target_instance=None,
            target_property=None, value=None,
        )
        errors = o.validate(mgr)
        assert len(errors) >= 1
        # Should indicate incomplete structured fields


class TestRuleOutputStructuredSerialization:
    """TC-17-14 through TC-17-21: RuleOutput serialization."""

    def test_to_dict_structured_change_state(self):
        """TC-17-14: to_dict with structured CHANGE_STATE."""
        o = RuleOutput(
            kind="CHANGE_STATE", description="human note",
            target_noun="User", target_instance="$u",
            target_property="adminRole", value="confirmed",
        )
        d = o.to_dict()
        assert d["kind"] == "CHANGE_STATE"
        assert d["description"] == "human note"
        assert d["target_noun"] == "User"
        assert d["target_instance"] == "$u"
        assert d["target_property"] == "adminRole"
        assert d["value"] == "confirmed"

    def test_to_dict_legacy_change_state(self):
        """TC-17-15: to_dict with legacy CHANGE_STATE (no structured fields)."""
        o = RuleOutput("CHANGE_STATE", "User.adminRole => confirmed")
        d = o.to_dict()
        assert d == {"kind": "CHANGE_STATE", "description": "User.adminRole => confirmed"}

    def test_to_dict_ruled_out(self):
        """TC-17-16: to_dict RULED_OUT."""
        o = RuleOutput("RULED_OUT", "User.adminRole")
        d = o.to_dict()
        assert d == {"kind": "RULED_OUT", "description": "User.adminRole"}

    def test_from_dict_structured(self):
        """TC-17-17: from_dict with structured fields."""
        d = {
            "kind": "CHANGE_STATE", "description": "",
            "target_noun": "Tenant", "target_instance": "*",
            "target_property": "status", "value": "active",
        }
        o = RuleOutput.from_dict(d)
        assert o.target_noun == "Tenant"
        assert o.target_instance == "*"
        assert o.target_property == "status"
        assert o.value == "active"

    def test_from_dict_legacy(self):
        """TC-17-18: from_dict with legacy format."""
        d = {"kind": "CHANGE_STATE", "description": "User.adminRole => confirmed"}
        o = RuleOutput.from_dict(d)
        assert o.target_noun is None
        assert o.description == "User.adminRole => confirmed"

    def test_from_dict_ruled_out(self):
        """TC-17-19: from_dict RULED_OUT."""
        d = {"kind": "RULED_OUT", "description": "User.adminRole"}
        o = RuleOutput.from_dict(d)
        assert o.target_noun is None

    def test_round_trip_structured(self):
        """TC-17-20: Round-trip for structured output."""
        o = RuleOutput(
            kind="CHANGE_STATE", description="note",
            target_noun="User", target_instance="$u",
            target_property="adminRole", value="confirmed",
        )
        o2 = RuleOutput.from_dict(o.to_dict())
        assert o2.target_noun == o.target_noun
        assert o2.target_instance == o.target_instance
        assert o2.target_property == o.target_property
        assert o2.value == o.value
        assert o2.description == o.description
        assert o2.kind == o.kind

    def test_round_trip_legacy(self):
        """TC-17-21: Round-trip for legacy output."""
        o = RuleOutput("CHANGE_STATE", "User.adminRole => confirmed")
        o2 = RuleOutput.from_dict(o.to_dict())
        assert o2.kind == o.kind
        assert o2.description == o.description
        assert o2.target_noun is None


class TestRuleOutputBackwardCompat:
    """TC-17-22 through TC-17-23: Backward compatibility."""

    def test_existing_constructions_still_work(self):
        """TC-17-22: Existing RuleOutput(kind, description) still works."""
        o = RuleOutput(kind="CHANGE_STATE", description="test")
        assert o.kind == "CHANGE_STATE"
        assert o.description == "test"
        assert o.target_noun is None
        assert o.target_instance is None
        assert o.target_property is None
        assert o.value is None

    def test_legacy_yaml_loads(self):
        """TC-17-23: Legacy YAML dict loads correctly."""
        d = {"kind": "CHANGE_STATE", "description": "User.adminRole => confirmed"}
        o = RuleOutput.from_dict(d)
        assert o.kind == "CHANGE_STATE"
        assert o.description == "User.adminRole => confirmed"
        assert o.target_noun is None


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


# ============================================================================
# EES-00018: Goal dataclass
# ============================================================================


class TestGoal:
    """TC-18-08 and TC-18-09: Goal construction and round-trip."""

    def test_construction(self):
        """TC-18-08: Goal construction."""
        g = Goal(
            noun="Incident", instance="$inc", property="rootCause",
            initial="unknown", terminal=["admin_role_missing", "token_expired"],
        )
        assert g.noun == "Incident"
        assert g.instance == "$inc"
        assert g.property == "rootCause"
        assert g.initial == "unknown"
        assert g.terminal == ["admin_role_missing", "token_expired"]

    def test_to_dict_from_dict_round_trip(self):
        """TC-18-09: Goal.to_dict and from_dict round-trip."""
        g = Goal(
            noun="Incident", instance="$inc", property="rootCause",
            initial="unknown", terminal=["admin_role_missing", "token_expired"],
        )
        g2 = Goal.from_dict(g.to_dict())
        assert g2.noun == g.noun
        assert g2.instance == g.instance
        assert g2.property == g.property
        assert g2.initial == g.initial
        assert g2.terminal == g.terminal


# ============================================================================
# EES-00018: EvaluationResult.goal_status
# ============================================================================


class TestEvaluationResultGoalStatus:
    """TC-18-10 through TC-18-13: EvaluationResult goal_status."""

    def test_with_goal_status(self):
        """TC-18-10: EvaluationResult with goal_status."""
        r = EvaluationResult(
            input_facts=[], derived_facts=[], fired_rules=[],
            outputs=[], rule_trace=[], goal_status="resolved",
        )
        assert r.goal_status == "resolved"

    def test_default_goal_status(self):
        """TC-18-11: EvaluationResult default goal_status."""
        r = EvaluationResult(
            input_facts=[], derived_facts=[], fired_rules=[],
            outputs=[], rule_trace=[],
        )
        assert r.goal_status is None

    def test_to_dict_includes_goal_status(self):
        """TC-18-12: to_dict includes goal_status."""
        r = EvaluationResult(
            input_facts=[], derived_facts=[], fired_rules=[],
            outputs=[], rule_trace=[], goal_status="escalated",
        )
        d = r.to_dict()
        assert d["goal_status"] == "escalated"

    def test_to_dict_goal_status_none(self):
        """TC-18-13: to_dict with goal_status=None."""
        r = EvaluationResult(
            input_facts=[], derived_facts=[], fired_rules=[],
            outputs=[], rule_trace=[],
        )
        d = r.to_dict()
        assert d["goal_status"] is None
