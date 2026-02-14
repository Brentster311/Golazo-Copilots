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


class TestVariableBinding:
    """TC-3 through TC-14: Variable binding in rule evaluation."""

    def test_single_instance_variable_binds(self):
        """TC-3: Error($op).ResultCode == X matches Error(op-1).ResultCode == X."""
        rule = Rule(
            rule_id="R-VAR-1",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
            ]),
            then=RuleThen("RootCause", "$op", "Name", "Zonal capacity"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "ResultCode", "==", "ZonalAllocationFailed"),
        ])
        assert len(result.fired_rules) == 1
        # Derived fact should have $op substituted with op-1
        assert any(f.instance == "op-1" for f in result.derived_facts)

    def test_single_value_variable_binds(self):
        """TC-4: VMSeries(*).Name == $vmsize matches VMSeries(*).Name == NvadsA10v5."""
        rule = Rule(
            rule_id="R-VAR-2",
            conditions=RuleConditions("AND", [
                Fact("VMSeries", "*", "Name", "==", "$vmsize"),
            ]),
            then=RuleThen("Troubleshooting", "*", "VMSize", "$vmsize"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("VMSeries", "*", "Name", "==", "NvadsA10v5"),
        ])
        assert len(result.fired_rules) == 1
        assert any(f.value == "NvadsA10v5" for f in result.derived_facts)

    def test_shared_variable_and_consistent(self):
        """TC-5: Two conditions with same $op — consistent binding fires."""
        rule = Rule(
            rule_id="R-VAR-3",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
                Fact("VMSeries", "$op", "Name", "==", "NvadsA10v5"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "Zonal capacity"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "ResultCode", "==", "ZonalAllocationFailed"),
            Fact("VMSeries", "op-1", "Name", "==", "NvadsA10v5"),
        ])
        assert len(result.fired_rules) == 1

    def test_shared_variable_and_inconsistent_no_fire(self):
        """TC-6: Two conditions with same $op — inconsistent binding does NOT fire."""
        rule = Rule(
            rule_id="R-VAR-4",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
                Fact("VMSeries", "$op", "Name", "==", "NvadsA10v5"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "Zonal capacity"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "ResultCode", "==", "ZonalAllocationFailed"),
            Fact("VMSeries", "op-2", "Name", "==", "NvadsA10v5"),
        ])
        assert len(result.fired_rules) == 0

    def test_shared_variable_backtracking(self):
        """TC-7: Multiple candidates — correct one found via backtracking."""
        rule = Rule(
            rule_id="R-VAR-5",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
                Fact("VMSeries", "$op", "Name", "==", "NvadsA10v5"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "Zonal capacity"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "ResultCode", "==", "OK"),
            Fact("Error", "op-2", "ResultCode", "==", "ZonalAllocationFailed"),
            Fact("VMSeries", "op-2", "Name", "==", "NvadsA10v5"),
        ])
        assert len(result.fired_rules) == 1

    def test_then_instance_substitution(self):
        """TC-8: Variable in then.instance is substituted."""
        rule = Rule(
            rule_id="R-VAR-6",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
            ]),
            then=RuleThen("RootCause", "$op", "Name", "Zonal capacity"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "ResultCode", "==", "ZonalAllocationFailed"),
        ])
        derived = [f for f in result.derived_facts if f.noun == "RootCause"]
        assert len(derived) == 1
        assert derived[0].instance == "op-1"

    def test_then_value_substitution_whole(self):
        """TC-9: If then.value is exactly '$vmsize', substitute it."""
        rule = Rule(
            rule_id="R-VAR-7",
            conditions=RuleConditions("AND", [
                Fact("VMSeries", "*", "Name", "==", "$vmsize"),
            ]),
            then=RuleThen("Troubleshooting", "*", "VMSize", "$vmsize"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("VMSeries", "*", "Name", "==", "NvadsA10v5"),
        ])
        derived = [f for f in result.derived_facts if f.noun == "Troubleshooting"]
        assert len(derived) == 1
        assert derived[0].value == "NvadsA10v5"

    def test_then_value_embedded_not_substituted(self):
        """TC-9 clarification: Embedded $var in value is NOT substituted."""
        rule = Rule(
            rule_id="R-VAR-8",
            conditions=RuleConditions("AND", [
                Fact("VMSeries", "*", "Name", "==", "$vmsize"),
            ]),
            then=RuleThen("Troubleshooting", "*", "Info", "Capacity for $vmsize"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("VMSeries", "*", "Name", "==", "NvadsA10v5"),
        ])
        derived = [f for f in result.derived_facts if f.noun == "Troubleshooting"]
        assert len(derived) == 1
        # Embedded variable — left as-is
        assert derived[0].value == "Capacity for $vmsize"

    def test_no_variable_rules_unchanged(self):
        """TC-10: Non-variable rules still work via fast path."""
        rule = Rule(
            rule_id="R-NOVAR",
            conditions=RuleConditions("AND", [
                Fact("Error", "*", "ResultCode", "==", "ZonalAllocationFailed"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "Zonal capacity"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "*", "ResultCode", "==", "ZonalAllocationFailed"),
        ])
        assert len(result.fired_rules) == 1

    def test_or_logic_with_variables(self):
        """TC-11: OR logic — any condition with variable can match."""
        rule = Rule(
            rule_id="R-VAR-OR",
            conditions=RuleConditions("OR", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
                Fact("Error", "$op", "ResultCode", "==", "AllocationFailed"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "Allocation failure"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "ResultCode", "==", "AllocationFailed"),
        ])
        assert len(result.fired_rules) == 1

    def test_multiple_different_variables(self):
        """TC-12: Two different variables bind independently."""
        rule = Rule(
            rule_id="R-VAR-MULTI",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
                Fact("VMSeries", "$op", "Name", "==", "$vmsize"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "Zonal capacity"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "ResultCode", "==", "ZonalAllocationFailed"),
            Fact("VMSeries", "op-1", "Name", "==", "NvadsA10v5"),
        ])
        assert len(result.fired_rules) == 1

    def test_variable_with_contains_operator(self):
        """TC-13: Variable binding works with contains operator."""
        rule = Rule(
            rule_id="R-VAR-CONTAINS",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "Message", "contains", "insufficient capacity"),
            ]),
            then=RuleThen("RootCause", "*", "Name", "Capacity issue"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        result = evaluator.evaluate([
            Fact("Error", "op-1", "Message", "contains", "No compute stamps available"),
            Fact("Error", "op-2", "Message", "contains", "insufficient capacity"),
        ])
        assert len(result.fired_rules) == 1

    def test_full_evaluate_variable_rule_derived_fact(self):
        """TC-14: Full integration — variable rule fires and produces derived fact."""
        rule = Rule(
            rule_id="R-VAR-INT",
            conditions=RuleConditions("AND", [
                Fact("Error", "$op", "ResultCode", "==", "ZonalAllocationFailed"),
                Fact("Error", "$op", "Message", "contains", "insufficient capacity"),
            ]),
            then=RuleThen("RootCause", "$op", "Name", "Zonal capacity exhaustion"),
            because="test",
        )
        evaluator = RuleEvaluator([rule])
        facts = [
            Fact("Error", "op-1", "ResultCode", "==", "ZonalAllocationFailed"),
            Fact("Error", "op-1", "Message", "contains", "insufficient capacity"),
        ]
        result = evaluator.evaluate(facts)
        assert "Zonal capacity exhaustion" in result.root_causes
        assert any(
            f.noun == "RootCause" and f.instance == "op-1" and f.value == "Zonal capacity exhaustion"
            for f in result.derived_facts
        )
