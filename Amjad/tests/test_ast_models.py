"""Tests for the AST model and parser (EES-00019).

TDD RED phase: These tests define the expected behavior of the new
expert system language AST. They should all FAIL before production
code is written.
"""
from __future__ import annotations

import pytest

from ees.exceptions import ParseError
from ees.models import (
    ActStmt,
    AssertStmt,
    Block,
    CheckExpr,
    DecideStmt,
    Fact,
    GapStmt,
    NoopStmt,
    RetractStmt,
    RuleBlock,
    parse_rule,
)


# ── TC-01: Parse valid rule with CHECK/DECIDE/ASSERT ──────────────────


class TestParseCheckDecideAssert:
    """TC-01: Valid rule with CHECK/DECIDE/ASSERT parses correctly."""

    def test_parse_valid_check_decide_assert(self):
        data = {
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
                        "else": [
                            {
                                "gap": "Admin role could not be confirmed"
                            }
                        ],
                    },
                }
            ],
        }
        rule = parse_rule(data)
        assert isinstance(rule, RuleBlock)
        assert rule.rule_id == "R-001"
        assert len(rule.block.stmts) == 1

        stmt = rule.block.stmts[0]
        assert isinstance(stmt, DecideStmt)
        assert stmt.check.noun == "User"
        assert stmt.check.instance == "$u"
        assert stmt.check.property == "adminRole"
        assert stmt.check.operator == "=="
        assert stmt.check.value == "unknown"

        # then block has ASSERT
        assert len(stmt.then_block.stmts) == 1
        assert isinstance(stmt.then_block.stmts[0], AssertStmt)
        assert stmt.then_block.stmts[0].noun == "User"
        assert stmt.then_block.stmts[0].value == "confirmed"

        # else block has GAP
        assert len(stmt.else_block.stmts) == 1
        assert isinstance(stmt.else_block.stmts[0], GapStmt)
        assert stmt.else_block.stmts[0].description == "Admin role could not be confirmed"


# ── TC-02: Parse nested DECIDE ────────────────────────────────────────


class TestParseNestedDecide:
    """TC-02: Nested DECIDE blocks parse correctly."""

    def test_nested_decide(self):
        data = {
            "rule_id": "R-002",
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
                        "then": [
                            {
                                "check": {
                                    "noun": "Tenant",
                                    "instance": "*",
                                    "property": "globalAdmin",
                                    "operator": "==",
                                    "value": "true",
                                },
                                "decide": {
                                    "then": [
                                        {
                                            "assert": {
                                                "noun": "User",
                                                "instance": "*",
                                                "property": "adminRole",
                                                "operator": "==",
                                                "value": "confirmed",
                                            }
                                        }
                                    ],
                                    "else": [{"noop": True}],
                                },
                            }
                        ],
                        "else": [{"noop": True}],
                    },
                }
            ],
        }
        rule = parse_rule(data)
        outer = rule.block.stmts[0]
        assert isinstance(outer, DecideStmt)
        inner = outer.then_block.stmts[0]
        assert isinstance(inner, DecideStmt)
        assert inner.check.noun == "Tenant"
        assert isinstance(inner.then_block.stmts[0], AssertStmt)
        assert isinstance(inner.else_block.stmts[0], NoopStmt)


# ── TC-03: Parse RETRACT ──────────────────────────────────────────────


class TestParseRetract:
    """TC-03: RETRACT statement parses correctly."""

    def test_parse_retract(self):
        data = {
            "rule_id": "R-003",
            "block": [
                {
                    "retract": {
                        "noun": "User",
                        "instance": "$u",
                        "property": "adminRole",
                    }
                }
            ],
        }
        rule = parse_rule(data)
        stmt = rule.block.stmts[0]
        assert isinstance(stmt, RetractStmt)
        assert stmt.noun == "User"
        assert stmt.instance == "$u"
        assert stmt.property == "adminRole"


# ── TC-04: Parse ACT and NOOP ─────────────────────────────────────────


class TestParseActNoop:
    """TC-04: ACT and NOOP statements parse correctly."""

    def test_parse_act_and_noop(self):
        data = {
            "rule_id": "R-004",
            "block": [
                {"act": "escalate to Exchange team"},
                {"noop": True},
            ],
        }
        rule = parse_rule(data)
        assert len(rule.block.stmts) == 2
        assert isinstance(rule.block.stmts[0], ActStmt)
        assert rule.block.stmts[0].description == "escalate to Exchange team"
        assert isinstance(rule.block.stmts[1], NoopStmt)


# ── TC-05: Reject unknown keyword ─────────────────────────────────────


class TestRejectUnknownKeyword:
    """TC-05: Unknown keywords are rejected with descriptive error."""

    def test_reject_invoke(self):
        data = {
            "rule_id": "R-005",
            "block": [
                {"invoke": {"target": "something"}}
            ],
        }
        with pytest.raises(ParseError, match="Unknown keyword.*invoke"):
            parse_rule(data)

    def test_reject_execute(self):
        data = {
            "rule_id": "R-006",
            "block": [
                {"execute": "run something"}
            ],
        }
        with pytest.raises(ParseError, match="Unknown keyword.*execute"):
            parse_rule(data)


# ── TC-06: Reject DECIDE with wrong number of blocks ──────────────────


class TestRejectDecideMissingElse:
    """TC-06: DECIDE with missing else block is rejected."""

    def test_decide_missing_else(self):
        data = {
            "rule_id": "R-007",
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
                        # missing "else"
                    },
                }
            ],
        }
        with pytest.raises(ParseError, match="DECIDE requires.*2 blocks|else"):
            parse_rule(data)


# ── TC-07: Reject DECIDE without CHECK ─────────────────────────────────


class TestRejectDecideWithoutCheck:
    """TC-07: DECIDE without a CHECK expression is rejected."""

    def test_decide_without_check(self):
        data = {
            "rule_id": "R-008",
            "block": [
                {
                    "decide": {
                        "then": [{"noop": True}],
                        "else": [{"noop": True}],
                    }
                }
            ],
        }
        with pytest.raises(ParseError, match="DECIDE requires a CHECK"):
            parse_rule(data)


# ── TC-23: YAML round-trip ────────────────────────────────────────────


class TestYamlRoundTrip:
    """TC-23: Serialize and deserialize preserves AST structure."""

    def test_round_trip_complex_rule(self):
        data = {
            "rule_id": "R-RT-001",
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
                            },
                            {"act": "notify admin"},
                        ],
                        "else": [
                            {
                                "retract": {
                                    "noun": "User",
                                    "instance": "$u",
                                    "property": "adminRole",
                                }
                            },
                            {"gap": "Admin role unknown"},
                        ],
                    },
                },
                {"noop": True},
            ],
        }
        rule = parse_rule(data)
        serialized = rule.to_dict()
        rule2 = parse_rule(serialized)
        assert rule.to_dict() == rule2.to_dict(), "YAML round-trip must preserve all AST structure"


# ── TC-24: Round-trip preserves variables ──────────────────────────────


class TestRoundTripVariables:
    """TC-24: Variable tokens survive round-trip."""

    def test_variables_preserved(self):
        data = {
            "rule_id": "R-VAR-001",
            "block": [
                {
                    "check": {
                        "noun": "Permission",
                        "instance": "$p",
                        "property": "mailAPI",
                        "operator": "==",
                        "value": "required",
                    },
                    "decide": {
                        "then": [
                            {
                                "assert": {
                                    "noun": "Permission",
                                    "instance": "$p",
                                    "property": "mailAPI",
                                    "operator": "==",
                                    "value": "granted",
                                }
                            }
                        ],
                        "else": [{"noop": True}],
                    },
                }
            ],
        }
        rule = parse_rule(data)
        serialized = rule.to_dict()
        # Verify variables are present in serialized form
        check_data = serialized["block"][0]["check"]
        assert check_data["instance"] == "$p", "Variable token must survive round-trip"
        assert_data = serialized["block"][0]["decide"]["then"][0]["assert"]
        assert assert_data["instance"] == "$p", "Variable token must survive round-trip in ASSERT"
