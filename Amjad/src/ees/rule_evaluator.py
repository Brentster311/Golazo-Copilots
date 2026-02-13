"""Forward-chaining rule evaluation engine.

Evaluates a set of input facts against the knowledge base rules using
forward chaining. Matching is symbolic/string-based via match_key().
"""
from __future__ import annotations

from ees.models import EvaluationResult, Fact, Rule


class RuleEvaluator:
    """Evaluates rules against input facts using forward chaining."""

    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    def evaluate(self, input_facts: list[Fact]) -> EvaluationResult:
        """Evaluate all rules against input facts.

        Forward chaining algorithm:
        1. Start with input facts as the working set.
        2. Iterate CONFIRMED rules. If all conditions match (AND) or
           any condition matches (OR), the rule fires — add derived fact.
        3. Repeat until no new facts are derived (fixed-point).
        4. Scan GAP rules for those whose requires are all in working set.

        Returns EvaluationResult with root causes, ruleouts, gaps, trace.
        """
        # Build working set keyed by match_key for O(1) lookup
        working_keys: set[tuple] = set()
        working_facts: list[Fact] = list(input_facts)
        for f in input_facts:
            working_keys.add(f.match_key())

        # Separate CONFIRMED rules (fireable) from GAP rules
        confirmed_rules = [r for r in self._rules if r.status == "CONFIRMED"]
        gap_rules = [r for r in self._rules if r.status == "GAP"]

        fired_rules: list[Rule] = []
        fired_rule_ids: set[str] = set()
        derived_facts: list[Fact] = []
        rule_trace: list[dict] = []
        iteration = 0

        # Forward chaining loop
        changed = True
        while changed:
            changed = False
            iteration += 1
            for rule in confirmed_rules:
                if rule.rule_id in fired_rule_ids:
                    continue
                if self._conditions_met(rule, working_keys):
                    # Rule fires — create derived fact from then clause
                    derived = Fact(
                        noun=rule.then.noun,
                        instance=rule.then.instance,
                        property=rule.then.property,
                        operator="==",
                        value=rule.then.value,
                    )
                    derived_key = derived.match_key()
                    if derived_key not in working_keys:
                        working_keys.add(derived_key)
                        working_facts.append(derived)
                        derived_facts.append(derived)
                        changed = True

                    fired_rules.append(rule)
                    fired_rule_ids.add(rule.rule_id)
                    rule_trace.append({
                        "rule_id": rule.rule_id,
                        "iteration": iteration,
                        "derived": derived.to_display(),
                    })

        # Collect root causes and ruleouts from fired rules
        root_causes: list[str] = []
        ruled_out: list[str] = []
        for rule in fired_rules:
            if rule.then.noun.lower() == "rootcause":
                root_causes.append(rule.then.value)
            elif rule.then.noun.lower() == "ruleout":
                ruled_out.append(rule.then.value)

        # Scan GAP rules — report those whose requires are all in working set
        triggered_gaps: list[Rule] = []
        for gap in gap_rules:
            if gap.requires and all(
                f.match_key() in working_keys for f in gap.requires
            ):
                triggered_gaps.append(gap)

        return EvaluationResult(
            input_facts=list(input_facts),
            derived_facts=derived_facts,
            fired_rules=fired_rules,
            root_causes=root_causes,
            ruled_out=ruled_out,
            gap_rules=triggered_gaps,
            rule_trace=rule_trace,
        )

    @staticmethod
    def _conditions_met(rule: Rule, working_keys: set[tuple]) -> bool:
        """Check if a rule's conditions are satisfied by the working set."""
        if not rule.conditions.items:
            return False

        if rule.conditions.logic == "OR":
            return any(
                item.match_key() in working_keys
                for item in rule.conditions.items
            )
        else:  # AND (default)
            return all(
                item.match_key() in working_keys
                for item in rule.conditions.items
            )
