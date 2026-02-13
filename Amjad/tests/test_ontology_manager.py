"""Tests for ontology manager."""
import pytest

from ees.ontology_manager import OntologyManager
from ees.models import Fact, OntologyNoun, OntologyProperty


class TestOntologyManagerNewEntries:
    """TC-13, TC-15: Adding new noun/property entries."""

    def test_new_noun_and_property(self):
        """TC-13: New Noun.Property added to ontology."""
        mgr = OntologyManager([])
        fact = Fact("Server", "*", "CPUUsage", ">", "90")
        added = mgr.update_from_facts([fact])
        assert len(added) == 1
        assert added[0] == ("Server", "CPUUsage")

        nouns = mgr.get_nouns()
        assert len(nouns) == 1
        assert nouns[0].name == "Server"
        assert nouns[0].has_property("CPUUsage")

    def test_multiple_properties_same_noun(self):
        """TC-15: Multiple new properties on same noun."""
        mgr = OntologyManager([
            OntologyNoun("Server", [OntologyProperty("CPUUsage", "numeric")]),
        ])
        facts = [
            Fact("Server", "*", "MemoryFree", "<", "5%"),
            Fact("Server", "*", "DiskIO", ">", "80%"),
        ]
        added = mgr.update_from_facts(facts)
        assert ("Server", "MemoryFree") in added
        assert ("Server", "DiskIO") in added

        nouns = mgr.get_nouns()
        assert len(nouns) == 1  # still one noun
        assert len(nouns[0].properties) == 3  # three properties now


class TestOntologyManagerExisting:
    """TC-14, TC-27: Reusing existing entries."""

    def test_existing_reused_case_insensitive(self):
        """TC-14: Existing Noun.Property reused (case-insensitive)."""
        mgr = OntologyManager([
            OntologyNoun("Server", [OntologyProperty("CPUUsage", "numeric")]),
        ])
        fact = Fact("server", "*", "cpuusage", ">", "95")
        added = mgr.update_from_facts([fact])
        assert len(added) == 0  # nothing new

        nouns = mgr.get_nouns()
        assert len(nouns) == 1
        assert len(nouns[0].properties) == 1

    def test_no_changes_no_updates(self):
        """TC-27: No new entries means ontology unchanged."""
        original = [
            OntologyNoun("Server", [OntologyProperty("CPUUsage", "numeric")]),
        ]
        mgr = OntologyManager(original)
        fact = Fact("Server", "*", "CPUUsage", ">", "90")
        added = mgr.update_from_facts([fact])
        assert len(added) == 0
        assert not mgr.has_changes()


class TestOntologyManagerMixedNouns:
    """TC-28: Second incident with overlapping and new entries."""

    def test_mixed_existing_and_new(self):
        """TC-28 partial: Existing entries reused, new ones added."""
        mgr = OntologyManager([
            OntologyNoun("Server", [OntologyProperty("CPUUsage", "numeric")]),
        ])
        facts = [
            Fact("Server", "*", "CPUUsage", ">", "90"),   # existing
            Fact("Server", "*", "MemoryFree", "<", "5%"),  # new prop
            Fact("App", "*", "ResponseTime", ">", "10s"),  # new noun
        ]
        added = mgr.update_from_facts(facts)
        assert ("Server", "MemoryFree") in added
        assert ("App", "ResponseTime") in added
        assert ("Server", "CPUUsage") not in added

        nouns = mgr.get_nouns()
        noun_names = [n.name for n in nouns]
        assert "Server" in noun_names
        assert "App" in noun_names


class TestOntologyManagerLookup:
    """Ontology lookup helpers."""

    def test_find_noun_case_insensitive(self):
        mgr = OntologyManager([
            OntologyNoun("Server", [OntologyProperty("CPUUsage")]),
        ])
        assert mgr.find_noun("server") is not None
        assert mgr.find_noun("SERVER") is not None
        assert mgr.find_noun("Unknown") is None

    def test_confirmed_facts_only(self):
        """Only confirmed facts update ontology."""
        mgr = OntologyManager([])
        facts = [
            Fact("Server", "*", "CPUUsage", ">", "90", status="confirmed"),
            Fact("Network", "*", "Latency", ">", "100ms", status="rejected"),
        ]
        added = mgr.update_from_facts([f for f in facts if f.status == "confirmed"])
        noun_names = [n.name for n in mgr.get_nouns()]
        assert "Server" in noun_names
        assert "Network" not in noun_names
