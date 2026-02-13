"""Ontology manager — maintains Noun.Property registry with case-insensitive matching."""
from __future__ import annotations

from ees.models import Fact, OntologyNoun, OntologyProperty


class OntologyManager:
    """Manages the ontology: lookup, matching, and updates from confirmed facts."""

    def __init__(self, nouns: list[OntologyNoun]) -> None:
        self._nouns = list(nouns)
        self._changed = False

    def get_nouns(self) -> list[OntologyNoun]:
        """Return current ontology nouns."""
        return list(self._nouns)

    def has_changes(self) -> bool:
        """Whether ontology was modified since construction."""
        return self._changed

    def find_noun(self, name: str) -> OntologyNoun | None:
        """Find a noun by name (case-insensitive)."""
        for noun in self._nouns:
            if noun.name.lower() == name.lower():
                return noun
        return None

    def update_from_facts(self, facts: list[Fact]) -> list[tuple[str, str]]:
        """Update ontology from confirmed facts. Returns list of (noun, property) pairs added.

        Only processes facts — caller should filter to confirmed-only before calling.
        """
        added: list[tuple[str, str]] = []

        for fact in facts:
            noun = self.find_noun(fact.noun)
            if noun is None:
                # New noun
                prop = OntologyProperty(name=fact.property)
                noun = OntologyNoun(name=fact.noun, properties=[prop])
                self._nouns.append(noun)
                self._changed = True
                added.append((fact.noun, fact.property))
            elif not noun.has_property(fact.property):
                # Existing noun, new property
                noun.properties.append(OntologyProperty(name=fact.property))
                self._changed = True
                added.append((noun.name, fact.property))
            # else: existing noun and property — no change

        return added
