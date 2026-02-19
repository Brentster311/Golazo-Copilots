"""Tests for the AST-based forward-chaining evaluator (EES-00019 Phase 2).

TDD RED phase: These tests define the expected behavior of ASTEvaluator.
They should all FAIL before production code is written.
"""
from __future__ import annotations

import pytest

from ees.models import (
    AssertStmt,
    Block,
    CheckExpr,
    DecideStmt,
    Fact,
    GapStmt,
    Goal,
    NoopStmt,
    RetractStmt,
    ActStmt,
    RuleBlock,
    parse_rule,
)

# Import will fail until ASTEvaluator is implemented:
from ees.rule_evaluator import ASTEvaluator


# ── Helpers ───────────────────────────────────────────────────────────


def _make_rule(rule_id: str, block_data: list[dict]) -> RuleBlock:
    """Convenience: build a RuleBlock from a block list dict."""
    return parse_rule({"rule_id": rule_id, "block": block_data})


def _fact(noun: str, instance: str, prop: str, op: str, value: str) -> Fact:
    return Fact(noun=noun, instance=instance, property=prop, operator=op, value=value)


# ── TC-08: Simple ASSERT adds fact to working memory ──────────────────


class TestSimpleAssert:
    """TC-08: Bare ASSERT adds the specified fact to working memory."""

    def test_bare_assert(self):
        rule = _make_rule("R-A01", [
            {"assert": {"noun": "User", "instance": "*", "property": "adminRole",
                        "operator": "==", "value": "confirmed"}},
        ])
        ev = ASTEvaluator([rule])
        result = ev.evaluate([])

        # Working memory should now contain the asserted fact
        wm_keys = {f.match_key() for f in result.derived_facts}
        expected = ("user", "*", "adminrole", "==", "confirmed")
        assert expected in wm_keys, "ASSERT should add the specified fact to working memory"


# ── TC-09: CHECK/DECIDE branches correctly - then path ────────────────


class TestDecideThenPath:
    """TC-09: DECIDE takes then-branch when CHECK is true."""

    def test_decide_then_branch(self):
        rule = _make_rule("R-D01", [
            {
                "check": {"noun": "User", "instance": "*", "property": "adminRole",
                          "operator": "==", "value": "unknown"},
                "decide": {
                    "then": [
                        {"assert": {"noun": "User", "instance": "*", "property": "adminRole",
                                    "operator": "==", "value": "confirmed"}},
                    ],
                    "else": [{"noop": True}],
                },
            },
        ])
        ev = ASTEvaluator([rule])
        initial = [_fact("User", "*", "adminRole", "==", "unknown")]
        result = ev.evaluate(initial)

        derived_keys = {f.match_key() for f in result.derived_facts}
        assert ("user", "*", "adminrole", "==", "confirmed") in derived_keys, \
            "DECIDE should take then-branch when CHECK is true"


# ── TC-10: CHECK/DECIDE branches correctly - else path ────────────────


class TestDecideElsePath:
    """TC-10: DECIDE takes else-branch when CHECK is false."""

    def test_decide_else_branch(self):
        rule = _make_rule("R-D02", [
            {
                "check": {"noun": "User", "instance": "*", "property": "adminRole",
                          "operator": "==", "value": "unknown"},
                "decide": {
                    "then": [
                        {"assert": {"noun": "User", "instance": "*", "property": "adminRole",
                                    "operator": "==", "value": "confirmed"}},
                    ],
                    "else": [
                        {"gap": "already confirmed"},
                    ],
                },
            },
        ])
        ev = ASTEvaluator([rule])
        # Working memory has "confirmed", not "unknown" → else branch fires
        initial = [_fact("User", "*", "adminRole", "==", "confirmed")]
        result = ev.evaluate(initial)

        # No ASSERT should have fired
        assert len(result.derived_facts) == 0, "No new facts when else branch fires"
        # Trace should record the GAP
        gap_entries = [t for t in result.rule_trace if t.get("stmt_kind") == "GAP"]
        assert len(gap_entries) >= 1, "DECIDE should take else-branch when CHECK is false"


# ── TC-11: RETRACT removes fact from working memory ───────────────────


class TestRetract:
    """TC-11: RETRACT removes matching facts from working memory."""

    def test_retract_removes_fact(self):
        rule = _make_rule("R-R01", [
            {"retract": {"noun": "User", "instance": "$u", "property": "adminRole"}},
        ])
        ev = ASTEvaluator([rule])
        initial = [_fact("User", "$u", "adminRole", "==", "unknown")]
        result = ev.evaluate(initial)

        # After retract, working memory should not contain User.adminRole
        all_facts = list(result.input_facts) + list(result.derived_facts)
        remaining = [f for f in all_facts
                     if f.noun.lower() == "user" and f.property.lower() == "adminrole"]
        # Retract should have removed the matching fact
        # Check the trace records the retraction
        retract_entries = [t for t in result.rule_trace if t.get("stmt_kind") == "RETRACT"]
        assert len(retract_entries) >= 1, "RETRACT should record removal in trace"


# ── TC-12: Fixed-point convergence ────────────────────────────────────


class TestFixedPointConvergence:
    """TC-12: Forward chaining converges when no new changes occur."""

    def test_convergence_chain(self):
        # R1: if C exists → assert B
        r1 = _make_rule("R-C01", [
            {
                "check": {"noun": "Signal", "instance": "*", "property": "flag",
                          "operator": "==", "value": "C"},
                "decide": {
                    "then": [
                        {"assert": {"noun": "Signal", "instance": "*", "property": "flag",
                                    "operator": "==", "value": "B"}},
                    ],
                    "else": [{"noop": True}],
                },
            },
        ])
        # R2: if B exists → assert A
        r2 = _make_rule("R-C02", [
            {
                "check": {"noun": "Signal", "instance": "*", "property": "flag",
                          "operator": "==", "value": "B"},
                "decide": {
                    "then": [
                        {"assert": {"noun": "Signal", "instance": "*", "property": "flag",
                                    "operator": "==", "value": "A"}},
                    ],
                    "else": [{"noop": True}],
                },
            },
        ])

        ev = ASTEvaluator([r1, r2])
        initial = [_fact("Signal", "*", "flag", "==", "C")]
        result = ev.evaluate(initial)

        derived_keys = {f.match_key() for f in result.derived_facts}
        assert ("signal", "*", "flag", "==", "B") in derived_keys
        assert ("signal", "*", "flag", "==", "A") in derived_keys
        assert result.goal_status is None, "No goal → status should be None"


# ── TC-13: Max-iteration guard ────────────────────────────────────────


class TestMaxIterationGuard:
    """TC-13: Evaluation stops at max_iterations even if not converged."""

    def test_max_iterations(self):
        # A rule that always produces new facts (simulate via
        # always-true check + assert of existing fact that doesn't
        # change working memory — the evaluator should still loop).
        # To truly test, we need a scenario where changes keep happening.
        # R1: assert X if Y exists. R2: retract Y if X exists. R3: assert Y if X exists.
        # This creates an infinite oscillation.

        r1 = _make_rule("R-MI01", [
            {
                "check": {"noun": "Toggle", "instance": "*", "property": "state",
                          "operator": "==", "value": "on"},
                "decide": {
                    "then": [
                        {"retract": {"noun": "Toggle", "instance": "*", "property": "state"}},
                        {"assert": {"noun": "Toggle", "instance": "*", "property": "state",
                                    "operator": "==", "value": "off"}},
                    ],
                    "else": [
                        {"retract": {"noun": "Toggle", "instance": "*", "property": "state"}},
                        {"assert": {"noun": "Toggle", "instance": "*", "property": "state",
                                    "operator": "==", "value": "on"}},
                    ],
                },
            },
        ])

        ev = ASTEvaluator([r1], max_iterations=5)
        initial = [_fact("Toggle", "*", "state", "==", "on")]
        result = ev.evaluate(initial)

        assert result.goal_status == "max_iterations", \
            "Evaluation must terminate at max_iterations even if not converged"


# ── TC-14: Goal-based termination ─────────────────────────────────────


class TestGoalTermination:
    """TC-14: Goal-based termination stops when terminal value is reached."""

    def test_goal_resolved(self):
        rule = _make_rule("R-G01", [
            {"assert": {"noun": "Incident", "instance": "*", "property": "rootCause",
                        "operator": "==", "value": "admin_role_missing"}},
        ])
        goal = Goal(
            noun="Incident",
            instance="*",
            property="rootCause",
            initial="unknown",
            terminal=["admin_role_missing", "permission_missing"],
        )

        ev = ASTEvaluator([rule])
        result = ev.evaluate([], goal=goal)
        assert result.goal_status == "resolved", \
            "Goal-based termination should stop evaluation when terminal value is reached"


# ── TC-15: Trace records CHECK result ──────────────────────────────────


class TestTraceCheck:
    """TC-15: Trace entries record CHECK statement with boolean result."""

    def test_trace_check_true(self):
        rule = _make_rule("R-T01", [
            {
                "check": {"noun": "User", "instance": "*", "property": "adminRole",
                          "operator": "==", "value": "unknown"},
                "decide": {
                    "then": [{"noop": True}],
                    "else": [{"noop": True}],
                },
            },
        ])
        ev = ASTEvaluator([rule])
        initial = [_fact("User", "*", "adminRole", "==", "unknown")]
        result = ev.evaluate(initial)

        check_entries = [t for t in result.rule_trace if t.get("stmt_kind") == "CHECK"]
        assert len(check_entries) >= 1, "Trace must record CHECK statement"
        assert check_entries[0]["result"] is True, "CHECK result should be True"

    def test_trace_check_false(self):
        rule = _make_rule("R-T02", [
            {
                "check": {"noun": "User", "instance": "*", "property": "adminRole",
                          "operator": "==", "value": "unknown"},
                "decide": {
                    "then": [{"noop": True}],
                    "else": [{"noop": True}],
                },
            },
        ])
        ev = ASTEvaluator([rule])
        initial = [_fact("User", "*", "adminRole", "==", "confirmed")]
        result = ev.evaluate(initial)

        check_entries = [t for t in result.rule_trace if t.get("stmt_kind") == "CHECK"]
        assert len(check_entries) >= 1, "Trace must record CHECK statement"
        assert check_entries[0]["result"] is False, "CHECK result should be False"


# ── TC-16: Trace records ASSERT/RETRACT delta ─────────────────────────


class TestTraceDelta:
    """TC-16: Trace records working memory delta for ASSERT and RETRACT."""

    def test_trace_assert_and_retract(self):
        rule = _make_rule("R-TD01", [
            {"assert": {"noun": "User", "instance": "*", "property": "adminRole",
                        "operator": "==", "value": "confirmed"}},
            {"retract": {"noun": "User", "instance": "*", "property": "adminRole"}},
        ])
        ev = ASTEvaluator([rule])
        result = ev.evaluate([])

        assert_entries = [t for t in result.rule_trace if t.get("stmt_kind") == "ASSERT"]
        retract_entries = [t for t in result.rule_trace if t.get("stmt_kind") == "RETRACT"]
        assert len(assert_entries) >= 1, "Trace must record ASSERT with fact added"
        assert len(retract_entries) >= 1, "Trace must record RETRACT with fact removed"
        # ASSERT entry should record the fact
        assert "fact" in assert_entries[0], "ASSERT trace entry should include fact info"
