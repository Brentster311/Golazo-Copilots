"""Tests for GUI adapter functions — model-to-display conversions.

These are pure Python functions, testable without Tkinter.
"""
import pytest

from ees.models import (
    EvaluationResult,
    Fact,
    OntologyNoun,
    OntologyProperty,
    Rule,
    RuleConditions,
    RuleThen,
)
from ees.gui.adapters import (
    facts_to_rows,
    rules_to_rows,
    ontology_to_tree,
    eval_result_to_display,
    filter_rules,
)


# ── Helper factories ──────────────────────────────────────────

def _fact(text: str) -> Fact:
    f = Fact.parse(text)
    assert f is not None
    return f


def _rule(rule_id: str, conditions: list[Fact], then: RuleThen,
          because: str = "test", logic: str = "AND",
          rule_type: str = "positive", status: str = "CONFIRMED") -> Rule:
    return Rule(
        rule_id=rule_id,
        status=status,
        type=rule_type,
        conditions=RuleConditions(logic=logic, items=conditions),
        then=then,
        because=because,
    )


# ── AC-2: facts_to_rows ──────────────────────────────────────

class TestFactsToRows:
    """TC-4/5/6: Fact-to-display row conversion."""

    def test_facts_to_rows_basic(self):
        """TC-4: Facts displayed with correct columns."""
        facts = [_fact("Server(*).CPUUsage > 90")]
        rows = facts_to_rows(facts)
        assert len(rows) == 1
        row = rows[0]
        assert row["noun"] == "Server"
        assert row["instance"] == "*"
        assert row["property"] == "CPUUsage"
        assert row["operator"] == ">"
        assert row["value"] == "90"

    def test_facts_to_rows_confirmed_status(self):
        """TC-5: Confirmed fact has status 'confirmed'."""
        fact = _fact("Server(*).CPUUsage > 90")
        fact.status = "confirmed"
        rows = facts_to_rows([fact])
        assert rows[0]["status"] == "confirmed"

    def test_facts_to_rows_rejected_status(self):
        """TC-6: Rejected fact has status 'rejected'."""
        fact = _fact("Server(*).CPUUsage > 90")
        fact.status = "rejected"
        rows = facts_to_rows([fact])
        assert rows[0]["status"] == "rejected"

    def test_facts_to_rows_empty(self):
        """Empty facts list returns empty rows."""
        assert facts_to_rows([]) == []


# ── AC-3: rules_to_rows ──────────────────────────────────────

class TestRulesToRows:
    """TC-8/9: Rule-to-display row conversion."""

    def test_rules_to_rows_basic(self):
        """TC-8: Rules displayed with IF/THEN/BECAUSE."""
        rules = [_rule("R-001",
                       [_fact("Server(*).CPUUsage > 90")],
                       RuleThen("RootCause", "*", "Name", "HighCPU"),
                       because="High CPU causes overload")]
        rows = rules_to_rows(rules)
        assert len(rows) == 1
        row = rows[0]
        assert row["rule_id"] == "R-001"
        assert "CPUUsage" in row["conditions"]
        assert "HighCPU" in row["then"]
        assert row["because"] == "High CPU causes overload"

    def test_rules_to_rows_ruleout(self):
        """TC-9: RULEOUT rules show type distinction."""
        rules = [_rule("R-002",
                       [_fact("Network(*).Latency == normal")],
                       RuleThen("RULEOUT", "*", "Target", "NetworkIssue"),
                       rule_type="ruleout")]
        rows = rules_to_rows(rules)
        assert rows[0]["type"] == "ruleout"

    def test_rules_to_rows_empty(self):
        """Empty rules list returns empty rows."""
        assert rules_to_rows([]) == []


# ── AC-4: ontology_to_tree ───────────────────────────────────

class TestOntologyToTree:
    """TC-10/11: Ontology-to-tree conversion."""

    def test_ontology_to_tree_basic(self):
        """TC-10: Ontology shows nouns with properties."""
        nouns = [
            OntologyNoun("Server", [
                OntologyProperty("CPUUsage", "number"),
                OntologyProperty("MemoryFree", "number"),
            ]),
        ]
        tree = ontology_to_tree(nouns)
        assert len(tree) == 1
        assert tree[0]["noun"] == "Server"
        assert len(tree[0]["properties"]) == 2
        assert tree[0]["properties"][0]["name"] == "CPUUsage"

    def test_ontology_to_tree_empty(self):
        """TC-11: Empty ontology returns empty tree."""
        assert ontology_to_tree([]) == []


# ── AC-5: filter_rules ───────────────────────────────────────

class TestFilterRules:
    """TC-12/13/14: Rule filtering."""

    def test_filter_all_rules(self):
        """TC-12: No filter returns all rules."""
        rules = [
            _rule("R-001", [_fact("S(*).P == v")],
                  RuleThen("RootCause", "*", "Name", "X")),
            _rule("R-002", [_fact("S(*).P == v")],
                  RuleThen("RootCause", "*", "Name", "Y"), status="GAP"),
        ]
        assert len(filter_rules(rules)) == 2

    def test_filter_by_status_gap(self):
        """TC-13: Filter by status=GAP returns only GAP rules."""
        rules = [
            _rule("R-001", [_fact("S(*).P == v")],
                  RuleThen("RootCause", "*", "Name", "X")),
            _rule("R-002", [_fact("S(*).P == v")],
                  RuleThen("RootCause", "*", "Name", "Y"), status="GAP"),
        ]
        result = filter_rules(rules, status="GAP")
        assert len(result) == 1
        assert result[0].rule_id == "R-002"

    def test_filter_by_type_ruleout(self):
        """TC-14: Filter by type=ruleout returns only RULEOUT rules."""
        rules = [
            _rule("R-001", [_fact("S(*).P == v")],
                  RuleThen("RootCause", "*", "Name", "X")),
            _rule("R-002", [_fact("N(*).L == normal")],
                  RuleThen("RULEOUT", "*", "Target", "Net"),
                  rule_type="ruleout"),
        ]
        result = filter_rules(rules, rule_type="ruleout")
        assert len(result) == 1
        assert result[0].rule_id == "R-002"


# ── AC-6: eval_result_to_display ─────────────────────────────

class TestEvalResultToDisplay:
    """TC-16/17/18/19: Evaluation result display conversion."""

    def _make_result(self, root_causes=None, ruled_out=None, gap_rules=None):
        return EvaluationResult(
            input_facts=[_fact("Server(*).CPUUsage > 90")],
            derived_facts=[],
            fired_rules=[],
            root_causes=root_causes or [],
            ruled_out=ruled_out or [],
            gap_rules=gap_rules or [],
            rule_trace=[],
        )

    def test_display_root_causes(self):
        """TC-16: Root causes shown in display dict."""
        result = self._make_result(root_causes=["HighCPU"])
        display = eval_result_to_display(result)
        assert "HighCPU" in display["root_causes"]

    def test_display_ruled_out(self):
        """TC-17: Ruled-out causes shown in display dict."""
        result = self._make_result(ruled_out=["NetworkIssue"])
        display = eval_result_to_display(result)
        assert "NetworkIssue" in display["ruled_out"]

    def test_display_gap_rules(self):
        """TC-18: GAP rules listed in display dict."""
        gap = Rule(rule_id="R-GAP-001", status="GAP",
                   requires=[_fact("S(*).P == v")],
                   produces=[_fact("S(*).D == unknown")],
                   note="Missing")
        result = self._make_result(gap_rules=[gap])
        display = eval_result_to_display(result)
        assert len(display["gap_rules"]) == 1

    def test_display_empty_results(self):
        """TC-19: Empty results displayed without crash."""
        result = self._make_result()
        display = eval_result_to_display(result)
        assert display["root_causes"] == []
        assert display["ruled_out"] == []
        assert display["gap_rules"] == []
        assert display["fired_rules"] == []


# ── Worker tests ──────────────────────────────────────────────

class TestWorkerErrorHandling:
    """TC-23/24: Worker thread error handling and result delivery."""

    def test_worker_error_callback(self):
        """TC-23: Worker calls on_error callback on exception."""
        from ees.gui.workers import run_in_worker
        errors = []

        def failing_func():
            raise RuntimeError("LLM failed")

        run_in_worker(failing_func, on_complete=lambda r: None,
                      on_error=lambda e: errors.append(e))

        # Wait for worker to finish
        import time
        time.sleep(0.2)
        assert len(errors) == 1
        assert "LLM failed" in str(errors[0])

    def test_worker_success_callback(self):
        """TC-24: Worker calls on_complete callback on success."""
        from ees.gui.workers import run_in_worker
        results = []

        def success_func():
            return "done"

        run_in_worker(success_func, on_complete=lambda r: results.append(r),
                      on_error=lambda e: None)

        import time
        time.sleep(0.2)
        assert results == ["done"]
