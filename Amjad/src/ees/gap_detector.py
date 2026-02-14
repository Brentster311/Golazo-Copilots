"""GAP detection and refinement — identifies missing diagnostic chains."""
from __future__ import annotations

from ees.models import Fact, GapRefinement, Rule
from ees.rule_evaluator import RuleEvaluator

# Normalized key type from Fact.match_key()
MatchKey = tuple[str, str, str, str, str]


class GapDetector:
    """Detects knowledge gaps and refines existing GAP rules.

    A "gap" exists when confirmed facts from an incident don't connect
    to the confirmed root cause through any existing or new CONFIRMED rules.
    """

    def __init__(self, existing_rules: list[Rule]) -> None:
        self._existing_rules = list(existing_rules)

    def detect_gaps(
        self,
        confirmed_facts: list[Fact],
        new_rules: list[Rule],
        root_cause: str | None,
        incident_id: str,
    ) -> list[Rule]:
        """Detect orphaned facts and create GAP rules.

        Single-hop analysis: a fact is "connected" if it appears in the
        conditions of any CONFIRMED rule whose then-clause targets the
        root cause.

        Returns a list of GAP rules (0 or 1 for V1).
        """
        if not root_cause or not confirmed_facts:
            return []

        # Collect all CONFIRMED rules (existing + newly confirmed)
        all_rules = self._existing_rules + new_rules

        # Find facts consumed by rules targeting the root cause
        connected_keys: set[MatchKey] = set()
        rc_lower = root_cause.lower()

        for rule in all_rules:
            if rule.status != "CONFIRMED":
                continue
            # Check if this rule's THEN targets the root cause (positive or RULEOUT)
            then_noun = rule.then.noun.lower()
            if then_noun == "rootcause" and rule.then.value.lower() == rc_lower:
                self._collect_connected_keys(rule, confirmed_facts, connected_keys)
            elif then_noun == "ruleout":
                # RULEOUT rules contribute to diagnostic reasoning
                self._collect_connected_keys(rule, confirmed_facts, connected_keys)

        # Orphaned facts = confirmed facts not consumed by any root-cause rule
        orphaned = [f for f in confirmed_facts if f.match_key() not in connected_keys]

        if not orphaned:
            return []

        # Create a single GAP rule bridging orphaned facts → root cause
        gap = Rule(
            rule_id="",  # Assigned later by YamlStore
            status="GAP",
            sources=[incident_id],
            requires=list(orphaned),
            produces=[
                Fact(
                    noun="RootCause",
                    instance="*",
                    property="Name",
                    operator="==",
                    value=root_cause,
                )
            ],
            note="Unknown intermediate diagnostic steps",
        )
        return [gap]

    @staticmethod
    def _collect_connected_keys(
        rule: Rule,
        confirmed_facts: list[Fact],
        connected_keys: set[MatchKey],
    ) -> None:
        """Add match_keys of confirmed facts consumed by *rule*'s conditions.

        For non-variable conditions, adds the condition's own match_key.
        For variable conditions, uses unification to find which confirmed
        facts actually match and adds those facts' keys instead.
        """
        has_vars = any(c.has_variables for c in rule.conditions.items)
        if not has_vars:
            for item in rule.conditions.items:
                connected_keys.add(item.match_key())
        else:
            # Variable conditions: unify each condition against all facts
            for cond in rule.conditions.items:
                if cond.has_variables:
                    for fact in confirmed_facts:
                        if RuleEvaluator._unify_condition(cond, fact) is not None:
                            connected_keys.add(fact.match_key())
                else:
                    connected_keys.add(cond.match_key())

    def check_refinements(
        self,
        new_rules: list[Rule],
        incident_id: str,
    ) -> list[GapRefinement]:
        """Check if new CONFIRMED rules refine existing GAP rules.

        Uses subset matching via match_key():
        - If all GAP requires facts are consumed by new rules → RESOLVED
        - If some but not all are consumed → NARROWED
        - If none overlap → no change

        Returns a list of GapRefinement results.
        """
        results: list[GapRefinement] = []

        # Collect condition facts from new CONFIRMED rules
        new_condition_keys: set[MatchKey] = set()
        new_var_conditions: list[Fact] = []
        for rule in new_rules:
            if rule.status != "CONFIRMED":
                continue
            for item in rule.conditions.items:
                if item.has_variables:
                    new_var_conditions.append(item)
                else:
                    new_condition_keys.add(item.match_key())

        for gap in self._existing_rules:
            if gap.status != "GAP":
                continue

            gap_require_keys = {f.match_key() for f in gap.requires}

            # Direct key overlap
            overlap = gap_require_keys & new_condition_keys

            # Variable-aware overlap: check if any GAP required fact
            # can unify with a variable condition from a new rule
            if new_var_conditions:
                for req_fact in gap.requires:
                    if req_fact.match_key() in overlap:
                        continue  # already matched
                    for var_cond in new_var_conditions:
                        if RuleEvaluator._unify_condition(var_cond, req_fact) is not None:
                            overlap.add(req_fact.match_key())
                            break

            if not overlap:
                continue

            remaining_keys = gap_require_keys - overlap
            updated_sources = list(gap.sources)
            if incident_id not in updated_sources:
                updated_sources.append(incident_id)

            if not remaining_keys:
                # Fully resolved
                updated = Rule(
                    rule_id=gap.rule_id,
                    status="RESOLVED",
                    sources=updated_sources,
                    requires=list(gap.requires),
                    produces=list(gap.produces),
                    note=gap.note,
                )
                results.append(
                    GapRefinement(
                        gap_rule_id=gap.rule_id,
                        action="resolved",
                        updated_rule=updated,
                    )
                )
            else:
                # Narrowed — keep only non-overlapping requires
                remaining_facts = [
                    f for f in gap.requires if f.match_key() in remaining_keys
                ]
                updated = Rule(
                    rule_id=gap.rule_id,
                    status="GAP",
                    sources=updated_sources,
                    requires=remaining_facts,
                    produces=list(gap.produces),
                    note=gap.note,
                )
                results.append(
                    GapRefinement(
                        gap_rule_id=gap.rule_id,
                        action="narrowed",
                        updated_rule=updated,
                    )
                )

        return results
