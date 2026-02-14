"""Forward-chaining rule evaluation engine.

Evaluates a set of input facts against the knowledge base rules using
forward chaining. Matching is symbolic/string-based via match_key().
"""
from __future__ import annotations

from itertools import product

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

                # Fast path: no variables in conditions — use hash lookup
                has_vars = any(c.has_variables for c in rule.conditions.items)
                if not has_vars:
                    if not self._conditions_met(rule, working_keys):
                        continue
                    bindings: dict[str, str] = {}
                else:
                    # Slow path: variable binding with backtracking
                    bindings = self._conditions_met_with_bindings(
                        rule, working_facts,
                    )
                    if bindings is None:
                        continue

                # Rule fires — create derived fact, substituting bindings
                derived = self._substitute_then(rule, bindings)
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

    # ---- condition matching ---------------------------------------------------

    @staticmethod
    def _conditions_met(rule: Rule, working_keys: set[tuple]) -> bool:
        """Check if a rule's conditions are satisfied by the working set (no variables)."""
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

    # ---- variable binding (slow path) ----------------------------------------

    @classmethod
    def _unify_condition(
        cls,
        condition: Fact,
        fact: Fact,
    ) -> dict[str, str] | None:
        """Try to unify *condition* with *fact*, returning a binding dict.

        Non-variable fields must match exactly (case-insensitive for
        noun/property, exact for operator/instance/value). Variable fields
        bind to the corresponding fact field.

        Returns None on mismatch.
        """
        if condition.noun.lower() != fact.noun.lower():
            return None
        if condition.property.lower() != fact.property.lower():
            return None
        if condition.operator != fact.operator:
            return None

        bindings: dict[str, str] = {}

        # Instance field
        if Fact.is_variable(condition.instance):
            bindings[condition.instance] = fact.instance
        elif condition.instance != fact.instance:
            return None

        # Value field
        if Fact.is_variable(condition.value):
            bindings[condition.value] = fact.value
        elif condition.value != fact.value:
            return None

        return bindings

    @classmethod
    def _conditions_met_with_bindings(
        cls,
        rule: Rule,
        working_facts: list[Fact],
    ) -> dict[str, str] | None:
        """Check conditions with variable binding.  Returns bindings dict or None.

        AND logic: all conditions must match with a consistent binding.
        OR logic: any single condition match is sufficient.
        """
        conditions = rule.conditions.items
        if not conditions:
            return None

        if rule.conditions.logic == "OR":
            # Any single condition match is enough
            for cond in conditions:
                for fact in working_facts:
                    b = cls._unify_condition(cond, fact)
                    if b is not None:
                        return b
            return None

        # AND logic — gather candidates per condition, then find consistent binding
        candidates_per_cond: list[list[dict[str, str]]] = []
        for cond in conditions:
            cands: list[dict[str, str]] = []
            for fact in working_facts:
                b = cls._unify_condition(cond, fact)
                if b is not None:
                    cands.append(b)
            if not cands:
                return None  # no match for this condition at all
            candidates_per_cond.append(cands)

        # Try all combinations (Cartesian product) to find consistent binding
        for combo in product(*candidates_per_cond):
            merged: dict[str, str] = {}
            ok = True
            for b in combo:
                for var, val in b.items():
                    if var in merged and merged[var] != val:
                        ok = False
                        break
                    merged[var] = val
                if not ok:
                    break
            if ok:
                return merged

        return None

    # ---- then substitution ---------------------------------------------------

    @staticmethod
    def _substitute_then(rule: Rule, bindings: dict[str, str]) -> Fact:
        """Create derived Fact from rule.then, substituting whole-field variables."""
        instance = rule.then.instance
        value = rule.then.value

        if Fact.is_variable(instance) and instance in bindings:
            instance = bindings[instance]
        if Fact.is_variable(value) and value in bindings:
            value = bindings[value]

        return Fact(
            noun=rule.then.noun,
            instance=instance,
            property=rule.then.property,
            operator="==",
            value=value,
        )
