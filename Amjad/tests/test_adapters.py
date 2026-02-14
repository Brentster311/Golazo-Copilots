"""Tests for ees.gui.adapters — facts_used_by_rules helper."""
from __future__ import annotations

import pytest

from ees.gui.adapters import facts_used_by_rules
from ees.models import Fact, Rule, RuleConditions, RuleOutput


def _fact(noun: str, prop: str) -> Fact:
    return Fact(noun=noun, instance="*", property=prop, operator="==", value="v")


def _rule(*conditions: tuple[str, str], then_kind: str = "CHANGE_STATE") -> Rule:
    items = [
        Fact(noun=n, instance="*" if n not in {"RULED_OUT", "CHANGE_STATE", "GAP"} else "*",
             property=p, operator="==", value="v" if n not in {"RULED_OUT", "CHANGE_STATE", "GAP"} else "true")
        for n, p in conditions
    ]
    return Rule(
        rule_id="",
        conditions=RuleConditions(logic="AND", items=items),
        then=RuleOutput(kind=then_kind, description="test"),
    )


class TestFactsUsedByRules:
    def test_returns_used_indices(self):
        """TC-01: Returns correct indices for facts used by rules."""
        facts = [_fact("User", "adminRole"), _fact("Case", "severity"), _fact("Permission", "mailAPI")]
        rules = [_rule(("User", "adminRole"), ("Permission", "mailAPI"))]

        result = facts_used_by_rules(facts, rules)
        assert result == {0, 2}

    def test_chaining_conditions_excluded(self):
        """TC-02: RULED_OUT/CHANGE_STATE/GAP conditions don't count as 'used'."""
        facts = [_fact("User", "adminRole")]
        rules = [_rule(("RULED_OUT", "User.adminRole"), then_kind="GAP")]

        result = facts_used_by_rules(facts, rules)
        assert result == set()

    def test_no_rules_returns_empty(self):
        """TC-03: No rules → empty set."""
        facts = [_fact("User", "adminRole"), _fact("Case", "severity")]
        result = facts_used_by_rules(facts, [])
        assert result == set()

    def test_case_insensitive_matching(self):
        """TC-04: Matching is case-insensitive."""
        facts = [_fact("user", "adminRole")]
        rules = [_rule(("User", "AdminRole"))]

        result = facts_used_by_rules(facts, rules)
        assert result == {0}

    def test_same_noun_different_property_not_matched(self):
        """TC-05: Same noun but different property is not a match."""
        facts = [_fact("Error", "code")]
        rules = [_rule(("Error", "message"))]

        result = facts_used_by_rules(facts, rules)
        assert result == set()

    def test_multiple_rules_union(self):
        """Multiple rules — used set is the union of all conditions."""
        facts = [_fact("A", "p1"), _fact("B", "p2"), _fact("C", "p3")]
        rules = [_rule(("A", "p1")), _rule(("C", "p3"))]

        result = facts_used_by_rules(facts, rules)
        assert result == {0, 2}

    def test_no_facts_returns_empty(self):
        """No facts → empty set regardless of rules."""
        rules = [_rule(("User", "adminRole"))]
        result = facts_used_by_rules([], rules)
        assert result == set()
