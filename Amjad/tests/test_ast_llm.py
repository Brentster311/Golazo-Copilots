"""Tests for the AST-based LLM integration (EES-00019 Phase 3).

TC-17: submit_rule accepts valid AST
TC-18: submit_rule rejects unknown keyword
TC-19: submit_rule rejects DECIDE with one block
TC-20: get_ontology includes types and values
"""
from __future__ import annotations

import json

import pytest

from ees.fact_extractor import FactExtractor
from ees.models import (
    Fact,
    OntologyNoun,
    OntologyProperty,
    RuleBlock,
)


# ── TC-17: submit_rule accepts valid AST ──────────────────────────────


class TestSubmitRuleAcceptsValidAST:
    """TC-17: submit_rule should accept structurally valid AST rules."""

    def test_valid_check_decide_assert(self):
        args = {
            "rule_id": "R-001",
            "block": [
                {
                    "check": {
                        "noun": "User",
                        "instance": "$u",
                        "property": "adminRole",
                        "operator": "==",
                        "value": "unknown",
                    },
                    "decide": {
                        "then": [
                            {
                                "assert": {
                                    "noun": "User",
                                    "instance": "$u",
                                    "property": "adminRole",
                                    "operator": "==",
                                    "value": "confirmed",
                                }
                            }
                        ],
                        "else": [{"gap": "Admin role could not be confirmed"}],
                    },
                }
            ],
        }
        collected: list[RuleBlock] = []
        result_str, accepted = FactExtractor._handle_submit_rule_ast(
            args, collected,
        )
        assert accepted, f"submit_rule should accept valid AST: {result_str}"
        assert len(collected) == 1
        assert collected[0].rule_id == "R-001"


# ── TC-18: submit_rule rejects unknown keyword ────────────────────────


class TestSubmitRuleRejectsUnknownKeyword:
    """TC-18: submit_rule should reject rules with unknown keywords."""

    def test_reject_invoke(self):
        args = {
            "rule_id": "R-BAD",
            "block": [{"invoke": {"target": "something"}}],
        }
        collected: list[RuleBlock] = []
        result_str, accepted = FactExtractor._handle_submit_rule_ast(
            args, collected,
        )
        assert not accepted, "submit_rule should reject unknown keyword"
        assert "Unknown keyword" in result_str


# ── TC-19: submit_rule rejects DECIDE with one block ──────────────────


class TestSubmitRuleRejectsIncompleteDecide:
    """TC-19: submit_rule should reject structurally invalid DECIDE."""

    def test_decide_missing_else(self):
        args = {
            "rule_id": "R-BAD2",
            "block": [
                {
                    "check": {
                        "noun": "User",
                        "instance": "*",
                        "property": "adminRole",
                        "operator": "==",
                        "value": "unknown",
                    },
                    "decide": {
                        "then": [{"noop": True}],
                        # missing else
                    },
                }
            ],
        }
        collected: list[RuleBlock] = []
        result_str, accepted = FactExtractor._handle_submit_rule_ast(
            args, collected,
        )
        assert not accepted, "submit_rule should reject DECIDE without else"
        assert "else" in result_str.lower() or "2 blocks" in result_str.lower()


# ── TC-20: get_ontology includes types and values ─────────────────────


class TestGetOntologyIncludesTypesAndValues:
    """TC-20: get_ontology must include property types and legal values."""

    def test_ontology_with_enum_property(self):
        ontology = [
            OntologyNoun(
                name="User",
                properties=[
                    OntologyProperty(
                        name="adminRole",
                        type="enum",
                        values=["unknown", "confirmed", "denied"],
                    ),
                ],
            ),
        ]
        result_str = FactExtractor._handle_get_ontology(ontology)
        data = json.loads(result_str)

        nouns = data["nouns"]
        assert len(nouns) == 1
        user = nouns[0]
        assert user["name"] == "User"

        props = user["properties"]
        assert len(props) == 1
        admin_role = props[0]
        assert admin_role["name"] == "adminRole"
        assert admin_role["type"] == "enum"
        assert admin_role["values"] == ["unknown", "confirmed", "denied"]

    def test_ontology_with_goal_annotations(self):
        ontology = [
            OntologyNoun(
                name="Incident",
                properties=[
                    OntologyProperty(
                        name="rootCause",
                        type="enum",
                        values=["unknown", "admin_role_missing", "permission_missing"],
                        is_goal=True,
                        initial="unknown",
                        terminal=["admin_role_missing", "permission_missing"],
                    ),
                ],
            ),
        ]
        result_str = FactExtractor._handle_get_ontology(ontology)
        data = json.loads(result_str)

        prop = data["nouns"][0]["properties"][0]
        assert prop["is_goal"] is True
        assert prop["initial"] == "unknown"
        assert prop["terminal"] == ["admin_role_missing", "permission_missing"]
