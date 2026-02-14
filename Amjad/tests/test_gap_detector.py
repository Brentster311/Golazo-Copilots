"""Tests for GAP detection and refinement (EES-00002)."""
import pytest

from ees.gap_detector import GapDetector
from ees.models import Fact, GapRefinement, Rule, RuleConditions, RuleThen


def _fact(noun, prop, op, value, instance="*"):
    return Fact(noun=noun, instance=instance, property=prop, operator=op, value=value)


def _confirmed_rule(rule_id, conditions, then_noun, then_prop, then_value, then_instance="*"):
    """Helper: build a CONFIRMED rule."""
    return Rule(
        rule_id=rule_id,
        status="CONFIRMED",
        sources=["INC-001"],
        conditions=RuleConditions(logic="AND", items=conditions),
        then=RuleThen(noun=then_noun, instance=then_instance, property=then_prop, value=then_value),
    )


def _gap_rule(rule_id, requires, produces_value, sources=None, note="Unknown"):
    """Helper: build a GAP rule."""
    return Rule(
        rule_id=rule_id,
        status="GAP",
        sources=sources or ["INC-001"],
        requires=requires,
        produces=[_fact("RootCause", "Name", "==", produces_value)],
        note=note,
    )


# ── detect_gaps tests ──────────────────────────────────────────────


class TestDetectGaps:
    """TC-01 through TC-06: GAP detection logic."""

    def test_gap_created_for_orphaned_facts(self):
        """TC-01: GAP created when confirmed facts don't connect to root cause."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        fact_b = _fact("Server", "MemoryFree", "<", "5%")
        # Only fact_a connects to root cause via rule
        rule = _confirmed_rule("R-001", [fact_a], "RootCause", "Name", "Resource Exhaustion")

        detector = GapDetector(existing_rules=[rule])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a, fact_b],
            new_rules=[],
            root_cause="Resource Exhaustion",
            incident_id="INC-002",
        )
        assert len(gaps) == 1
        assert gaps[0].status == "GAP"
        assert len(gaps[0].requires) == 1
        assert gaps[0].requires[0].property == "MemoryFree"

    def test_no_gap_when_all_facts_connected(self):
        """TC-02: No GAP when all facts connect to root cause through rules."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        fact_b = _fact("Server", "MemoryFree", "<", "5%")
        rule = _confirmed_rule(
            "R-001", [fact_a, fact_b], "RootCause", "Name", "Resource Exhaustion"
        )

        detector = GapDetector(existing_rules=[rule])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a, fact_b],
            new_rules=[],
            root_cause="Resource Exhaustion",
            incident_id="INC-002",
        )
        assert len(gaps) == 0

    def test_no_gap_when_no_root_cause(self):
        """TC-03: No GAP when no root cause is confirmed."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        detector = GapDetector(existing_rules=[])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a],
            new_rules=[],
            root_cause=None,
            incident_id="INC-001",
        )
        assert len(gaps) == 0

    def test_multiple_orphaned_facts_single_gap(self):
        """TC-04: Multiple orphaned facts produce a single GAP."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        fact_b = _fact("Server", "MemoryFree", "<", "5%")
        fact_c = _fact("Server", "DiskIO", ">", "100")
        # Only fact_a connects
        rule = _confirmed_rule("R-001", [fact_a], "RootCause", "Name", "X")

        detector = GapDetector(existing_rules=[rule])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a, fact_b, fact_c],
            new_rules=[],
            root_cause="X",
            incident_id="INC-002",
        )
        assert len(gaps) == 1
        assert len(gaps[0].requires) == 2

    def test_no_gap_empty_confirmed_facts(self):
        """TC-05: No GAP when no confirmed facts."""
        detector = GapDetector(existing_rules=[])
        gaps = detector.detect_gaps(
            confirmed_facts=[],
            new_rules=[],
            root_cause="X",
            incident_id="INC-001",
        )
        assert len(gaps) == 0

    def test_gap_uses_new_rules_for_connection(self):
        """New rules from this incident are considered for connection check."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        fact_b = _fact("Server", "MemoryFree", "<", "5%")
        new_rule = _confirmed_rule("R-001", [fact_a], "RootCause", "Name", "X")

        detector = GapDetector(existing_rules=[])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a, fact_b],
            new_rules=[new_rule],
            root_cause="X",
            incident_id="INC-002",
        )
        assert len(gaps) == 1
        assert gaps[0].requires[0].property == "MemoryFree"

    def test_gap_produces_matches_root_cause(self):
        """GAP produces list contains the root cause as a fact."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        detector = GapDetector(existing_rules=[])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a],
            new_rules=[],
            root_cause="Resource Exhaustion",
            incident_id="INC-001",
        )
        assert len(gaps) == 1
        assert gaps[0].produces[0].noun == "RootCause"
        assert gaps[0].produces[0].value == "Resource Exhaustion"

    def test_gap_sources_contain_incident_id(self):
        """GAP sources list contains the current incident ID."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        detector = GapDetector(existing_rules=[])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a],
            new_rules=[],
            root_cause="X",
            incident_id="INC-042",
        )
        assert "INC-042" in gaps[0].sources

    def test_gap_case_insensitive_root_cause_match(self):
        """Root cause matching is case-insensitive."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        fact_b = _fact("Server", "MemoryFree", "<", "5%")
        # Rule then value has different case than root_cause param
        rule = _confirmed_rule("R-001", [fact_a], "RootCause", "Name", "resource exhaustion")

        detector = GapDetector(existing_rules=[rule])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a, fact_b],
            new_rules=[],
            root_cause="Resource Exhaustion",
            incident_id="INC-002",
        )
        # fact_a should still be connected (case-insensitive match)
        assert len(gaps) == 1
        assert gaps[0].requires[0].property == "MemoryFree"

    def test_all_facts_orphaned_creates_gap(self):
        """When no rules exist at all, all facts are orphaned."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        detector = GapDetector(existing_rules=[])
        gaps = detector.detect_gaps(
            confirmed_facts=[fact_a],
            new_rules=[],
            root_cause="X",
            incident_id="INC-001",
        )
        assert len(gaps) == 1
        assert len(gaps[0].requires) == 1


# ── check_refinements tests ───────────────────────────────────────


class TestCheckRefinements:
    """TC-14 through TC-18: GAP refinement logic."""

    def test_full_resolution(self):
        """TC-14: GAP fully resolved when new rules bridge requires→produces."""
        orphan = _fact("Server", "MemoryFree", "<", "5%")
        gap = _gap_rule("R-010", requires=[orphan], produces_value="Resource Exhaustion")

        # New rule connects the orphaned fact to root cause
        new_rule = _confirmed_rule(
            "R-011", [orphan], "RootCause", "Name", "Resource Exhaustion"
        )
        detector = GapDetector(existing_rules=[gap])
        results = detector.check_refinements([new_rule], "INC-002")

        assert len(results) == 1
        assert results[0].action == "resolved"
        assert results[0].updated_rule.status == "RESOLVED"

    def test_partial_narrowing(self):
        """TC-15: GAP narrowed when new rules cover some requires facts."""
        orphan_a = _fact("Server", "MemoryFree", "<", "5%")
        orphan_b = _fact("Server", "DiskIO", ">", "100")
        gap = _gap_rule("R-010", requires=[orphan_a, orphan_b], produces_value="X")

        # New rule only covers orphan_a
        new_rule = _confirmed_rule("R-011", [orphan_a], "RootCause", "Name", "X")

        detector = GapDetector(existing_rules=[gap])
        results = detector.check_refinements([new_rule], "INC-002")

        assert len(results) == 1
        assert results[0].action == "narrowed"
        assert len(results[0].updated_rule.requires) == 1
        assert results[0].updated_rule.requires[0].property == "DiskIO"

    def test_no_refinement_when_no_overlap(self):
        """TC-16: No refinement when new rules don't overlap with GAP."""
        orphan = _fact("Server", "MemoryFree", "<", "5%")
        gap = _gap_rule("R-010", requires=[orphan], produces_value="X")

        # New rule has completely different conditions
        new_rule = _confirmed_rule(
            "R-011", [_fact("Network", "Latency", ">", "100")], "RootCause", "Name", "X"
        )
        detector = GapDetector(existing_rules=[gap])
        results = detector.check_refinements([new_rule], "INC-002")

        assert len(results) == 0

    def test_multiple_gaps_only_overlapping_refined(self):
        """TC-17: Only the overlapping GAP is refined."""
        orphan_a = _fact("Server", "MemoryFree", "<", "5%")
        orphan_b = _fact("Network", "Latency", ">", "100")
        gap1 = _gap_rule("R-010", requires=[orphan_a], produces_value="X")
        gap2 = _gap_rule("R-011", requires=[orphan_b], produces_value="Y")

        # New rule overlaps with gap1 only
        new_rule = _confirmed_rule("R-012", [orphan_a], "RootCause", "Name", "X")

        detector = GapDetector(existing_rules=[gap1, gap2])
        results = detector.check_refinements([new_rule], "INC-002")

        assert len(results) == 1
        assert results[0].gap_rule_id == "R-010"

    def test_resolved_gap_preserves_sources(self):
        """TC-18: Resolved GAP preserves source incident provenance."""
        orphan = _fact("Server", "MemoryFree", "<", "5%")
        gap = _gap_rule("R-010", requires=[orphan], produces_value="X", sources=["INC-001"])

        new_rule = _confirmed_rule("R-011", [orphan], "RootCause", "Name", "X")

        detector = GapDetector(existing_rules=[gap])
        results = detector.check_refinements([new_rule], "INC-002")

        assert "INC-001" in results[0].updated_rule.sources
        assert "INC-002" in results[0].updated_rule.sources

    def test_narrowed_gap_updates_sources(self):
        """Narrowed GAP adds new incident to sources."""
        orphan_a = _fact("Server", "MemoryFree", "<", "5%")
        orphan_b = _fact("Server", "DiskIO", ">", "100")
        gap = _gap_rule("R-010", requires=[orphan_a, orphan_b], produces_value="X", sources=["INC-001"])

        new_rule = _confirmed_rule("R-011", [orphan_a], "RootCause", "Name", "X")

        detector = GapDetector(existing_rules=[gap])
        results = detector.check_refinements([new_rule], "INC-002")

        assert "INC-002" in results[0].updated_rule.sources

    def test_skip_non_gap_rules(self):
        """check_refinements ignores CONFIRMED rules in existing_rules."""
        confirmed = _confirmed_rule(
            "R-001", [_fact("S", "P", ">", "1")], "RootCause", "Name", "X"
        )
        detector = GapDetector(existing_rules=[confirmed])
        new_rule = _confirmed_rule(
            "R-002", [_fact("S", "P", ">", "1")], "RootCause", "Name", "X"
        )
        results = detector.check_refinements([new_rule], "INC-002")
        assert len(results) == 0

    def test_skip_resolved_gaps(self):
        """check_refinements ignores already-RESOLVED gaps."""
        orphan = _fact("Server", "MemoryFree", "<", "5%")
        resolved = Rule(
            rule_id="R-010",
            status="RESOLVED",
            sources=["INC-001"],
            requires=[orphan],
            produces=[_fact("RootCause", "Name", "==", "X")],
            note="was a gap",
        )
        new_rule = _confirmed_rule("R-011", [orphan], "RootCause", "Name", "X")
        detector = GapDetector(existing_rules=[resolved])
        results = detector.check_refinements([new_rule], "INC-002")
        assert len(results) == 0


# ── RULEOUT + GAP Detection Tests (EES-00003) ──────────────────────


class TestDetectGapsRuleout:
    """TC-20, TC-21, TC-22: RULEOUT rules in GAP detection."""

    def test_ruleout_facts_are_connected(self):
        """TC-20: Facts connected via RULEOUT rules are not orphaned."""
        fact_a = _fact("Net", "Latency", "==", "normal")
        fact_b = _fact("Server", "MemoryFree", "<", "5%")

        # fact_a connected via RULEOUT rule
        ruleout = Rule(
            rule_id="R-020",
            status="CONFIRMED",
            type="ruleout",
            sources=["INC-001"],
            conditions=RuleConditions(logic="AND", items=[fact_a]),
            then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
        )

        # fact_b connected via positive rule
        positive = _confirmed_rule("R-001", [fact_b], "RootCause", "Name", "Resource Exhaustion")

        detector = GapDetector(existing_rules=[ruleout, positive])
        gaps = detector.detect_gaps([fact_a, fact_b], [], "Resource Exhaustion", "INC-002")
        assert len(gaps) == 0  # No orphaned facts

    def test_ruleout_mixed_with_positive(self):
        """TC-21: Mix of positive + RULEOUT rules — all connected facts excluded."""
        fact_a = _fact("Server", "CPUUsage", ">", "90")
        fact_b = _fact("Net", "Latency", "==", "normal")

        positive = _confirmed_rule("R-001", [fact_a], "RootCause", "Name", "RC1")
        ruleout = Rule(
            rule_id="R-020",
            status="CONFIRMED",
            type="ruleout",
            sources=["INC-001"],
            conditions=RuleConditions(logic="AND", items=[fact_b]),
            then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
        )

        detector = GapDetector(existing_rules=[positive, ruleout])
        gaps = detector.detect_gaps([fact_a, fact_b], [], "RC1", "INC-002")
        assert len(gaps) == 0

    def test_ruleout_present_but_facts_still_orphaned(self):
        """TC-22: RULEOUT rules exist but some facts are still orphaned."""
        fact_a = _fact("Net", "Latency", "==", "normal")
        fact_b = _fact("Server", "MemoryFree", "<", "5%")
        fact_c = _fact("Disk", "IOPS", ">", "1000")  # orphaned

        ruleout = Rule(
            rule_id="R-020",
            status="CONFIRMED",
            type="ruleout",
            sources=["INC-001"],
            conditions=RuleConditions(logic="AND", items=[fact_a]),
            then=RuleThen("RULEOUT", "*", "Target", "Network Issue"),
        )
        positive = _confirmed_rule("R-001", [fact_b], "RootCause", "Name", "RC1")

        detector = GapDetector(existing_rules=[ruleout, positive])
        gaps = detector.detect_gaps([fact_a, fact_b, fact_c], [], "RC1", "INC-003")
        assert len(gaps) == 1
        # fact_c should be in the GAP's requires
        require_keys = {f.match_key() for f in gaps[0].requires}
        assert fact_c.match_key() in require_keys
