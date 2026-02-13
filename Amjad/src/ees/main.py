"""CLI entry point for the Expert System."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ees.exceptions import ConfigError, IncidentLoadError, LLMError
from ees.fact_extractor import FactExtractor
from ees.incident_loader import IncidentLoader
from ees.models import Fact, Incident, Rule, RootCause
from ees.ontology_manager import OntologyManager
from ees.rule_generator import RuleGenerator
from ees.yaml_store import YamlStore


def _confirm_facts(facts: list[Fact]) -> list[Fact]:
    """Interactive CLI confirmation of proposed facts.

    Actions: c=confirm, e=edit, r=reject, s=specialize
    Returns the processed facts (all with status set).
    """
    result: list[Fact] = []

    print("\nProposed facts (LLM defaults to generalized *):")
    for i, fact in enumerate(facts, 1):
        while True:
            action = input(
                f"  {i}. {fact.to_display()}  [confirm/edit/reject/specialize] (c/e/r/s): "
            ).strip().lower()

            if action == "c":
                fact.status = "confirmed"
                result.append(fact)
                break
            elif action == "r":
                fact.status = "rejected"
                result.append(fact)
                break
            elif action == "e":
                edited = _edit_fact(fact)
                if edited:
                    result.append(edited)
                    break
                # If edit failed 3 times, skip this fact
                fact.status = "rejected"
                result.append(fact)
                break
            elif action == "s":
                specialized = _specialize_fact(fact)
                if specialized:
                    result.append(specialized)
                    break
            else:
                print("    Invalid action. Enter c, e, r, or s.")

    return result


def _edit_fact(fact: Fact) -> Fact | None:
    """Prompt user to edit a fact. Returns edited fact or None after 3 failures."""
    for attempt in range(3):
        text = input("     Enter edited fact: ").strip()
        parsed = Fact.parse(text)
        if parsed:
            parsed.status = "confirmed"
            return parsed
        remaining = 2 - attempt
        if remaining > 0:
            print(
                f"    Invalid fact format. Expected: Noun(instance).Property operator value "
                f"({remaining} attempt(s) remaining)"
            )
        else:
            print("    Invalid fact format. Expected: Noun(instance).Property operator value")
            print("    Skipping this fact.")
    return None


def _specialize_fact(fact: Fact) -> Fact | None:
    """Prompt user to specialize a fact's instance."""
    instance = input("     Enter instance: ").strip()
    if not instance:
        print("    Empty instance. Keeping original.")
        return None

    specialized = Fact(
        noun=fact.noun,
        instance=instance,
        property=fact.property,
        operator=fact.operator,
        value=fact.value,
    )
    action = input(
        f"     → {specialized.to_display()}  [confirm/reject] (c/r): "
    ).strip().lower()

    if action == "c":
        specialized.status = "confirmed"
        return specialized

    specialized.status = "rejected"
    return specialized


def _confirm_rules(rules: list[Rule]) -> list[Rule]:
    """Interactive CLI confirmation of proposed rules.

    Actions: c=confirm, e=edit (BECAUSE clause), r=reject
    """
    confirmed: list[Rule] = []

    print("\nProposed rules:")
    for i, rule in enumerate(rules, 1):
        conditions_str = _format_rule_conditions(rule)
        then_str = f"{rule.then.noun}({rule.then.instance}).{rule.then.property} = {rule.then.value}"
        print(f"  {i}. IF {conditions_str} THEN {then_str}")
        print(f"     BECAUSE: {rule.because}")

        action = input("     [confirm/edit/reject] (c/e/r): ").strip().lower()
        if action == "c":
            confirmed.append(rule)
        elif action == "e":
            new_because = input("     Enter updated BECAUSE clause: ").strip()
            if new_because:
                rule.because = new_because
            confirmed.append(rule)
        # action == "r" or anything else: skip

    return confirmed


def _format_rule_conditions(rule: Rule) -> str:
    """Format rule conditions for display."""
    parts = []
    for item in rule.conditions.items:
        parts.append(f"{item.noun}({item.instance}).{item.property} {item.operator} {item.value}")
    joiner = f" {rule.conditions.logic} "
    return joiner.join(parts)


def _confirm_root_cause(proposed: str | None) -> str | None:
    """Confirm root cause (c/e/r only — root causes are not parameterized)."""
    if not proposed:
        return None

    action = input(
        f"\nProposed root cause: \"{proposed}\"  [confirm/edit/reject] (c/e/r): "
    ).strip().lower()

    if action == "c":
        return proposed
    elif action == "e":
        edited = input("  Enter root cause name: ").strip()
        return edited if edited else None
    else:
        return None


def process_incident(incident_path: str, data_dir: str) -> None:
    """Main workflow: load incident → extract → confirm → persist."""
    data_path = Path(data_dir)

    # Ensure data directories exist
    (data_path / "incidents").mkdir(parents=True, exist_ok=True)
    (data_path / "rules").mkdir(parents=True, exist_ok=True)

    store = YamlStore(data_path)
    loader = IncidentLoader()

    # Step 1: Load incident
    print(f"Loading incident from: {incident_path}")
    text = loader.load(Path(incident_path))

    incident_id = store.next_incident_id()
    print(f"Incident ID: {incident_id}")

    # Step 2: Extract facts via LLM
    print("\nExtracting facts via LLM...")
    extractor = FactExtractor()
    ontology_nouns = store.load_ontology()
    llm_response = extractor.extract(text, ontology_nouns)

    # Step 3: Check for empty response
    if not llm_response.facts:
        print("No facts extracted from incident. No changes made.")
        return

    # Step 4: Confirm facts
    all_facts = _confirm_facts(llm_response.facts)
    confirmed_facts = [f for f in all_facts if f.status == "confirmed"]

    if not confirmed_facts:
        print("\nAll facts rejected. No rules generated.")
        # Still save incident with rejected facts
        incident = Incident(
            incident_id=incident_id,
            source_text=text,
            facts=all_facts,
            root_cause_identified=None,
        )
        store.save_incident(incident)
        print("Incident saved (all facts rejected).")
        return

    # Step 5: Confirm root cause
    root_cause = _confirm_root_cause(llm_response.root_cause)

    # Step 6: Confirm rules
    existing_rules = store.list_rules()
    gen = RuleGenerator(existing_rules)
    filtered_rules = gen.filter_rules(llm_response.rules, confirmed_facts)

    confirmed_rules: list[Rule] = []
    if filtered_rules:
        confirmed_rules = _confirm_rules(filtered_rules)

    # Step 7: Update ontology
    ontology_mgr = OntologyManager(ontology_nouns)
    added = ontology_mgr.update_from_facts(confirmed_facts)

    if added:
        print("\nOntology updates:")
        for noun, prop in added:
            print(f"  + {noun}.{prop} (new)")

    # Step 8: Assign rule IDs and persist
    # Save incident
    incident = Incident(
        incident_id=incident_id,
        source_text=text,
        facts=all_facts,
        root_cause_identified=root_cause,
    )
    store.save_incident(incident)

    # Save rules
    for rule in confirmed_rules:
        rule.rule_id = store.next_rule_id()
        rule.sources = [incident_id]
        store.save_rule(rule)

    # Update ontology
    if ontology_mgr.has_changes():
        store.save_ontology(ontology_mgr.get_nouns())

    # Update root causes
    if root_cause:
        existing_rcs = store.load_root_causes()
        rc_names = {rc.name.lower() for rc in existing_rcs}
        if root_cause.lower() not in rc_names:
            existing_rcs.append(RootCause(name=root_cause))
        store.save_root_causes(existing_rcs)

    # Step 9: Print summary
    confirmed_count = len(confirmed_facts)
    rejected_count = len([f for f in all_facts if f.status == "rejected"])
    print(f"\nGenerated rules:")
    for rule in confirmed_rules:
        cond_str = _format_rule_conditions(rule)
        then_str = f"{rule.then.noun}({rule.then.instance}).{rule.then.property} = {rule.then.value}"
        print(f"  {rule.rule_id}: IF {cond_str} THEN {then_str}")

    print(f"\nSummary:")
    print(f"  Facts: {len(all_facts)} proposed → {confirmed_count} confirmed, {rejected_count} rejected")
    print(f"  Ontology: {len(added)} new entries")
    print(f"  Rules: {len(confirmed_rules)} generated")
    print(f"\nAll files saved.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ees",
        description="Expert System — extract troubleshooting rules from incidents",
    )
    subparsers = parser.add_subparsers(dest="command")

    process_parser = subparsers.add_parser("process", help="Process an incident file")
    process_parser.add_argument(
        "--incident", required=True, help="Path to the incident text file"
    )
    process_parser.add_argument(
        "--data-dir",
        default="data",
        help="Path to the data directory (default: data)",
    )

    args = parser.parse_args()

    if args.command == "process":
        try:
            process_incident(args.incident, args.data_dir)
        except (IncidentLoadError, ConfigError, LLMError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
