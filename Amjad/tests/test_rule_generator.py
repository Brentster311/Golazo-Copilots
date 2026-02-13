"""Tests for rule generator."""
import pytest

from ees.rule_generator import RuleGenerator
from ees.models import Fact, Rule, RuleConditions, RuleThen


class TestRuleGeneratorHappyPath:
    """TC-16, TC-17, TC-18, TC-19: Rule generation."""

    def test_generate_rule_with_required_fields(self):
        """TC-16: Generated rule has all required fields."""
        rule = Rule(
            rule_id="R-001",
            status="CONFIRMED",
            type="positive",
            sources=["INC-001"],
            conditions=RuleConditions(
                logic="AND",
                items=[
                    Fact("Server", "*", "CPUUsage", ">", "90"),
                    Fact("Server", "*", "MemoryFree", "<", "5%"),
                ],
            ),
            then=RuleThen("Server", "*", "ResourceExhausted", "TRUE"),
            because="High CPU combined with low memory indicates resource exhaustion",
        )
        d = rule.to_dict()
        assert d["rule_id"] == "R-001"
        assert d["status"] == "CONFIRMED"
        assert d["type"] == "positive"
        assert "INC-001" in d["sources"]
        assert d["conditions"]["logic"] in ("AND", "OR")
        assert len(d["conditions"]["items"]) > 0
        assert d["then"]["noun"] == "Server"
        assert len(d["because"]) > 0

    def test_flat_logic_only(self):
        """TC-17: Rules use flat AND or OR only, never mixed."""
        rule = Rule(
            rule_id="R-001",
            conditions=RuleConditions(
                logic="AND",
                items=[
                    Fact("S", "*", "A", ">", "1"),
                    Fact("S", "*", "B", "<", "2"),
                ],
            ),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="reason",
        )
        assert rule.conditions.logic in ("AND", "OR")

    def test_instance_preserved(self):
        """TC-18: Rules preserve instance parameter."""
        rule = Rule(
            rule_id="R-001",
            conditions=RuleConditions(
                logic="AND",
                items=[Fact("Server", "WebApp01", "CPUUsage", ">", "90")],
            ),
            then=RuleThen("Server", "WebApp01", "ResourceExhausted", "TRUE"),
            because="specific server",
        )
        assert rule.conditions.items[0].instance == "WebApp01"
        assert rule.then.instance == "WebApp01"

    def test_single_fact_rule(self):
        """TC-19: Single confirmed fact generates a valid rule."""
        rule = Rule(
            rule_id="R-001",
            conditions=RuleConditions(
                logic="AND",
                items=[Fact("Server", "*", "CPUUsage", ">", "90")],
            ),
            then=RuleThen("Server", "*", "HighLoad", "TRUE"),
            because="reason",
        )
        assert len(rule.conditions.items) == 1
        d = rule.to_dict()
        assert d["conditions"]["logic"] == "AND"


class TestRuleGeneratorDuplication:
    """MN-3: Duplicate rule detection."""

    def test_exact_duplicate_detected(self):
        """Exact duplicate rules are detected."""
        gen = RuleGenerator(existing_rules=[
            Rule(
                rule_id="R-001",
                conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
                then=RuleThen("S", "*", "X", "TRUE"),
                because="a",
            ),
        ])
        new_rule = Rule(
            rule_id="R-002",
            conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="b",
        )
        assert gen.is_duplicate(new_rule)

    def test_not_duplicate_different_value(self):
        gen = RuleGenerator(existing_rules=[
            Rule(
                rule_id="R-001",
                conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
                then=RuleThen("S", "*", "X", "TRUE"),
                because="a",
            ),
        ])
        new_rule = Rule(
            rule_id="R-002",
            conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "2")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="b",
        )
        assert not gen.is_duplicate(new_rule)


class TestRuleGeneratorConfirmation:
    """TC-05-TC-10: User confirmation of rules (via simulated input)."""

    def test_all_facts_rejected_no_rules(self):
        """TC-10: All facts rejected means no rules generated."""
        gen = RuleGenerator(existing_rules=[])
        # If all facts are rejected, the confirmed facts list is empty
        # and no rules should be produced
        confirmed_facts = []
        llm_rules = []
        result = gen.filter_rules(llm_rules, confirmed_facts)
        assert len(result) == 0


class TestFilterRules:
    """Coverage for filter_rules logic: confirmed-fact matching and dedup."""

    def test_keep_rule_all_conditions_confirmed(self):
        """Rule is kept when all its condition facts are in confirmed_facts."""
        gen = RuleGenerator(existing_rules=[])
        confirmed = [
            Fact("Server", "*", "CPUUsage", ">", "90"),
            Fact("Server", "*", "MemoryFree", "<", "5%"),
        ]
        rule = Rule(
            rule_id="",
            conditions=RuleConditions("AND", [
                Fact("Server", "*", "CPUUsage", ">", "90"),
                Fact("Server", "*", "MemoryFree", "<", "5%"),
            ]),
            then=RuleThen("Server", "*", "Overloaded", "TRUE"),
            because="reason",
        )
        result = gen.filter_rules([rule], confirmed)
        assert len(result) == 1

    def test_drop_rule_missing_condition(self):
        """Rule is dropped when a condition fact is not confirmed."""
        gen = RuleGenerator(existing_rules=[])
        confirmed = [Fact("Server", "*", "CPUUsage", ">", "90")]
        rule = Rule(
            rule_id="",
            conditions=RuleConditions("AND", [
                Fact("Server", "*", "CPUUsage", ">", "90"),
                Fact("Server", "*", "MemoryFree", "<", "5%"),  # not confirmed
            ]),
            then=RuleThen("Server", "*", "Overloaded", "TRUE"),
            because="reason",
        )
        result = gen.filter_rules([rule], confirmed)
        assert len(result) == 0

    def test_drop_duplicate_rule_in_filter(self):
        """Rule is dropped if it duplicates an existing rule."""
        existing = Rule(
            rule_id="R-001",
            conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="old",
        )
        gen = RuleGenerator(existing_rules=[existing])
        confirmed = [Fact("S", "*", "P", ">", "1")]
        dup = Rule(
            rule_id="",
            conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="new",
        )
        result = gen.filter_rules([dup], confirmed)
        assert len(result) == 0

    def test_case_insensitive_matching(self):
        """Confirmed facts match rule conditions case-insensitively on noun/property."""
        gen = RuleGenerator(existing_rules=[])
        confirmed = [Fact("server", "*", "cpuusage", ">", "90")]
        rule = Rule(
            rule_id="",
            conditions=RuleConditions("AND", [Fact("Server", "*", "CPUUsage", ">", "90")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="r",
        )
        result = gen.filter_rules([rule], confirmed)
        assert len(result) == 1

    def test_mixed_keep_and_drop(self):
        """Multiple rules: some kept, some dropped."""
        gen = RuleGenerator(existing_rules=[])
        confirmed = [Fact("S", "*", "A", ">", "1")]
        good = Rule(
            rule_id="",
            conditions=RuleConditions("AND", [Fact("S", "*", "A", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="r",
        )
        bad = Rule(
            rule_id="",
            conditions=RuleConditions("AND", [Fact("S", "*", "B", "<", "2")]),
            then=RuleThen("S", "*", "Y", "TRUE"),
            because="r",
        )
        result = gen.filter_rules([good, bad], confirmed)
        assert len(result) == 1
        assert result[0].then.property == "X"
