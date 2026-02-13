"""Tests for YAML persistence layer."""
import os
import pytest
from pathlib import Path

from ees.yaml_store import YamlStore
from ees.models import (
    Fact, Incident, Rule, RuleConditions, RuleThen,
    OntologyNoun, OntologyProperty, RootCause,
)


@pytest.fixture
def data_dir(tmp_path):
    """Create a temporary data directory structure."""
    (tmp_path / "incidents").mkdir()
    (tmp_path / "rules").mkdir()
    return tmp_path


@pytest.fixture
def store(data_dir):
    return YamlStore(data_dir)


class TestYamlStoreIncidents:
    """TC-11, TC-12: Incident YAML persistence."""

    def test_save_and_load_incident(self, store, data_dir):
        """TC-11: Incident YAML contains source text and confirmed facts."""
        inc = Incident(
            incident_id="INC-001",
            source_text="Some incident text",
            facts=[
                Fact("Server", "*", "CPUUsage", ">", "90", status="confirmed"),
            ],
            root_cause_identified="Resource Exhaustion",
            processed_at="2026-02-12T10:00:00",
        )
        store.save_incident(inc)

        path = data_dir / "incidents" / "INC-001.yaml"
        assert path.exists()

        loaded = store.load_incident("INC-001")
        assert loaded.incident_id == "INC-001"
        assert loaded.source_text == "Some incident text"
        assert len(loaded.facts) == 1
        assert loaded.facts[0].status == "confirmed"
        assert loaded.root_cause_identified == "Resource Exhaustion"

    def test_rejected_facts_recorded(self, store):
        """TC-12: Rejected facts are recorded in incident YAML."""
        inc = Incident(
            incident_id="INC-002",
            source_text="text",
            facts=[
                Fact("Server", "*", "CPUUsage", ">", "90", status="confirmed"),
                Fact("Network", "*", "Latency", ">", "100ms", status="rejected"),
            ],
        )
        store.save_incident(inc)
        loaded = store.load_incident("INC-002")
        statuses = [f.status for f in loaded.facts]
        assert "confirmed" in statuses
        assert "rejected" in statuses


class TestYamlStoreRules:
    """TC-16, TC-23: Rule YAML persistence."""

    def test_save_and_load_rule(self, store, data_dir):
        """TC-16 partial + TC-23: Rule YAML is valid and loadable."""
        rule = Rule(
            rule_id="R-001",
            status="CONFIRMED",
            type="positive",
            sources=["INC-001"],
            conditions=RuleConditions(
                logic="AND",
                items=[Fact("Server", "*", "CPUUsage", ">", "90")],
            ),
            then=RuleThen("Server", "*", "ResourceExhausted", "TRUE"),
            because="High CPU indicates exhaustion",
        )
        store.save_rule(rule)

        path = data_dir / "rules" / "R-001.yaml"
        assert path.exists()

        loaded = store.load_rule("R-001")
        assert loaded.rule_id == "R-001"
        assert loaded.status == "CONFIRMED"
        assert loaded.because == "High CPU indicates exhaustion"
        assert len(loaded.conditions.items) == 1

    def test_list_rules(self, store):
        """List all existing rules."""
        store.save_rule(Rule(rule_id="R-001", because="a"))
        store.save_rule(Rule(rule_id="R-002", because="b"))
        rules = store.list_rules()
        ids = [r.rule_id for r in rules]
        assert "R-001" in ids
        assert "R-002" in ids


class TestYamlStoreOntology:
    """TC-13, TC-23: Ontology YAML persistence."""

    def test_save_and_load_ontology(self, store):
        nouns = [
            OntologyNoun("Server", [OntologyProperty("CPUUsage", "numeric")]),
        ]
        store.save_ontology(nouns)
        loaded = store.load_ontology()
        assert len(loaded) == 1
        assert loaded[0].name == "Server"
        assert loaded[0].properties[0].name == "CPUUsage"

    def test_empty_ontology(self, store):
        """Load ontology when file doesn't exist yet."""
        loaded = store.load_ontology()
        assert loaded == []


class TestYamlStoreRootCauses:
    """TC-20, TC-23: Root cause YAML persistence."""

    def test_save_and_load_root_causes(self, store):
        rcs = [RootCause("Resource Exhaustion", None)]
        store.save_root_causes(rcs)
        loaded = store.load_root_causes()
        assert len(loaded) == 1
        assert loaded[0].name == "Resource Exhaustion"

    def test_empty_root_causes(self, store):
        loaded = store.load_root_causes()
        assert loaded == []


class TestYamlStoreIDGeneration:
    """ID generation via file scanning."""

    def test_next_incident_id_empty(self, store):
        assert store.next_incident_id() == "INC-001"

    def test_next_incident_id_existing(self, store):
        inc = Incident(incident_id="INC-001", source_text="t")
        store.save_incident(inc)
        assert store.next_incident_id() == "INC-002"

    def test_next_incident_id_multiple(self, store):
        for i in range(1, 4):
            store.save_incident(Incident(incident_id=f"INC-{i:03d}", source_text="t"))
        assert store.next_incident_id() == "INC-004"

    def test_next_rule_id_empty(self, store):
        assert store.next_rule_id() == "R-001"

    def test_next_rule_id_existing(self, store):
        store.save_rule(Rule(rule_id="R-001"))
        assert store.next_rule_id() == "R-002"


class TestYamlStoreFileErrors:
    """TC-24: File error handling."""

    def test_write_to_nonexistent_dir(self, tmp_path):
        """TC-24: Error when target directory doesn't exist."""
        data_dir = tmp_path / "nonexistent"
        # Don't create incidents/rules subdirectories
        store = YamlStore(data_dir)

        inc = Incident(incident_id="INC-001", source_text="t")
        with pytest.raises((OSError, FileNotFoundError)):
            store.save_incident(inc)


class TestYamlValidity:
    """TC-23: All output files are valid YAML."""

    def test_all_outputs_valid_yaml(self, store):
        """All saved files can be re-loaded without parse errors."""
        import ruamel.yaml

        inc = Incident(
            incident_id="INC-001",
            source_text="text",
            facts=[Fact("S", "*", "P", ">", "1")],
            root_cause_identified="RC",
        )
        store.save_incident(inc)

        rule = Rule(
            rule_id="R-001",
            sources=["INC-001"],
            conditions=RuleConditions("AND", [Fact("S", "*", "P", ">", "1")]),
            then=RuleThen("S", "*", "X", "TRUE"),
            because="reason",
        )
        store.save_rule(rule)

        store.save_ontology([OntologyNoun("S", [OntologyProperty("P", "numeric")])])
        store.save_root_causes([RootCause("RC")])

        yaml = ruamel.yaml.YAML()

        # Verify all files parse
        for f in store.data_dir.rglob("*.yaml"):
            with open(f) as fh:
                data = yaml.load(fh)
                assert data is not None
