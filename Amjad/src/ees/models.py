"""Data models for the Expert System."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


# Valid operators for fact expressions
VALID_OPERATORS = ("==", "!=", ">", "<", ">=", "<=", "contains", "!contains")

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
        """Serialize to dict for YAML output (includes status)."""
        d = self.to_condition_dict()
        d["status"] = self.status
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
class RuleThen:
    """The THEN clause of a rule."""
    noun: str
    instance: str
    property: str
    value: str

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
    """A troubleshooting rule: IF conditions THEN conclusion BECAUSE reason.

    For CONFIRMED rules: uses conditions/then.
    For GAP rules: uses requires/produces/note (conditions/then left at defaults).
    """
    rule_id: str
    status: Literal["CONFIRMED", "GAP", "RESOLVED"] = "CONFIRMED"
    type: Literal["positive"] = "positive"
    sources: list[str] = field(default_factory=list)
    conditions: RuleConditions = field(default_factory=lambda: RuleConditions(logic="AND"))
    then: RuleThen = field(default_factory=lambda: RuleThen("", "*", "", ""))
    because: str = ""
    # GAP-specific fields
    requires: list[Fact] = field(default_factory=list)
    produces: list[Fact] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        d = {
            "rule_id": self.rule_id,
            "status": self.status,
            "type": self.type,
            "sources": self.sources,
            "conditions": self.conditions.to_dict(),
            "then": self.then.to_dict(),
            "because": self.because,
        }
        if self.requires:
            d["requires"] = [f.to_condition_dict() for f in self.requires]
        if self.produces:
            d["produces"] = [f.to_condition_dict() for f in self.produces]
        if self.note:
            d["note"] = self.note
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Rule:
        return cls(
            rule_id=d["rule_id"],
            status=d.get("status", "CONFIRMED"),
            type=d.get("type", "positive"),
            sources=d.get("sources", []),
            conditions=RuleConditions.from_dict(d["conditions"]),
            then=RuleThen.from_dict(d["then"]),
            because=d.get("because", ""),
            requires=[Fact.from_dict(f) for f in d.get("requires", [])],
            produces=[Fact.from_dict(f) for f in d.get("produces", [])],
            note=d.get("note", ""),
        )

    def is_duplicate_of(self, other: Rule) -> bool:
        """Check exact duplicate: same conditions and same then clause."""
        return (
            self.conditions.to_dict() == other.conditions.to_dict()
            and self.then.to_dict() == other.then.to_dict()
        )


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
    """Parsed response from LLM containing facts, rules, and root cause."""
    facts: list[Fact] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    root_cause: str | None = None
