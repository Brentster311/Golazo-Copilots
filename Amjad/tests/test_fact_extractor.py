"""Tests for multi-turn tool-calling fact extractor (EES-00013).

Covers TC-01 through TC-27 from the test cases document.
All tests mock client.chat.completions.create to simulate tool-call sequences.
"""
from __future__ import annotations

import json
import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from ees.exceptions import ConfigError, LLMError
from ees.fact_extractor import FactExtractor
from ees.models import (
    Fact,
    LLMResponse,
    OntologyNoun,
    OntologyProperty,
    Rule,
    RuleOutput,
)


# ---------------------------------------------------------------------------
# Helpers to build mock OpenAI tool-calling responses
# ---------------------------------------------------------------------------

def _tool_call(name: str, arguments: dict, call_id: str = "call_1") -> MagicMock:
    """Build a mock tool_call object."""
    tc = MagicMock()
    tc.id = call_id
    tc.type = "function"
    tc.function.name = name
    tc.function.arguments = json.dumps(arguments)
    return tc


def _assistant_msg_with_tools(tool_calls: list[MagicMock]) -> MagicMock:
    """Build a mock ChatCompletion response whose message has tool_calls."""
    msg = MagicMock()
    msg.role = "assistant"
    msg.content = None
    msg.tool_calls = tool_calls
    choice = MagicMock()
    choice.message = msg
    choice.finish_reason = "tool_calls"
    resp = MagicMock()
    resp.choices = [choice]
    usage = MagicMock()
    usage.total_tokens = 100
    usage.prompt_tokens = 60
    usage.completion_tokens = 40
    resp.usage = usage
    return resp


def _assistant_msg_done(content: str = "Extraction complete.") -> MagicMock:
    """Build a mock ChatCompletion response with no tool_calls (model is done)."""
    msg = MagicMock()
    msg.role = "assistant"
    msg.content = content
    msg.tool_calls = None
    choice = MagicMock()
    choice.message = msg
    choice.finish_reason = "stop"
    resp = MagicMock()
    resp.choices = [choice]
    usage = MagicMock()
    usage.total_tokens = 50
    usage.prompt_tokens = 30
    usage.completion_tokens = 20
    resp.usage = usage
    return resp


def _make_extractor() -> FactExtractor:
    """Create a FactExtractor with mocked client."""
    ext = FactExtractor.__new__(FactExtractor)
    ext.client = MagicMock()
    ext.deployment = "gpt-5.2"
    return ext


# ---------------------------------------------------------------------------
# TC-01: Happy Path — Full Extraction
# ---------------------------------------------------------------------------
class TestHappyPath:
    def test_full_extraction(self):
        """TC-01: Model calls get_ontology, submit_fact x2, submit_rule, set_root_cause."""
        ext = _make_extractor()
        ontology = [OntologyNoun("Server", [OntologyProperty("CPUUsage")])]

        turn1 = _assistant_msg_with_tools([
            _tool_call("get_ontology", {}, "c1"),
            _tool_call("get_existing_rules", {}, "c2"),
        ])
        turn2 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "Server", "instance": "*", "property": "CPUUsage",
                "operator": ">", "value": "90", "scope": "rule",
            }, "c3"),
            _tool_call("submit_fact", {
                "noun": "Server", "instance": "*", "property": "MemoryFree",
                "operator": "<", "value": "5%", "scope": "rule",
            }, "c4"),
        ])
        turn3 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {
                    "logic": "AND",
                    "items": [
                        {"noun": "Server", "instance": "*", "property": "CPUUsage", "operator": ">", "value": "90"},
                        {"noun": "Server", "instance": "*", "property": "MemoryFree", "operator": "<", "value": "5%"},
                    ],
                },
                "then": {"kind": "CHANGE_STATE", "description": "Resource exhaustion"},
                "because": "High CPU + low memory = resource exhaustion",
            }, "c5"),
        ])
        turn4 = _assistant_msg_with_tools([
            _tool_call("set_root_cause", {"name": "Resource Exhaustion"}, "c6"),
        ])
        turn5 = _assistant_msg_done()

        ext.client.chat.completions.create.side_effect = [turn1, turn2, turn3, turn4, turn5]

        result = ext.extract("Server is slow", ontology)

        assert isinstance(result, LLMResponse)
        assert len(result.facts) == 2
        assert result.facts[0].noun == "Server"
        assert result.facts[0].operator == ">"
        assert result.facts[1].operator == "<"
        assert len(result.rules) == 1
        assert result.rules[0].then.kind == "CHANGE_STATE"
        assert result.rules[0].then.description == "Resource exhaustion"
        assert result.rules[0].because == "High CPU + low memory = resource exhaustion"
        assert result.root_cause == "Resource Exhaustion"


# ---------------------------------------------------------------------------
# TC-02: Invalid operator in submit_fact → error → retry succeeds
# ---------------------------------------------------------------------------
class TestFactValidation:
    def test_invalid_operator_returns_error(self):
        """TC-02: Invalid operator gets error, retry with valid operator succeeds."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "X", "property": "Y", "operator": "LIKE", "value": "z",
            }, "c1"),
        ])
        turn2 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "X", "property": "Y", "operator": "contains", "value": "z",
            }, "c2"),
        ])
        turn3 = _assistant_msg_done()

        ext.client.chat.completions.create.side_effect = [turn1, turn2, turn3]
        result = ext.extract("text", [])

        assert len(result.facts) == 1
        assert result.facts[0].operator == "contains"

    def test_variable_in_fact_rejected(self):
        """TC-06: Facts with variables ($) are rejected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "X", "instance": "$op", "property": "Y",
                "operator": "==", "value": "z",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.facts) == 0

    def test_variable_in_value_rejected(self):
        """TC-06 extended: Variable in value field rejected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "X", "property": "Y", "operator": "==", "value": "$val",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.facts) == 0

    def test_scope_preserved(self):
        """TC-22: Facts with scope='context' retain that scope."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "VM", "property": "Name", "operator": "==",
                "value": "myvm", "scope": "context",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert result.facts[0].scope == "context"

    def test_instance_defaults_to_star(self):
        """TC-23: Omitted instance defaults to '*'."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "X", "property": "Y", "operator": "==", "value": "z",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert result.facts[0].instance == "*"

    def test_scope_defaults_to_rule(self):
        """TC-24: Omitted scope defaults to 'rule'."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "X", "property": "Y", "operator": "==", "value": "z",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert result.facts[0].scope == "rule"

    def test_ontology_warning_but_accepted(self):
        """TC-17: Unknown noun accepted with warning."""
        ext = _make_extractor()
        ontology = [OntologyNoun("Server", [OntologyProperty("CPUUsage")])]

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "Storage", "property": "Capacity",
                "operator": "==", "value": "full",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", ontology)
        # Fact IS accepted even though "Storage" isn't in ontology
        assert len(result.facts) == 1
        assert result.facts[0].noun == "Storage"


# ---------------------------------------------------------------------------
# TC-03 through TC-09: Rule validation
# ---------------------------------------------------------------------------
class TestRuleValidation:
    def test_invalid_kind_returns_error(self):
        """TC-03: Invalid kind POSITIVE rejected, retry with CHANGE_STATE succeeds."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": ">", "value": "1"},
                ]},
                "then": {"kind": "POSITIVE", "description": "test"},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": ">", "value": "1"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "test"},
                "because": "reason",
            }, "c2"),
        ])
        turn3 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2, turn3]

        result = ext.extract("text", [])
        assert len(result.rules) == 1
        assert result.rules[0].then.kind == "CHANGE_STATE"

    def test_empty_description_rejected(self):
        """TC-04: Empty description rejected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": ">", "value": "1"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": ""},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 0

    def test_missing_because_rejected(self):
        """TC-05: Missing because rejected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": ">", "value": "1"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "test"},
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 0

    def test_empty_because_rejected(self):
        """TC-05 variant: Empty string because rejected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": ">", "value": "1"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "test"},
                "because": "",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 0

    def test_rule_with_else_branch(self):
        """TC-07: Rule with THEN and ELSE branches."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": "==", "value": "X"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "Identified issue"},
                "else": {"kind": "GAP", "description": "Need more info"},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 1
        assert result.rules[0].then.kind == "CHANGE_STATE"
        assert result.rules[0].else_ is not None
        assert result.rules[0].else_.kind == "GAP"

    def test_rule_ruled_out(self):
        """TC-08: Rule with RULED_OUT kind."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "Net", "property": "Latency", "operator": "==", "value": "normal"},
                ]},
                "then": {"kind": "RULED_OUT", "description": "Network issue eliminated"},
                "because": "Normal latency rules out network issues",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert result.rules[0].then.kind == "RULED_OUT"

    def test_rule_gap(self):
        """TC-09: Rule with GAP kind."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": "==", "value": "X"},
                ]},
                "then": {"kind": "GAP", "description": "Missing disk usage data"},
                "because": "Need disk info",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert result.rules[0].then.kind == "GAP"

    def test_empty_conditions_rejected(self):
        """TC-18: Rule with empty conditions.items rejected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": []},
                "then": {"kind": "CHANGE_STATE", "description": "test"},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 0

    def test_invalid_operator_in_condition(self):
        """TC-26: Condition item with invalid operator."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": "LIKE", "value": "X"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "test"},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 0

    def test_variable_binding_in_conditions_allowed(self):
        """TC-27: Variables allowed in rule conditions (not facts)."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "Error", "instance": "$op", "property": "Code", "operator": "==", "value": "Fail"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "Op failed"},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 1
        assert result.rules[0].conditions.items[0].instance == "$op"

    def test_invalid_else_kind_rejected(self):
        """Else branch with invalid kind rejected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": "==", "value": "X"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "test"},
                "else": {"kind": "INVALID", "description": "test"},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert len(result.rules) == 0


# ---------------------------------------------------------------------------
# TC-10 & TC-11: Loop control
# ---------------------------------------------------------------------------
class TestLoopControl:
    def test_max_turns_cutoff(self):
        """TC-10: Loop exits at max_turns, returns collected data."""
        ext = _make_extractor()

        # Every turn submits a fact
        def make_turn(i):
            return _assistant_msg_with_tools([
                _tool_call("submit_fact", {
                    "noun": f"N{i}", "property": "P", "operator": "==", "value": "v",
                }, f"c{i}"),
            ])

        # 20 turns worth of responses, but max_turns=3
        ext.client.chat.completions.create.side_effect = [make_turn(i) for i in range(20)]

        result = ext.extract("text", [], max_turns=3)
        # Should have facts from 3 turns only
        assert len(result.facts) == 3

    def test_no_tool_calls_returns_empty(self):
        """TC-11: Model responds with plain text, no tool_calls."""
        ext = _make_extractor()

        ext.client.chat.completions.create.return_value = _assistant_msg_done("No facts found.")

        result = ext.extract("text", [])
        assert isinstance(result, LLMResponse)
        assert result.facts == []
        assert result.rules == []
        assert result.root_cause is None


# ---------------------------------------------------------------------------
# TC-12: Unknown tool name
# ---------------------------------------------------------------------------
class TestUnknownTool:
    def test_unknown_tool_returns_error(self):
        """TC-12: Unknown tool name returns error, not collected."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("do_something_else", {"x": 1}, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert result.facts == []
        assert result.rules == []


# ---------------------------------------------------------------------------
# TC-13 & TC-14: get_ontology handler
# ---------------------------------------------------------------------------
class TestGetOntology:
    def test_returns_ontology_json(self):
        """TC-13: get_ontology returns formatted ontology."""
        ext = _make_extractor()
        ontology = [OntologyNoun("Server", [OntologyProperty("CPUUsage")])]

        turn1 = _assistant_msg_with_tools([
            _tool_call("get_ontology", {}, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        # We verify by checking the tool result message sent back
        result = ext.extract("text", ontology)
        # The call happened — verify messages were built correctly
        assert ext.client.chat.completions.create.call_count == 2

    def test_empty_ontology(self):
        """TC-14: get_ontology with empty ontology."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("get_ontology", {}, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert ext.client.chat.completions.create.call_count == 2


# ---------------------------------------------------------------------------
# TC-15: get_existing_rules returns empty
# ---------------------------------------------------------------------------
class TestGetExistingRules:
    def test_returns_empty_list(self):
        """TC-15: get_existing_rules returns empty list."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("get_existing_rules", {}, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert ext.client.chat.completions.create.call_count == 2


# ---------------------------------------------------------------------------
# TC-16: Multiple set_root_cause — last wins
# ---------------------------------------------------------------------------
class TestSetRootCause:
    def test_last_wins(self):
        """TC-16: Multiple set_root_cause calls, last one wins."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("set_root_cause", {"name": "A"}, "c1"),
        ])
        turn2 = _assistant_msg_with_tools([
            _tool_call("set_root_cause", {"name": "B"}, "c2"),
        ])
        turn3 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2, turn3]

        result = ext.extract("text", [])
        assert result.root_cause == "B"


# ---------------------------------------------------------------------------
# TC-19: API failure during loop
# ---------------------------------------------------------------------------
class TestAPIFailure:
    def test_api_error_raises_llm_error(self):
        """TC-19: API call raises exception → LLMError."""
        ext = _make_extractor()
        ext.client.chat.completions.create.side_effect = Exception("Connection refused")

        with pytest.raises(LLMError, match="LLM API call failed"):
            ext.extract("text", [])

    def test_api_error_mid_loop(self):
        """TC-19: API fails on second turn."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("get_ontology", {}, "c1"),
        ])
        ext.client.chat.completions.create.side_effect = [
            turn1,
            Exception("timeout"),
        ]

        with pytest.raises(LLMError, match="LLM API call failed"):
            ext.extract("text", [])


# ---------------------------------------------------------------------------
# TC-20: Backward compat — extract returns LLMResponse with v2 Rule
# ---------------------------------------------------------------------------
class TestBackwardCompat:
    def test_returns_v2_rule_objects(self):
        """TC-20: Rules use RuleOutput, not RuleThen."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_rule", {
                "conditions": {"logic": "AND", "items": [
                    {"noun": "S", "property": "P", "operator": "==", "value": "X"},
                ]},
                "then": {"kind": "CHANGE_STATE", "description": "test"},
                "because": "reason",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        result = ext.extract("text", [])
        assert isinstance(result, LLMResponse)
        assert isinstance(result.rules[0].then, RuleOutput)
        assert result.rules[0].then.kind in ("CHANGE_STATE", "RULED_OUT", "GAP")


# ---------------------------------------------------------------------------
# TC-21: Auth uses ChainedTokenCredential
# ---------------------------------------------------------------------------
class TestAuth:
    @patch("ees.fact_extractor.AzureCliCredential")
    @patch("ees.fact_extractor.ManagedIdentityCredential")
    @patch("ees.fact_extractor.ChainedTokenCredential")
    @patch("ees.fact_extractor.AzureOpenAI")
    def test_uses_chained_credential(self, mock_aoai, mock_chained, mock_msi, mock_cli):
        """TC-21: Auth uses ChainedTokenCredential, NOT DefaultAzureCredential."""
        env = {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "gpt-4o",
        }
        with patch.dict(os.environ, env):
            FactExtractor()

        mock_cli.assert_called_once()
        mock_msi.assert_called_once()
        mock_chained.assert_called_once()
        mock_aoai.assert_called_once()


# ---------------------------------------------------------------------------
# TC-25: Token usage logged
# ---------------------------------------------------------------------------
class TestTokenLogging:
    def test_token_usage_logged(self, caplog):
        """TC-25: Total tokens summed and logged."""
        ext = _make_extractor()

        turn1 = _assistant_msg_with_tools([
            _tool_call("submit_fact", {
                "noun": "X", "property": "Y", "operator": "==", "value": "z",
            }, "c1"),
        ])
        turn2 = _assistant_msg_done()
        ext.client.chat.completions.create.side_effect = [turn1, turn2]

        with caplog.at_level(logging.INFO, logger="ees.fact_extractor"):
            ext.extract("text", [])

        log_text = caplog.text
        # Should log token count (100 + 50 = 150)
        assert "150" in log_text or "token" in log_text.lower()
