"""Tests for ees.rule_evaluator — v2 engine with THEN/ELSE branches."""
from __future__ import annotations

import pytest
from ees.models import (
    EvaluationResult,
    Fact,
    Rule,
    RuleConditions,
    RuleOutput,
)
from ees.rule_evaluator import RuleEvaluator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fact(noun: str, value: str, instance: str = "*", prop: str = "Status") -> Fact:
    """Shorthand for creating a confirmed Fact."""
    return Fact(noun=noun, instance=instance, property=prop, operator="==", value=value)


def _cond(*pairs: tuple[str, str], logic: str = "AND") -> RuleConditions:
    """Build conditions from (noun, value) pairs."""
    return RuleConditions(
        logic=logic,
        items=[_fact(n, v) for n, v in pairs],
    )


def _rule(
    rule_id: str,
    conditions: RuleConditions,
    then: RuleOutput,
    else_: RuleOutput | None = None,
    status: str = "CONFIRMED",
) -> Rule:
    return Rule(
        rule_id=rule_id,
        status=status,
        conditions=conditions,
        then=then,
        else_=else_,
    )


# ============================================================================
# TC4: Engine THEN Branch Fires
# ============================================================================

class TestThenBranchFires:
    def test_then_fires_change_state(self):
        """When conditions are met, THEN branch fires and derived fact is CHANGE_STATE."""
        r = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU is overloaded"),
        )
        facts = [_fact("CPU", "High")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 1
        assert result.outputs[0]["branch"] == "then"
        assert result.outputs[0]["output"].kind == "CHANGE_STATE"
        # Derived fact should be in working set
        assert any(
            f.noun == "CHANGE_STATE" and f.property == "CPU is overloaded"
            for f in result.derived_facts
        )

    def test_then_fires_ruled_out(self):
        """RULED_OUT via THEN branch produces a derived fact."""
        r = _rule(
            "R1",
            _cond(("DNS", "OK")),
            then=RuleOutput(kind="RULED_OUT", description="DNS is fine"),
        )
        facts = [_fact("DNS", "OK")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 1
        assert result.outputs[0]["output"].kind == "RULED_OUT"
        assert any(
            f.noun == "RULED_OUT" and f.property == "DNS is fine"
            for f in result.derived_facts
        )

    def test_then_fires_gap(self):
        """GAP via THEN branch is recorded but NOT added to working set."""
        r = _rule(
            "R1",
            _cond(("Disk", "Unknown")),
            then=RuleOutput(kind="GAP", description="Need disk I/O metrics"),
        )
        facts = [_fact("Disk", "Unknown")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 1
        assert result.outputs[0]["output"].kind == "GAP"
        # GAP must NOT appear in derived_facts (terminal)
        assert not any(f.noun == "GAP" for f in result.derived_facts)

    def test_no_fire_when_conditions_not_met_no_else(self):
        """Rule without ELSE does not fire when conditions are not met."""
        r = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        facts = [_fact("CPU", "Low")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 0
        assert len(result.outputs) == 0


# ============================================================================
# TC5: Engine ELSE Branch Fires
# ============================================================================

class TestElseBranchFires:
    def test_else_fires_when_conditions_not_met(self):
        """ELSE branch fires when conditions are NOT met."""
        r = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU is root cause"),
            else_=RuleOutput(kind="RULED_OUT", description="CPU ruled out"),
        )
        facts = [_fact("CPU", "Low")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 1
        assert result.outputs[0]["branch"] == "else"
        assert result.outputs[0]["output"].kind == "RULED_OUT"
        assert any(
            f.noun == "RULED_OUT" and f.property == "CPU ruled out"
            for f in result.derived_facts
        )

    def test_else_not_fired_when_no_else(self):
        """Rule without ELSE does not fire anything when conditions not met."""
        r = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            # No else_
        )
        facts = [_fact("CPU", "Low")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 0
        assert len(result.outputs) == 0

    def test_else_not_fired_when_then_fires(self):
        """When conditions ARE met, only THEN fires — ELSE is ignored."""
        r = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU root cause"),
            else_=RuleOutput(kind="RULED_OUT", description="CPU ruled out"),
        )
        facts = [_fact("CPU", "High")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 1
        assert result.outputs[0]["branch"] == "then"
        assert result.outputs[0]["output"].kind == "CHANGE_STATE"
        # ELSE output should NOT appear
        assert not any(
            o["output"].kind == "RULED_OUT" for o in result.outputs
        )


# ============================================================================
# TC6: Chaining RULED_OUT
# ============================================================================

class TestChainingRuledOut:
    def test_ruled_out_chains_as_condition(self):
        """RULED_OUT from R1 and R2 chains into R3's conditions."""
        r1 = _rule(
            "R1",
            _cond(("CPU", "OK")),
            then=RuleOutput(kind="RULED_OUT", description="CPU ruled out"),
        )
        r2 = _rule(
            "R2",
            _cond(("Memory", "OK")),
            then=RuleOutput(kind="RULED_OUT", description="Memory ruled out"),
        )
        # R3 conditions require both RULED_OUTs (dict syntax)
        r3_cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="RULED_OUT", instance="*", property="CPU ruled out",
                     operator="==", value="true"),
                Fact(noun="RULED_OUT", instance="*", property="Memory ruled out",
                     operator="==", value="true"),
            ],
        )
        r3 = _rule(
            "R3",
            r3_cond,
            then=RuleOutput(kind="CHANGE_STATE", description="Look at network"),
        )

        facts = [_fact("CPU", "OK"), _fact("Memory", "OK")]
        result = RuleEvaluator([r1, r2, r3]).evaluate(facts)

        assert len(result.fired_rules) == 3
        assert any(r.rule_id == "R3" for r in result.fired_rules)
        assert "Look at network" in result.change_states

    def test_ruled_out_chain_incomplete(self):
        """Only one RULED_OUT present — R3 does NOT fire."""
        r1 = _rule(
            "R1",
            _cond(("CPU", "OK")),
            then=RuleOutput(kind="RULED_OUT", description="CPU ruled out"),
        )
        r3_cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="RULED_OUT", instance="*", property="CPU ruled out",
                     operator="==", value="true"),
                Fact(noun="RULED_OUT", instance="*", property="Memory ruled out",
                     operator="==", value="true"),
            ],
        )
        r3 = _rule(
            "R3",
            r3_cond,
            then=RuleOutput(kind="CHANGE_STATE", description="Look at network"),
        )

        facts = [_fact("CPU", "OK")]
        result = RuleEvaluator([r1, r3]).evaluate(facts)

        fired_ids = {r.rule_id for r in result.fired_rules}
        assert "R1" in fired_ids
        assert "R3" not in fired_ids


# ============================================================================
# TC7: Chaining CHANGE_STATE
# ============================================================================

class TestChainingChangeState:
    def test_change_state_chains(self):
        """CHANGE_STATE from R1 satisfies R2's condition."""
        r1 = _rule(
            "R1",
            _cond(("Service", "Degraded")),
            then=RuleOutput(kind="CHANGE_STATE", description="Escalate to L2"),
        )
        r2_cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="CHANGE_STATE", instance="*", property="Escalate to L2",
                     operator="==", value="true"),
            ],
        )
        r2 = _rule(
            "R2",
            r2_cond,
            then=RuleOutput(kind="CHANGE_STATE", description="Notify manager"),
        )

        facts = [_fact("Service", "Degraded")]
        result = RuleEvaluator([r1, r2]).evaluate(facts)

        assert len(result.fired_rules) == 2
        assert "Notify manager" in result.change_states


# ============================================================================
# TC8: GAP Terminal
# ============================================================================

class TestGapTerminal:
    def test_gap_not_in_working_set(self):
        """GAP output is recorded but does NOT chain to downstream rules."""
        r1 = _rule(
            "R1",
            _cond(("Disk", "Unknown")),
            then=RuleOutput(kind="GAP", description="Need disk metrics"),
        )
        r2_cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="GAP", instance="*", property="description",
                     operator="==", value="Need disk metrics"),
            ],
        )
        r2 = _rule(
            "R2",
            r2_cond,
            then=RuleOutput(kind="CHANGE_STATE", description="Should not fire"),
        )

        facts = [_fact("Disk", "Unknown")]
        result = RuleEvaluator([r1, r2]).evaluate(facts)

        # R1 fires (GAP), R2 should NOT fire
        fired_ids = {r.rule_id for r in result.fired_rules}
        assert "R1" in fired_ids
        assert "R2" not in fired_ids
        assert result.gaps == ["Need disk metrics"]
        assert not any(f.noun == "GAP" for f in result.derived_facts)


# ============================================================================
# TC9: Rule Trace
# ============================================================================

class TestRuleTrace:
    def test_trace_records_branch(self):
        """Each trace entry includes which branch fired."""
        r1 = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="y"),
        )
        r2 = _rule(
            "R2",
            _cond(("Memory", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="m"),
            else_=RuleOutput(kind="RULED_OUT", description="n"),
        )
        # CPU high → R1 THEN fires; Memory not present → R2 ELSE fires
        facts = [_fact("CPU", "High")]
        result = RuleEvaluator([r1, r2]).evaluate(facts)

        trace_by_id = {t["rule_id"]: t for t in result.rule_trace}
        assert trace_by_id["R1"]["branch"] == "then"
        assert trace_by_id["R2"]["branch"] == "else"

    def test_trace_iteration_and_derived(self):
        """Trace includes iteration count and derived description."""
        r = _rule(
            "R1",
            _cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="state X"),
        )
        facts = [_fact("A", "1")]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.rule_trace) == 1
        assert result.rule_trace[0]["iteration"] == 1
        assert "CHANGE_STATE" in result.rule_trace[0]["derived"]


# ============================================================================
# Condition matching — AND / OR
# ============================================================================

class TestConditionLogic:
    def test_and_conditions_all_met(self):
        r = _rule(
            "R1",
            _cond(("A", "1"), ("B", "2")),
            then=RuleOutput(kind="CHANGE_STATE", description="both"),
        )
        facts = [_fact("A", "1"), _fact("B", "2")]
        result = RuleEvaluator([r]).evaluate(facts)
        assert len(result.fired_rules) == 1

    def test_and_conditions_partial(self):
        r = _rule(
            "R1",
            _cond(("A", "1"), ("B", "2")),
            then=RuleOutput(kind="CHANGE_STATE", description="both"),
        )
        facts = [_fact("A", "1")]
        result = RuleEvaluator([r]).evaluate(facts)
        assert len(result.fired_rules) == 0

    def test_or_conditions_one_met(self):
        r = _rule(
            "R1",
            _cond(("A", "1"), ("B", "2"), logic="OR"),
            then=RuleOutput(kind="CHANGE_STATE", description="either"),
        )
        facts = [_fact("B", "2")]
        result = RuleEvaluator([r]).evaluate(facts)
        assert len(result.fired_rules) == 1

    def test_or_conditions_none_met(self):
        r = _rule(
            "R1",
            _cond(("A", "1"), ("B", "2"), logic="OR"),
            then=RuleOutput(kind="CHANGE_STATE", description="either"),
        )
        facts = [_fact("C", "3")]
        result = RuleEvaluator([r]).evaluate(facts)
        assert len(result.fired_rules) == 0


# ============================================================================
# Variable binding
# ============================================================================

class TestVariableBinding:
    def test_variable_conditions_then_fires(self):
        """Variable binding works with v2 THEN output."""
        cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="Server", instance="$host", property="CPU",
                     operator="==", value="High"),
            ],
        )
        r = _rule(
            "R1",
            cond,
            then=RuleOutput(kind="CHANGE_STATE", description="High CPU on server"),
        )
        facts = [
            Fact(noun="Server", instance="web01", property="CPU",
                 operator="==", value="High"),
        ]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 1
        assert result.outputs[0]["output"].kind == "CHANGE_STATE"

    def test_variable_conditions_else_fires(self):
        """Variable binding: conditions not met → ELSE fires."""
        cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="Server", instance="$host", property="CPU",
                     operator="==", value="High"),
            ],
        )
        r = _rule(
            "R1",
            cond,
            then=RuleOutput(kind="CHANGE_STATE", description="CPU problem"),
            else_=RuleOutput(kind="RULED_OUT", description="CPU fine"),
        )
        facts = [
            Fact(noun="Server", instance="web01", property="CPU",
                 operator="==", value="Low"),
        ]
        result = RuleEvaluator([r]).evaluate(facts)

        assert len(result.fired_rules) == 1
        assert result.outputs[0]["branch"] == "else"


# ============================================================================
# Only CONFIRMED rules fire
# ============================================================================

class TestStatusFiltering:
    def test_gap_status_rule_skipped(self):
        """Rules with status=GAP are not evaluated."""
        r = _rule(
            "R1",
            _cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            status="GAP",
        )
        facts = [_fact("A", "1")]
        result = RuleEvaluator([r]).evaluate(facts)
        assert len(result.fired_rules) == 0

    def test_resolved_status_rule_skipped(self):
        r = _rule(
            "R1",
            _cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            status="RESOLVED",
        )
        facts = [_fact("A", "1")]
        result = RuleEvaluator([r]).evaluate(facts)
        assert len(result.fired_rules) == 0


# ============================================================================
# Empty inputs
# ============================================================================

class TestEdgeCases:
    def test_no_rules(self):
        result = RuleEvaluator([]).evaluate([_fact("A", "1")])
        assert result.fired_rules == []
        assert result.outputs == []

    def test_no_facts(self):
        r = _rule(
            "R1",
            _cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        result = RuleEvaluator([r]).evaluate([])
        assert result.fired_rules == []

    def test_empty_both(self):
        result = RuleEvaluator([]).evaluate([])
        assert result.fired_rules == []

    def test_result_input_facts_preserved(self):
        facts = [_fact("A", "1")]
        result = RuleEvaluator([]).evaluate(facts)
        assert result.input_facts == facts

    def test_multiple_rules_fire_order(self):
        """Multiple rules fire in list order."""
        r1 = _rule("R1", _cond(("A", "1")),
                    then=RuleOutput(kind="CHANGE_STATE", description="first"))
        r2 = _rule("R2", _cond(("B", "2")),
                    then=RuleOutput(kind="RULED_OUT", description="second"))
        facts = [_fact("A", "1"), _fact("B", "2")]
        result = RuleEvaluator([r1, r2]).evaluate(facts)

        assert [r.rule_id for r in result.fired_rules] == ["R1", "R2"]

    def test_else_fires_with_no_input_facts(self):
        """ELSE fires when there are no input facts at all (conditions can't be met)."""
        r = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="CPU not checked"),
        )
        result = RuleEvaluator([r]).evaluate([])
        assert len(result.fired_rules) == 1
        assert result.outputs[0]["branch"] == "else"
