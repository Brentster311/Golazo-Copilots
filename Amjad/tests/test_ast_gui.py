"""Tests for the AST-based GUI adapters (EES-00019 Phase 4).

TC-21: rules_to_rows produces display dicts for AST rules
TC-22: rules_to_rows handles empty rule (block with no statements)
"""
from __future__ import annotations

from ees.gui.adapters import ast_rules_to_rows
from ees.models import (
    AssertStmt,
    Block,
    CheckExpr,
    DecideStmt,
    GapStmt,
    NoopStmt,
    RuleBlock,
    parse_rule,
)


# ── TC-21: rules_to_rows produces display dicts for AST rules ─────────


class TestASTRulesToRows:
    """TC-21: rules_to_rows must produce display-ready dicts for new AST rules."""

    def test_check_decide_assert_display(self):
        rule = parse_rule({
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
                        "else": [{"gap": "Admin role unknown"}],
                    },
                }
            ],
        })
        rows = ast_rules_to_rows([rule])
        assert len(rows) == 1
        row = rows[0]
        assert row["rule_id"] == "R-001"
        assert "summary" in row, "Row must have a 'summary' key"
        assert len(row["summary"]) > 0, "Summary must not be empty"
        # Summary should mention key concepts
        assert "CHECK" in row["summary"] or "DECIDE" in row["summary"], \
            "Summary should mention CHECK or DECIDE keywords"

    def test_multiple_rules(self):
        r1 = parse_rule({
            "rule_id": "R-001",
            "block": [{"act": "escalate"}],
        })
        r2 = parse_rule({
            "rule_id": "R-002",
            "block": [{"noop": True}],
        })
        rows = ast_rules_to_rows([r1, r2])
        assert len(rows) == 2
        assert rows[0]["rule_id"] == "R-001"
        assert rows[1]["rule_id"] == "R-002"


# ── TC-22: rules_to_rows handles empty rule ───────────────────────────


class TestASTRulesToRowsEmpty:
    """TC-22: Empty rules should display gracefully without error."""

    def test_empty_block(self):
        rule = RuleBlock(rule_id="R-EMPTY", block=Block(stmts=[]))
        rows = ast_rules_to_rows([rule])
        assert len(rows) == 1
        row = rows[0]
        assert row["rule_id"] == "R-EMPTY"
        assert "(empty rule)" in row["summary"].lower() or row["summary"] == "(empty rule)"
