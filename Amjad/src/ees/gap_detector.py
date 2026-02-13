"""GAP detection and refinement — identifies missing diagnostic chains."""
from __future__ import annotations

from ees.models import Fact, GapRefinement, Rule

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
                for item in rule.conditions.items:
                    connected_keys.add(item.match_key())
            elif then_noun == "ruleout":
                # RULEOUT rules contribute to diagnostic reasoning
                for item in rule.conditions.items:
                    connected_keys.add(item.match_key())

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
            because=(
                f"Facts {', '.join(f.to_display() for f in orphaned)} do not connect "
                f"to root cause '{root_cause}' through any known rules"
            ),
        )
        return [gap]

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
        for rule in new_rules:
            if rule.status != "CONFIRMED":
                continue
            for item in rule.conditions.items:
                new_condition_keys.add(item.match_key())

        for gap in self._existing_rules:
            if gap.status != "GAP":
                continue

            gap_require_keys = {f.match_key() for f in gap.requires}
            overlap = gap_require_keys & new_condition_keys

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
                    because=gap.because,
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
                    because=gap.because,
                )
                results.append(
                    GapRefinement(
                        gap_rule_id=gap.rule_id,
                        action="narrowed",
                        updated_rule=updated,
                    )
                )

        return results
