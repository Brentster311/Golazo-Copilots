"""YAML persistence layer — atomic read/write for all data files."""
from __future__ import annotations

import re
from pathlib import Path

from ruamel.yaml import YAML

from ees.models import (
    Fact,
    Incident,
    OntologyNoun,
    OntologyProperty,
    RootCause,
    Rule,
    RuleConditions,
    RuleThen,
)


class YamlStore:
    """Handles all YAML file I/O for incidents, rules, ontology, and root causes."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self._yaml = YAML()
        self._yaml.default_flow_style = False

    # ── Incidents ──────────────────────────────────────────────

    def save_incident(self, incident: Incident) -> Path:
        """Save an incident to incidents/<id>.yaml."""
        path = self.data_dir / "incidents" / f"{incident.incident_id}.yaml"
        data = incident.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            self._yaml.dump(data, f)
        return path

    def load_incident(self, incident_id: str) -> Incident:
        """Load an incident by ID."""
        path = self.data_dir / "incidents" / f"{incident_id}.yaml"
        with open(path, encoding="utf-8") as f:
            data = self._yaml.load(f)
        return Incident.from_dict(data)

    # ── Rules ──────────────────────────────────────────────────

    def save_rule(self, rule: Rule) -> Path:
        """Save a rule to rules/<id>.yaml."""
        path = self.data_dir / "rules" / f"{rule.rule_id}.yaml"
        data = rule.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            self._yaml.dump(data, f)
        return path

    def load_rule(self, rule_id: str) -> Rule:
        """Load a rule by ID."""
        path = self.data_dir / "rules" / f"{rule_id}.yaml"
        with open(path, encoding="utf-8") as f:
            data = self._yaml.load(f)
        return Rule.from_dict(data)

    def list_rules(self) -> list[Rule]:
        """Load all existing rules."""
        rules_dir = self.data_dir / "rules"
        rules = []
        if rules_dir.exists():
            for path in sorted(rules_dir.glob("*.yaml")):
                with open(path, encoding="utf-8") as f:
                    data = self._yaml.load(f)
                if data:
                    rules.append(Rule.from_dict(data))
        return rules

    # ── Ontology ───────────────────────────────────────────────

    def save_ontology(self, nouns: list[OntologyNoun]) -> Path:
        """Save the ontology to ontology.yaml."""
        path = self.data_dir / "ontology.yaml"
        data = {"nouns": [n.to_dict() for n in nouns]}
        with open(path, "w", encoding="utf-8") as f:
            self._yaml.dump(data, f)
        return path

    def load_ontology(self) -> list[OntologyNoun]:
        """Load the ontology. Returns empty list if file doesn't exist."""
        path = self.data_dir / "ontology.yaml"
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            data = self._yaml.load(f)
        if not data or "nouns" not in data:
            return []
        return [OntologyNoun.from_dict(n) for n in data["nouns"]]

    # ── Root Causes ────────────────────────────────────────────

    def save_root_causes(self, root_causes: list[RootCause]) -> Path:
        """Save root causes to rootcauses.yaml."""
        path = self.data_dir / "rootcauses.yaml"
        data = {"root_causes": [rc.to_dict() for rc in root_causes]}
        with open(path, "w", encoding="utf-8") as f:
            self._yaml.dump(data, f)
        return path

    def load_root_causes(self) -> list[RootCause]:
        """Load root causes. Returns empty list if file doesn't exist."""
        path = self.data_dir / "rootcauses.yaml"
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            data = self._yaml.load(f)
        if not data or "root_causes" not in data:
            return []
        return [RootCause.from_dict(rc) for rc in data["root_causes"]]

    # ── ID Generation ──────────────────────────────────────────

    def next_incident_id(self) -> str:
        """Generate next sequential incident ID by scanning existing files."""
        return self._next_id(self.data_dir / "incidents", "INC")

    def next_rule_id(self) -> str:
        """Generate next sequential rule ID by scanning existing files."""
        return self._next_id(self.data_dir / "rules", "R")

    def _next_id(self, directory: Path, prefix: str) -> str:
        """Scan directory for highest numbered file and return next ID."""
        max_num = 0
        pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)\.yaml$")
        if directory.exists():
            for path in directory.iterdir():
                m = pattern.match(path.name)
                if m:
                    num = int(m.group(1))
                    max_num = max(max_num, num)
        next_num = max_num + 1
        return f"{prefix}-{next_num:03d}"
