"""Adapter functions — convert engine models to GUI display-ready data.

These are pure Python functions with no Tkinter dependency,
making them fully testable without a GUI event loop.
"""
from __future__ import annotations

from ees.models import EvaluationResult, Fact, OntologyNoun, Rule, RuleOutput


def facts_to_rows(facts: list[Fact]) -> list[dict]:
    """Convert Fact objects to display-ready row dicts.

    Each row: {noun, instance, property, operator, value, status, scope, display}
    """
    return [
        {
            "noun": f.noun,
            "instance": f.instance,
            "property": f.property,
            "operator": f.operator,
            "value": f.value,
            "status": f.status,
            "scope": f.scope,
            "display": f.to_display(),
        }
        for f in facts
    ]


def _then_display(then: RuleOutput | object) -> str:
    """Format a rule's then/else branch for display.

    Handles both v2 RuleOutput and v1 RuleThen objects.
    """
    if isinstance(then, RuleOutput):
        return f'{then.kind}("{then.description}")'
    # v1 backward compat
    return getattr(then, "value", str(then))


def rules_to_rows(rules: list[Rule]) -> list[dict]:
    """Convert Rule objects to display-ready row dicts.

    Each row: {rule_id, status, type, conditions, then, else, because, sources}
    """
    rows = []
    for r in rules:
        # Format conditions as readable string
        parts = []
        for item in r.conditions.items:
            parts.append(f"{item.noun}({item.instance}).{item.property} "
                         f"{item.operator} {item.value}")
        joiner = f" {r.conditions.logic} "
        conditions_str = joiner.join(parts)

        # Format then/else using v2-aware helper
        then_str = _then_display(r.then)
        else_str = _then_display(r.else_) if r.else_ else ""

        rows.append({
            "rule_id": r.rule_id,
            "status": r.status,
            "type": r.type,
            "conditions": conditions_str,
            "then": then_str,
            "else": else_str,
            "because": r.because,
            "sources": r.sources,
        })
    return rows


def ontology_to_tree(nouns: list[OntologyNoun]) -> list[dict]:
    """Convert OntologyNoun objects to tree-ready dicts.

    Each entry: {noun, properties: [{name, type}]}
    """
    tree = []
    for noun in nouns:
        tree.append({
            "noun": noun.name,
            "properties": [
                {"name": p.name, "type": p.type}
                for p in noun.properties
            ],
        })
    return tree


def eval_result_to_display(result: EvaluationResult) -> dict:
    """Convert EvaluationResult to a display-ready dict.

    Keys: input_facts, fired_rules, outputs, root_causes, ruled_out, gap_rules, trace
    """
    return {
        "input_facts": [f.to_display() for f in result.input_facts],
        "fired_rules": [
            {
                "rule_id": r.rule_id,
                "conditions": " AND ".join(
                    item.to_display() for item in r.conditions.items
                ),
                "then": _then_display(r.then),
                "type": r.type,
            }
            for r in result.fired_rules
        ],
        "outputs": [
            {
                "rule_id": o["rule_id"],
                "branch": o["branch"],
                "kind": o["output"].kind,
                "description": o["output"].description,
            }
            for o in result.outputs
        ],
        # Backward-compat keys (derived from outputs)
        "root_causes": list(result.root_causes),
        "ruled_out": list(result.ruled_out),
        "gap_rules": [
            {
                "rule_id": g.rule_id,
                "requires": ", ".join(f.to_display() for f in g.requires),
                "note": g.note,
            }
            for g in result.gap_rules
        ],
        "trace": result.rule_trace,
    }


def filter_rules(
    rules: list[Rule],
    status: str | None = None,
    rule_type: str | None = None,
) -> list[Rule]:
    """Filter rules by status and/or type."""
    result = rules
    if status is not None:
        result = [r for r in result if r.status == status]
    if rule_type is not None:
        result = [r for r in result if r.type == rule_type]
    return result
