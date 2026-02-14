"""Rule generator — deduplication and filtering of LLM-proposed rules."""
from __future__ import annotations

from ees.models import Fact, Rule
from ees.rule_evaluator import RuleEvaluator


class RuleGenerator:
    """Handles rule deduplication and filtering."""

    def __init__(self, existing_rules: list[Rule]) -> None:
        self._existing = list(existing_rules)

    def is_duplicate(self, rule: Rule) -> bool:
        """Check if a rule is an exact duplicate of any existing CONFIRMED rule.

        GAP-status rules are skipped — a confirmed rule matching a GAP
        is a refinement, not a duplicate.
        """
        for existing in self._existing:
            if existing.status == "GAP":
                continue
            if rule.is_duplicate_of(existing):
                return True
        return False

    def filter_rules(
        self, llm_rules: list[Rule], confirmed_facts: list[Fact]
    ) -> list[Rule]:
        """Filter LLM-proposed rules: remove those with no confirmed facts, and dedup.

        A rule is kept only if ALL its condition facts are present in confirmed_facts.
        Duplicate rules (matching an existing rule) are skipped.

        Variable conditions use unification-based matching via RuleEvaluator.
        """
        if not confirmed_facts:
            return []

        confirmed_set = {f.match_key() for f in confirmed_facts}

        kept: list[Rule] = []
        for rule in llm_rules:
            has_vars = any(c.has_variables for c in rule.conditions.items)

            if has_vars:
                # Slow path: use unification to check if a consistent
                # binding exists against the confirmed facts.
                bindings = RuleEvaluator._conditions_met_with_bindings(
                    rule, confirmed_facts,
                )
                if bindings is None:
                    continue
            else:
                # Fast path: exact match_key lookup
                all_confirmed = all(
                    item.match_key() in confirmed_set
                    for item in rule.conditions.items
                )
                if not all_confirmed:
                    continue

            # Dedup check
            if self.is_duplicate(rule):
                continue

            kept.append(rule)

        return kept
