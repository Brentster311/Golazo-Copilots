"""Tests for ees.rule_generator — v2 deduplication and filtering."""
from __future__ import annotations

import pytest
from ees.models import (
    Fact,
    Rule,
    RuleConditions,
    RuleOutput,
)
from ees.rule_generator import RuleGenerator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fact(noun: str, value: str, instance: str = "*", prop: str = "Status") -> Fact:
    return Fact(noun=noun, instance=instance, property=prop, operator="==", value=value)


def _cond(*pairs: tuple[str, str], logic: str = "AND") -> RuleConditions:
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
# TC10: is_duplicate
# ============================================================================

class TestIsDuplicate:
    def test_is_duplicate_v2(self):
        """Two rules with same conditions + then + else_ → duplicate."""
        existing = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU problem"),
            else_=RuleOutput(kind="RULED_OUT", description="CPU ok"),
        )
        candidate = _rule(
            "R2",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU problem"),
            else_=RuleOutput(kind="RULED_OUT", description="CPU ok"),
        )
        gen = RuleGenerator([existing])
        assert gen.is_duplicate(candidate)

    def test_not_duplicate_different_then(self):
        existing = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="CPU problem"),
        )
        candidate = _rule(
            "R2",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="RULED_OUT", description="CPU problem"),
        )
        gen = RuleGenerator([existing])
        assert not gen.is_duplicate(candidate)

    def test_not_duplicate_different_conditions(self):
        existing = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        candidate = _rule(
            "R2",
            _cond(("Memory", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        gen = RuleGenerator([existing])
        assert not gen.is_duplicate(candidate)

    def test_not_duplicate_different_else(self):
        existing = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="a"),
        )
        candidate = _rule(
            "R2",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            else_=RuleOutput(kind="RULED_OUT", description="b"),
        )
        gen = RuleGenerator([existing])
        assert not gen.is_duplicate(candidate)

    def test_gap_status_skipped_in_dedup(self):
        """GAP-status rules are skipped — a confirmed rule matching a GAP is a refinement."""
        existing = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
            status="GAP",
        )
        candidate = _rule(
            "R2",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        gen = RuleGenerator([existing])
        assert not gen.is_duplicate(candidate)

    def test_empty_existing(self):
        candidate = _rule(
            "R1",
            _cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        gen = RuleGenerator([])
        assert not gen.is_duplicate(candidate)


# ============================================================================
# TC10: filter_rules
# ============================================================================

class TestFilterRules:
    def test_filter_rules_v2_keeps_matching(self):
        """filter_rules keeps rules whose conditions are all in confirmed_facts."""
        existing = []
        gen = RuleGenerator(existing)

        candidate = _rule(
            "R1",
            _cond(("CPU", "High"), ("Memory", "Low")),
            then=RuleOutput(kind="CHANGE_STATE", description="both issues"),
        )
        confirmed = [_fact("CPU", "High"), _fact("Memory", "Low")]
        kept = gen.filter_rules([candidate], confirmed)
        assert len(kept) == 1
        assert kept[0].rule_id == "R1"

    def test_filter_rules_removes_unconfirmed(self):
        """Rules with conditions not in confirmed_facts are removed."""
        gen = RuleGenerator([])
        candidate = _rule(
            "R1",
            _cond(("CPU", "High"), ("Disk", "Full")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        confirmed = [_fact("CPU", "High")]  # Disk not confirmed
        kept = gen.filter_rules([candidate], confirmed)
        assert len(kept) == 0

    def test_filter_rules_removes_duplicates(self):
        """Duplicates of existing rules are removed."""
        existing = _rule(
            "R1",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        gen = RuleGenerator([existing])

        candidate = _rule(
            "R2",
            _cond(("CPU", "High")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        confirmed = [_fact("CPU", "High")]
        kept = gen.filter_rules([candidate], confirmed)
        assert len(kept) == 0

    def test_filter_rules_empty_confirmed(self):
        gen = RuleGenerator([])
        candidate = _rule(
            "R1",
            _cond(("A", "1")),
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        kept = gen.filter_rules([candidate], [])
        assert len(kept) == 0

    def test_filter_rules_with_variables(self):
        """Variable conditions use unification matching."""
        gen = RuleGenerator([])
        cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="Server", instance="$host", property="CPU",
                     operator="==", value="High"),
            ],
        )
        candidate = _rule(
            "R1",
            cond,
            then=RuleOutput(kind="CHANGE_STATE", description="server issue"),
        )
        confirmed = [
            Fact(noun="Server", instance="web01", property="CPU",
                 operator="==", value="High"),
        ]
        kept = gen.filter_rules([candidate], confirmed)
        assert len(kept) == 1

    def test_filter_rules_variable_no_match(self):
        gen = RuleGenerator([])
        cond = RuleConditions(
            logic="AND",
            items=[
                Fact(noun="Server", instance="$host", property="CPU",
                     operator="==", value="High"),
            ],
        )
        candidate = _rule(
            "R1",
            cond,
            then=RuleOutput(kind="CHANGE_STATE", description="x"),
        )
        confirmed = [
            Fact(noun="Server", instance="web01", property="CPU",
                 operator="==", value="Low"),
        ]
        kept = gen.filter_rules([candidate], confirmed)
        assert len(kept) == 0

    def test_filter_multiple_candidates(self):
        """Multiple candidates — keeps valid, removes invalid."""
        gen = RuleGenerator([])
        good = _rule("R1", _cond(("A", "1")),
                      then=RuleOutput(kind="CHANGE_STATE", description="ok"))
        bad = _rule("R2", _cond(("Z", "9")),
                     then=RuleOutput(kind="CHANGE_STATE", description="nope"))
        confirmed = [_fact("A", "1")]
        kept = gen.filter_rules([good, bad], confirmed)
        assert len(kept) == 1
        assert kept[0].rule_id == "R1"
