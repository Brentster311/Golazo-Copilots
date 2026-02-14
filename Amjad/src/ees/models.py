"""Data models for the Expert System."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


# Valid operators for fact expressions
VALID_OPERATORS = ("==", "!=", ">", "<", ">=", "<=", "contains", "!contains")

# Valid output entity kinds for v2 rule grammar
VALID_OUTPUT_KINDS = ("CHANGE_STATE", "RULED_OUT", "GAP")

# Regex for parsing a fact string: Noun(instance).Property operator value
FACT_PATTERN = re.compile(
    r"^([A-Za-z_]\w*)"          # noun name
    r"\(([^)]+)\)"              # (instance)
    r"\.([A-Za-z_]\w*)"         # .Property
    r"\s+"                      # whitespace
    r"(==|!=|>=|<=|>|<|contains|!contains)"  # operator
    r"\s+"                      # whitespace
    r"(.+)$"                    # value (rest of string)
)


@dataclass
class Fact:
    """A single extracted fact: Noun(instance).Property operator value."""
    noun: str
    instance: str          # "*" = generalized
    property: str
    operator: str
    value: str
    status: Literal["confirmed", "rejected"] = "confirmed"
    scope: Literal["rule", "context"] = "rule"

    # ------ variable helpers (EES-00009) ------

    @staticmethod
    def is_variable(text: str) -> bool:
        """Return True if *text* is a variable token (starts with '$' + name)."""
        return len(text) >= 2 and text.startswith("$")

    @property
    def has_variable_instance(self) -> bool:
        return self.is_variable(self.instance)

    @property
    def has_variable_value(self) -> bool:
        return self.is_variable(self.value)

    @property
    def has_variables(self) -> bool:
        return self.has_variable_instance or self.has_variable_value

    # ------ display / matching ------

    def to_display(self) -> str:
        """Format as human-readable string: Noun(instance).Property operator value."""
        return f"{self.noun}({self.instance}).{self.property} {self.operator} {self.value}"

    def match_key(self) -> tuple[str, str, str, str, str]:
        """Return a normalized key for case-insensitive matching (noun/property lowered)."""
        return (self.noun.lower(), self.instance, self.property.lower(), self.operator, self.value)

    @classmethod
    def parse(cls, text: str) -> Fact | None:
        """Parse a fact string. Returns None if invalid format."""
        m = FACT_PATTERN.match(text.strip())
        if not m:
            return None
        noun, instance, prop, op, val = m.groups()
        if op not in VALID_OPERATORS:
            return None
        return cls(noun=noun, instance=instance, property=prop, operator=op, value=val.strip())

    def to_condition_dict(self) -> dict:
        """Serialize to dict without status — used for rule conditions, requires, produces."""
        return {
            "noun": self.noun,
            "instance": self.instance,
            "property": self.property,
            "operator": self.operator,
            "value": self.value,
        }

    def to_dict(self) -> dict:
        """Serialize to dict for YAML output (includes status and scope)."""
        d = self.to_condition_dict()
        d["status"] = self.status
        d["scope"] = self.scope
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Fact:
        """Deserialize from dict."""
        return cls(
            noun=d["noun"],
            instance=d["instance"],
            property=d["property"],
            operator=d["operator"],
            value=d["value"],
            status=d.get("status", "confirmed"),
            scope=d.get("scope", "rule"),
        )


@dataclass
class RuleConditions:
    """Conditions block for a rule: flat AND or flat OR."""
    logic: Literal["AND", "OR"]
    items: list[Fact] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "logic": self.logic,
            "items": [f.to_condition_dict() for f in self.items],
        }

    @classmethod
    def from_dict(cls, d: dict) -> RuleConditions:
        items = [Fact.from_dict(it) for it in d.get("items", [])]
        return cls(logic=d["logic"], items=items)


@dataclass
class RuleOutput:
    """Output entity for a rule branch (THEN or ELSE).

    kind: CHANGE_STATE | RULED_OUT | GAP
    description: free-text describing the state change, elimination, or gap.
    """
    kind: Literal["CHANGE_STATE", "RULED_OUT", "GAP"]
    description: str

    def to_dict(self) -> dict:
        return {"kind": self.kind, "description": self.description}

    @classmethod
    def from_dict(cls, d: dict) -> RuleOutput:
        return cls(kind=d["kind"], description=d["description"])

    def to_fact(self) -> Fact:
        """Convert this output to a Fact for working-set matching.

        CHANGE_STATE("X") -> Fact(noun="CHANGE_STATE", instance="*",
                                  property="description", operator="==", value="X")
        """
        return Fact(
            noun=self.kind,
            instance="*",
            property="description",
            operator="==",
            value=self.description,
        )


# Backward-compat alias — old code that imports RuleThen still works at import time.
# RuleThen is deprecated; new code should use RuleOutput.
class RuleThen:
    """DEPRECATED — use RuleOutput. Kept for import compatibility during migration."""
    def __init__(self, noun: str, instance: str, property: str, value: str):
        self.noun = noun
        self.instance = instance
        self.property = property
        self.value = value

    def to_dict(self) -> dict:
        return {
            "noun": self.noun,
            "instance": self.instance,
            "property": self.property,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> RuleThen:
        return cls(
            noun=d["noun"],
            instance=d["instance"],
            property=d["property"],
            value=d["value"],
        )


@dataclass
class Rule:
    """A troubleshooting rule using v2 grammar.

    IF <conditions> THEN CHANGE_STATE|RULED_OUT|GAP [ELSE CHANGE_STATE|RULED_OUT|GAP]
    """
    rule_id: str
    status: Literal["CONFIRMED", "GAP", "RESOLVED"] = "CONFIRMED"
    sources: list[str] = field(default_factory=list)
    conditions: RuleConditions = field(default_factory=lambda: RuleConditions(logic="AND"))
    then: RuleOutput = field(default_factory=lambda: RuleOutput("CHANGE_STATE", ""))
    else_: RuleOutput | None = None

    # ── deprecated v1 fields (kept for backward compat until EES-00011/12) ──
    type: str = "positive"
    requires: list[Fact] = field(default_factory=list)
    produces: list[Fact] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        d: dict = {
            "rule_id": self.rule_id,
            "status": self.status,
            "sources": self.sources,
            "conditions": self.conditions.to_dict(),
            "then": self.then.to_dict(),
        }
        if self.else_ is not None:
            d["else"] = self.else_.to_dict()
        # Deprecated v1 fields — serialize for backward compat
        if self.type != "positive":
            d["type"] = self.type
        if self.requires:
            d["requires"] = [f.to_condition_dict() for f in self.requires]
        if self.produces:
            d["produces"] = [f.to_condition_dict() for f in self.produces]
        if self.note:
            d["note"] = self.note
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Rule:
        else_data = d.get("else")
        # Handle v1 then format (RuleThen dict) vs v2 (RuleOutput dict)
        then_data = d.get("then", {})
        if "kind" in then_data:
            then = RuleOutput.from_dict(then_data)
        else:
            # v1 format: {"noun": ..., "instance": ..., "property": ..., "value": ...}
            then = RuleOutput(kind="CHANGE_STATE", description=then_data.get("value", ""))
        return cls(
            rule_id=d["rule_id"],
            status=d.get("status", "CONFIRMED"),
            sources=d.get("sources", []),
            conditions=RuleConditions.from_dict(d["conditions"]),
            then=then,
            else_=RuleOutput.from_dict(else_data) if else_data else None,
            type=d.get("type", "positive"),
            requires=[Fact.from_dict(f) for f in d.get("requires", [])],
            produces=[Fact.from_dict(f) for f in d.get("produces", [])],
            note=d.get("note", ""),
        )

    def is_duplicate_of(self, other: Rule) -> bool:
        """Check exact duplicate: same conditions, same then, same else."""
        if self.conditions.to_dict() != other.conditions.to_dict():
            return False
        if self.then.to_dict() != other.then.to_dict():
            return False
        self_else = self.else_.to_dict() if self.else_ else None
        other_else = other.else_.to_dict() if other.else_ else None
        return self_else == other_else


@dataclass
class Incident:
    """A processed incident with extracted facts."""
    incident_id: str
    source_text: str
    facts: list[Fact] = field(default_factory=list)
    root_cause_identified: str | None = None
    processed_at: str = ""

    def __post_init__(self):
        if not self.processed_at:
            self.processed_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "source_text": self.source_text,
            "facts": [f.to_dict() for f in self.facts],
            "root_cause_identified": self.root_cause_identified,
            "processed_at": self.processed_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Incident:
        return cls(
            incident_id=d["incident_id"],
            source_text=d["source_text"],
            facts=[Fact.from_dict(f) for f in d.get("facts", [])],
            root_cause_identified=d.get("root_cause_identified"),
            processed_at=d.get("processed_at", ""),
        )


@dataclass
class OntologyProperty:
    """A single property within a noun."""
    name: str
    type: str = "string"

    def to_dict(self) -> dict:
        return {"name": self.name, "type": self.type}

    @classmethod
    def from_dict(cls, d: dict) -> OntologyProperty:
        return cls(name=d["name"], type=d.get("type", "string"))


@dataclass
class OntologyNoun:
    """A noun with its properties in the ontology."""
    name: str
    properties: list[OntologyProperty] = field(default_factory=list)

    def has_property(self, prop_name: str) -> bool:
        """Case-insensitive property lookup."""
        return any(p.name.lower() == prop_name.lower() for p in self.properties)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "properties": [p.to_dict() for p in self.properties],
        }

    @classmethod
    def from_dict(cls, d: dict) -> OntologyNoun:
        return cls(
            name=d["name"],
            properties=[OntologyProperty.from_dict(p) for p in d.get("properties", [])],
        )


@dataclass
class RootCause:
    """A root cause entity."""
    name: str
    action_plan: str | None = None

    def to_dict(self) -> dict:
        return {"name": self.name, "action_plan": self.action_plan}

    @classmethod
    def from_dict(cls, d: dict) -> RootCause:
        return cls(name=d["name"], action_plan=d.get("action_plan"))


@dataclass
class GapRefinement:
    """Result of checking a GAP rule against new rules."""
    gap_rule_id: str
    action: Literal["narrowed", "resolved"]
    updated_rule: Rule


@dataclass
class LLMResponse:
    """Parsed response from LLM containing facts and rules."""
    facts: list[Fact] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Result of evaluating rules against input facts."""
    input_facts: list[Fact]
    derived_facts: list[Fact]
    fired_rules: list[Rule]         # In firing order
    outputs: list[dict]             # [{rule_id, branch, output: RuleOutput}]
    rule_trace: list[dict]          # [{rule_id, iteration, branch, derived}]

    # ── convenience properties ──

    @property
    def change_states(self) -> list[str]:
        """Descriptions of all CHANGE_STATE outputs."""
        return [o["output"].description for o in self.outputs if o["output"].kind == "CHANGE_STATE"]

    @property
    def ruled_outs(self) -> list[str]:
        """Descriptions of all RULED_OUT outputs."""
        return [o["output"].description for o in self.outputs if o["output"].kind == "RULED_OUT"]

    @property
    def gaps(self) -> list[str]:
        """Descriptions of all GAP outputs."""
        return [o["output"].description for o in self.outputs if o["output"].kind == "GAP"]

    # ── backward-compat properties (used by GUI/CLI until EES-00012) ──

    @property
    def root_causes(self) -> list[str]:
        """DEPRECATED — returns change_states for backward compat."""
        return self.change_states

    @property
    def ruled_out(self) -> list[str]:
        """DEPRECATED — returns ruled_outs for backward compat."""
        return self.ruled_outs

    @property
    def gap_rules(self) -> list[Rule]:
        """DEPRECATED — returns fired rules that produced GAP outputs."""
        gap_rule_ids = {o["rule_id"] for o in self.outputs if o["output"].kind == "GAP"}
        return [r for r in self.fired_rules if r.rule_id in gap_rule_ids]

    def to_dict(self) -> dict:
        return {
            "input_facts": [f.to_condition_dict() for f in self.input_facts],
            "derived_facts": [f.to_condition_dict() for f in self.derived_facts],
            "fired_rules": [r.to_dict() for r in self.fired_rules],
            "outputs": [
                {"rule_id": o["rule_id"], "branch": o["branch"],
                 "kind": o["output"].kind, "description": o["output"].description}
                for o in self.outputs
            ],
            "rule_trace": list(self.rule_trace),
            # Backward-compat keys (used by main.py CLI until EES-00012)
            "root_causes": self.root_causes,
            "ruled_out": self.ruled_out,
        }
