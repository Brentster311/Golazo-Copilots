"""Tests for rule_evaluator.py — forward chaining rule evaluation engine."""
import pytest

from ees.models import (
    EvaluationResult,
    Fact,
    Rule,
    RuleConditions,
    RuleThen,
)
from ees.rule_evaluator import RuleEvaluator


# ── Helper factories ──────────────────────────────────────────

def _fact(text: str) -> Fact:
    """Parse a fact string, assert valid."""
    f = Fact.parse(text)
    assert f is not None, f"Invalid fact: {text}"
    return f


def _rule(rule_id: str, conditions: list[Fact], then: RuleThen,
          because: str = "test", logic: str = "AND",
          rule_type: str = "positive", status: str = "CONFIRMED") -> Rule:
    """Build a rule with given conditions and then clause."""
    return Rule(
        rule_id=rule_id,
        status=status,
        type=rule_type,
        conditions=RuleConditions(logic=logic, items=conditions),
        then=then,
        because=because,
    )


# ── AC-1: Evaluates rules and reports matching root causes ────

class TestBasicEvaluation:
    """AC-1: Evaluates rules and reports matching root causes."""

    def test_single_rule_fires(self):
        """TC-1: Single rule fires and identifies root cause."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert "HighCPU" in result.root_causes
        assert len(result.fired_rules) == 1
        assert result.fired_rules[0].rule_id == "R-001"

    def test_no_rules_fire(self):
        """TC-2: No matching conditions — empty result."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).MemoryFree < 5%")])

        assert result.root_causes == []
        assert result.fired_rules == []

    def test_multiple_root_causes(self):
        """TC-3: Multiple root causes identified from same facts."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
            _rule("R-002",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "RunawayProcess")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert "HighCPU" in result.root_causes
        assert "RunawayProcess" in result.root_causes
        assert len(result.fired_rules) == 2


# ── AC-2: Reports RULEOUT rules and eliminated root causes ────

class TestRuleoutEvaluation:
    """AC-2: Reports RULEOUT rules and eliminated root causes."""

    def test_ruleout_fires(self):
        """TC-4: RULEOUT rule fires and reports eliminated root cause."""
        rules = [
            _rule("R-001",
                  [_fact("Network(*).Latency == normal")],
                  RuleThen("RULEOUT", "*", "Target", "NetworkIssue"),
                  rule_type="ruleout"),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Network(*).Latency == normal")])

        assert "NetworkIssue" in result.ruled_out
        assert len(result.fired_rules) == 1

    def test_positive_and_ruleout_both_fire(self):
        """TC-5: Both positive and RULEOUT rules fire."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
            _rule("R-002",
                  [_fact("Network(*).Latency == normal")],
                  RuleThen("RULEOUT", "*", "Target", "NetworkIssue"),
                  rule_type="ruleout"),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([
            _fact("Server(*).CPUUsage > 90"),
            _fact("Network(*).Latency == normal"),
        ])

        assert "HighCPU" in result.root_causes
        assert "NetworkIssue" in result.ruled_out


# ── AC-3: Reports encountered GAP rules ──────────────────────

class TestGapDetection:
    """AC-3: Reports encountered GAP rules."""

    def test_gap_rule_fully_met(self):
        """TC-6: GAP rule whose requires are all in working set is reported."""
        gap_rule = Rule(
            rule_id="R-GAP-001",
            status="GAP",
            requires=[_fact("Server(*).CPUUsage > 90")],
            produces=[_fact("Server(*).Diagnosis == unknown")],
            note="Missing link",
        )
        rules = [gap_rule]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert len(result.gap_rules) == 1
        assert result.gap_rules[0].rule_id == "R-GAP-001"

    def test_gap_rule_partially_met(self):
        """TC-7: GAP rule with only partial match is NOT reported."""
        gap_rule = Rule(
            rule_id="R-GAP-001",
            status="GAP",
            requires=[
                _fact("Server(*).CPUUsage > 90"),
                _fact("Server(*).MemoryFree < 5%"),
            ],
            produces=[_fact("Server(*).Diagnosis == unknown")],
            note="Missing link",
        )
        rules = [gap_rule]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert result.gap_rules == []


# ── AC-4: Full rule chain trace ──────────────────────────────

class TestRuleTrace:
    """AC-4: Full rule chain trace (traceability)."""

    def test_chain_trace_order(self):
        """TC-8: Two-rule chain produces trace with 2 entries in order."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("Server", "*", "State", "overloaded")),
            _rule("R-002",
                  [_fact("Server(*).State == overloaded")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert len(result.rule_trace) == 2
        assert result.rule_trace[0]["rule_id"] == "R-001"
        assert result.rule_trace[1]["rule_id"] == "R-002"

    def test_trace_entry_structure(self):
        """TC-9: Each trace entry contains rule_id and derived fact."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        entry = result.rule_trace[0]
        assert "rule_id" in entry
        assert "derived" in entry
        assert entry["rule_id"] == "R-001"


# ── AC-5: Rules evaluated in dependency order (chaining) ──────

class TestChaining:
    """AC-5: Forward chaining with dependent rules."""

    def test_two_level_chain(self):
        """TC-10: Chain depth 2 — derived fact triggers second rule."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("Server", "*", "State", "overloaded")),
            _rule("R-002",
                  [_fact("Server(*).State == overloaded")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert "HighCPU" in result.root_causes
        assert len(result.fired_rules) == 2

    def test_three_level_chain(self):
        """TC-11: Chain depth 3 — A→B→C→RootCause."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("Server", "*", "State", "overloaded")),
            _rule("R-002",
                  [_fact("Server(*).State == overloaded")],
                  RuleThen("Server", "*", "Alert", "critical")),
            _rule("R-003",
                  [_fact("Server(*).Alert == critical")],
                  RuleThen("RootCause", "*", "Name", "CriticalOverload")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert "CriticalOverload" in result.root_causes
        assert len(result.fired_rules) == 3

    def test_convergence_skips_inapplicable_rules(self):
        """TC-12: Rules that can't fire are skipped."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
            _rule("R-002",
                  [_fact("Network(*).Latency > 100")],
                  RuleThen("RootCause", "*", "Name", "NetworkSlow")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert "HighCPU" in result.root_causes
        assert "NetworkSlow" not in result.root_causes
        assert len(result.fired_rules) == 1


# ── AC-6: Conflicting root causes presented as candidates ────

class TestConflicts:
    """AC-6: Conflicting root causes all presented."""

    def test_conflicting_root_causes(self):
        """TC-13: Same facts lead to different root causes — both reported."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
            _rule("R-002",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "MiningMalware")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert len(result.root_causes) == 2
        assert set(result.root_causes) == {"HighCPU", "MiningMalware"}


# ── AC-7: Structured output ──────────────────────────────────

class TestStructuredOutput:
    """AC-7: EvaluationResult.to_dict() serialization."""

    def test_to_dict_keys(self):
        """TC-14: to_dict contains all expected keys."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])
        d = result.to_dict()

        expected_keys = {
            "input_facts", "derived_facts", "fired_rules",
            "root_causes", "ruled_out", "gap_rules", "rule_trace",
        }
        assert set(d.keys()) == expected_keys


# ── Edge cases ────────────────────────────────────────────────

class TestEdgeCases:
    """Cross-cutting: Edge cases."""

    def test_empty_input_facts(self):
        """TC-20: Empty input facts — no rules fire."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([])

        assert result.root_causes == []
        assert result.fired_rules == []
        assert result.derived_facts == []

    def test_or_logic_fires(self):
        """TC-21: OR logic rule fires when any condition matches."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90"),
                   _fact("Server(*).MemoryFree < 5%")],
                  RuleThen("RootCause", "*", "Name", "ResourceExhaustion"),
                  logic="OR"),
        ]
        evaluator = RuleEvaluator(rules)
        # Only one condition matches — should fire with OR logic
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert "ResourceExhaustion" in result.root_causes
        assert len(result.fired_rules) == 1

    def test_derived_fact_chains(self):
        """TC-22: Derived fact from one rule matches condition of another."""
        rules = [
            _rule("R-001",
                  [_fact("App(*).ErrorRate > 50")],
                  RuleThen("App", "*", "Health", "degraded")),
            _rule("R-002",
                  [_fact("App(*).Health == degraded")],
                  RuleThen("RootCause", "*", "Name", "AppFailure")),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("App(*).ErrorRate > 50")])

        assert "AppFailure" in result.root_causes
        assert len(result.derived_facts) == 2  # Health=degraded + RootCause

    def test_only_confirmed_rules_evaluated(self):
        """Only CONFIRMED rules are evaluated — GAP and RESOLVED are skipped."""
        rules = [
            _rule("R-001",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "HighCPU"),
                  status="CONFIRMED"),
            _rule("R-002",
                  [_fact("Server(*).CPUUsage > 90")],
                  RuleThen("RootCause", "*", "Name", "OldRC"),
                  status="RESOLVED"),
        ]
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert result.root_causes == ["HighCPU"]
        assert len(result.fired_rules) == 1

    def test_no_rules_at_all(self):
        """Empty rule set — evaluation returns empty result."""
        evaluator = RuleEvaluator([])
        result = evaluator.evaluate([_fact("Server(*).CPUUsage > 90")])

        assert result.root_causes == []
        assert result.fired_rules == []
        assert result.gap_rules == []
