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


# ============================================================================
# EES-00016: OntologyProperty typed validation
# ============================================================================


class TestOntologyPropertyValidateValue:
    """TC-16-01 through TC-16-16: OntologyProperty.validate_value()."""

    # ---- Enum ----

    def test_enum_valid(self):
        """TC-16-01: Valid enum value."""
        prop = OntologyProperty("role", "enum", values=["admin", "user", "none"], default="none")
        assert prop.validate_value("admin") is True

    def test_enum_invalid(self):
        """TC-16-02: Invalid enum value."""
        prop = OntologyProperty("role", "enum", values=["admin", "user", "none"], default="none")
        assert prop.validate_value("superadmin") is False

    def test_enum_empty_values(self):
        """TC-16-03: Empty enum values list rejects everything."""
        prop = OntologyProperty("role", "enum", values=[], default=None)
        assert prop.validate_value("anything") is False

    def test_enum_case_sensitive(self):
        """TC-16-04: Enum matching is case-sensitive."""
        prop = OntologyProperty("role", "enum", values=["Admin"], default=None)
        assert prop.validate_value("admin") is False

    # ---- Bool ----

    def test_bool_true(self):
        """TC-16-05: Bool accepts 'true'."""
        prop = OntologyProperty("active", "bool")
        assert prop.validate_value("true") is True

    def test_bool_false(self):
        """TC-16-06: Bool accepts 'false'."""
        prop = OntologyProperty("active", "bool")
        assert prop.validate_value("false") is True

    def test_bool_capitalized_invalid(self):
        """TC-16-07: Bool rejects 'True'."""
        prop = OntologyProperty("active", "bool")
        assert prop.validate_value("True") is False

    def test_bool_yes_invalid(self):
        """TC-16-08: Bool rejects 'yes'."""
        prop = OntologyProperty("active", "bool")
        assert prop.validate_value("yes") is False

    # ---- Long ----

    def test_long_positive(self):
        """TC-16-09: Long accepts positive integers."""
        prop = OntologyProperty("count", "long")
        assert prop.validate_value("42") is True

    def test_long_negative(self):
        """TC-16-10: Long accepts negative integers."""
        prop = OntologyProperty("count", "long")
        assert prop.validate_value("-1") is True

    def test_long_zero(self):
        """TC-16-11: Long accepts zero."""
        prop = OntologyProperty("count", "long")
        assert prop.validate_value("0") is True

    def test_long_float_invalid(self):
        """TC-16-12: Long rejects floats."""
        prop = OntologyProperty("count", "long")
        assert prop.validate_value("3.14") is False

    def test_long_text_invalid(self):
        """TC-16-13: Long rejects text."""
        prop = OntologyProperty("count", "long")
        assert prop.validate_value("abc") is False

    # ---- Invalid / removed types ----

    def test_string_type_rejected(self):
        """TC-16-14: String type no longer supported — rejects values."""
        prop = OntologyProperty("desc", "string")
        assert prop.validate_value("anything at all") is False

    def test_string_type_rejects_empty(self):
        """TC-16-15: String type rejects even empty string."""
        prop = OntologyProperty("desc", "string")
        assert prop.validate_value("") is False

    # ---- Unknown type ----

    def test_unknown_type_rejected(self):
        """TC-16-16: Unknown type returns False."""
        prop = OntologyProperty("x", "float")
        assert prop.validate_value("3.14") is False


class TestOntologyPropertySerialization:
    """TC-16-17 through TC-16-21: OntologyProperty serialization."""

    def test_to_dict_includes_new_fields(self):
        """TC-16-17: to_dict includes values and default."""
        prop = OntologyProperty("role", "enum", values=["admin", "user"], default="user")
        d = prop.to_dict()
        assert d == {"name": "role", "type": "enum", "values": ["admin", "user"], "default": "user"}

    def test_from_dict_all_fields(self):
        """TC-16-18: from_dict with all fields."""
        d = {"name": "role", "type": "enum", "values": ["admin"], "default": "admin"}
        prop = OntologyProperty.from_dict(d)
        assert prop.values == ["admin"]
        assert prop.default == "admin"

    def test_from_dict_backward_compat_no_values(self):
        """TC-16-19: from_dict with explicit type preserves it even if unsupported."""
        d = {"name": "role", "type": "string"}
        prop = OntologyProperty.from_dict(d)
        assert prop.type == "string"  # preserved but will fail validate_value
        assert prop.values == []
        assert prop.default is None

    def test_from_dict_backward_compat_minimal(self):
        """TC-16-20: from_dict with only name defaults to enum."""
        d = {"name": "x"}
        prop = OntologyProperty.from_dict(d)
        assert prop.type == "enum"
        assert prop.values == []
        assert prop.default is None

    def test_round_trip(self):
        """TC-16-21: Serialization round trip."""
        prop = OntologyProperty("role", "enum", values=["admin", "user"], default="user")
        assert OntologyProperty.from_dict(prop.to_dict()).to_dict() == prop.to_dict()


class TestOntologyManagerValidateFact:
    """TC-16-22 through TC-16-27: OntologyManager.validate_fact()."""

    def _make_manager(self):
        return OntologyManager([
            OntologyNoun("User", [
                OntologyProperty("directoryRole", "enum",
                                 values=["admin", "user", "none"], default="none"),
            ]),
        ])

    def test_valid_fact(self):
        """TC-16-22: Valid fact returns no errors."""
        mgr = self._make_manager()
        fact = Fact("User", "$u", "directoryRole", "==", "admin")
        assert mgr.validate_fact(fact) == []

    def test_unknown_noun(self):
        """TC-16-23: Unknown noun returns error."""
        mgr = self._make_manager()
        fact = Fact("Server", "*", "cpu", "==", "90")
        errors = mgr.validate_fact(fact)
        assert len(errors) == 1
        assert "Server" in errors[0]

    def test_unknown_property(self):
        """TC-16-24: Known noun, unknown property returns error."""
        mgr = self._make_manager()
        fact = Fact("User", "*", "email", "==", "foo@bar.com")
        errors = mgr.validate_fact(fact)
        assert len(errors) == 1
        assert "email" in errors[0]

    def test_invalid_value(self):
        """TC-16-25: Invalid value returns error."""
        mgr = self._make_manager()
        fact = Fact("User", "$u", "directoryRole", "==", "superadmin")
        errors = mgr.validate_fact(fact)
        assert len(errors) == 1
        assert "superadmin" in errors[0]

    def test_case_insensitive_noun_lookup(self):
        """TC-16-26: Noun lookup is case-insensitive."""
        mgr = self._make_manager()
        fact = Fact("user", "*", "directoryRole", "==", "admin")
        assert mgr.validate_fact(fact) == []

    def test_chaining_facts_skip_validation(self):
        """TC-16-27: RULED_OUT/CHANGE_STATE/GAP pseudo-nouns skip validation."""
        mgr = self._make_manager()
        fact = Fact("RULED_OUT", "*", "User.directoryRole", "==", "true")
        assert mgr.validate_fact(fact) == []


# ============================================================================
# EES-00018: OntologyProperty goal fields
# ============================================================================


class TestOntologyPropertyGoalFields:
    """TC-18-01 through TC-18-07: OntologyProperty goal annotations."""

    def test_goal_annotations(self):
        """TC-18-01: OntologyProperty with goal annotations."""
        prop = OntologyProperty(
            "rootCause", "enum",
            values=["unknown", "admin_role_missing", "token_expired"],
            default="unknown",
            is_goal=True,
            initial="unknown",
            terminal=["admin_role_missing", "token_expired"],
        )
        assert prop.is_goal is True
        assert prop.initial == "unknown"
        assert prop.terminal == ["admin_role_missing", "token_expired"]

    def test_goal_defaults(self):
        """TC-18-02: OntologyProperty goal field defaults."""
        prop = OntologyProperty("status", "enum")
        assert prop.is_goal is False
        assert prop.initial is None
        assert prop.terminal == []

    def test_to_dict_includes_goal_fields(self):
        """TC-18-03: to_dict includes goal fields when set."""
        prop = OntologyProperty(
            "rootCause", "enum",
            values=["unknown", "admin_role_missing", "token_expired"],
            default="unknown",
            is_goal=True,
            initial="unknown",
            terminal=["admin_role_missing", "token_expired"],
        )
        d = prop.to_dict()
        assert d["is_goal"] is True
        assert d["initial"] == "unknown"
        assert d["terminal"] == ["admin_role_missing", "token_expired"]

    def test_to_dict_omits_goal_fields_when_default(self):
        """TC-18-04: to_dict omits goal fields when default."""
        prop = OntologyProperty("status", "enum")
        d = prop.to_dict()
        assert "is_goal" not in d
        assert "initial" not in d
        assert "terminal" not in d

    def test_from_dict_with_goal_fields(self):
        """TC-18-05: from_dict with goal fields."""
        d = {
            "name": "rootCause", "type": "enum",
            "values": ["unknown", "admin_role_missing"],
            "is_goal": True, "initial": "unknown",
            "terminal": ["admin_role_missing"],
        }
        prop = OntologyProperty.from_dict(d)
        assert prop.is_goal is True
        assert prop.initial == "unknown"
        assert prop.terminal == ["admin_role_missing"]

    def test_from_dict_without_goal_fields(self):
        """TC-18-06: from_dict without goal fields (backward compat)."""
        d = {"name": "status", "type": "enum"}
        prop = OntologyProperty.from_dict(d)
        assert prop.is_goal is False
        assert prop.initial is None
        assert prop.terminal == []

    def test_round_trip_with_goal_fields(self):
        """TC-18-07: Round-trip with goal fields."""
        prop = OntologyProperty(
            "rootCause", "enum",
            values=["unknown", "admin_role_missing", "token_expired"],
            default="unknown",
            is_goal=True,
            initial="unknown",
            terminal=["admin_role_missing", "token_expired"],
        )
        prop2 = OntologyProperty.from_dict(prop.to_dict())
        assert prop2.is_goal == prop.is_goal
        assert prop2.initial == prop.initial
        assert prop2.terminal == prop.terminal
        assert prop2.to_dict() == prop.to_dict()
