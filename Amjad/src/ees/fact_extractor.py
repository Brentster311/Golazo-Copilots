"""Fact extractor — multi-turn tool-calling via Azure OpenAI (EES-00013).

Uses an agentic loop: the model inspects ontology/rules via read-only tools,
then submits facts and rules through schema-validated tool calls.  Invalid
submissions return validation errors so the model can self-correct.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    ManagedIdentityCredential,
)
from openai import AzureOpenAI

from ees.exceptions import ConfigError, LLMError
from ees.models import (
    Fact,
    LLMResponse,
    OntologyNoun,
    Rule,
    RuleConditions,
    RuleOutput,
    VALID_OPERATORS,
    VALID_OUTPUT_KINDS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — intentionally brief; schema is enforced by tool parameters
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert system fact extractor. Given an incident report, your job is to:

1. Call get_ontology() to see existing entity types and properties.
2. Call get_existing_rules() to see what rules already exist (avoid duplicates).
3. Read the incident report and extract facts using submit_fact().
4. Propose troubleshooting rules using submit_rule().
5. If a root cause is identified, call set_root_cause().

Guidelines:
- Facts use scope="rule" for generalizable patterns, scope="context" for instance-specific data.
- Do NOT extract GUIDs, timestamps, resource names, or subscription IDs as rule-scoped facts.
- Rules use variables ($op, $vm, etc.) in instance fields when conditions must match the same entity.
- Facts never use variables — only rules do.
- Every rule needs a "because" explanation.
- Use CHANGE_STATE for positive identification, RULED_OUT for elimination, GAP for missing information.
- Prefer reusing existing ontology nouns/properties (case-insensitive match).
- Default instance to "*" unless a specific instance is required.
- Valid operators: ==, !=, >, <, >=, <=, contains, !contains
- Use flat AND or flat OR logic only (never mix).
"""

# ---------------------------------------------------------------------------
# Tool definitions (JSON-Schema for each tool's parameters)
# ---------------------------------------------------------------------------

_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_ontology",
            "description": (
                "Retrieve the current ontology (nouns and their properties). "
                "Call this first to understand available entities before extracting facts."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_existing_rules",
            "description": (
                "Retrieve all confirmed troubleshooting rules in the knowledge base. "
                "Use to avoid duplicating existing rules."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_fact",
            "description": (
                "Submit a single extracted fact. Facts represent observed conditions "
                "in the incident. Use scope='rule' for generalizable facts, "
                "scope='context' for instance-specific documentation. "
                "Do NOT include variables ($) in facts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "noun": {"type": "string", "description": "Entity name (e.g., 'Error', 'VM')"},
                    "instance": {"type": "string", "description": "Instance name or '*' for generalized"},
                    "property": {"type": "string", "description": "Property name (e.g., 'ResultCode')"},
                    "operator": {
                        "type": "string",
                        "enum": list(VALID_OPERATORS),
                    },
                    "value": {"type": "string", "description": "The observed value"},
                    "scope": {"type": "string", "enum": ["rule", "context"]},
                },
                "required": ["noun", "property", "operator", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_rule",
            "description": (
                "Submit a troubleshooting rule with v2 grammar. "
                "The THEN branch is required (CHANGE_STATE, RULED_OUT, or GAP). "
                "An optional ELSE branch fires when conditions are NOT met."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "object",
                        "properties": {
                            "logic": {"type": "string", "enum": ["AND", "OR"]},
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "noun": {"type": "string"},
                                        "instance": {"type": "string"},
                                        "property": {"type": "string"},
                                        "operator": {"type": "string", "enum": list(VALID_OPERATORS)},
                                        "value": {"type": "string"},
                                    },
                                    "required": ["noun", "property", "operator", "value"],
                                },
                                "minItems": 1,
                            },
                        },
                        "required": ["logic", "items"],
                    },
                    "then": {
                        "type": "object",
                        "properties": {
                            "kind": {"type": "string", "enum": list(VALID_OUTPUT_KINDS)},
                            "description": {"type": "string", "minLength": 1},
                        },
                        "required": ["kind", "description"],
                    },
                    "else": {
                        "type": "object",
                        "properties": {
                            "kind": {"type": "string", "enum": list(VALID_OUTPUT_KINDS)},
                            "description": {"type": "string", "minLength": 1},
                        },
                        "required": ["kind", "description"],
                    },
                    "because": {"type": "string", "description": "Human-readable explanation"},
                },
                "required": ["conditions", "then", "because"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_root_cause",
            "description": (
                "Set the root cause identified in this incident. "
                "Call once when you have determined the root cause."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Root cause name"},
                },
                "required": ["name"],
            },
        },
    },
]

_KNOWN_TOOLS = {t["function"]["name"] for t in _TOOLS}


def _validate_output_branch(
    data: dict, label: str
) -> tuple[RuleOutput | None, str | None]:
    """Validate a THEN or ELSE branch dict.

    Returns (RuleOutput, None) on success or (None, error_message) on failure.
    """
    kind = data.get("kind", "")
    desc = data.get("description", "")
    if kind not in VALID_OUTPUT_KINDS:
        return None, (
            f"Invalid kind '{kind}' in {label} branch. "
            f"Valid: {', '.join(VALID_OUTPUT_KINDS)}"
        )
    if not desc:
        return None, f"{label} description must not be empty."
    return RuleOutput(kind=kind, description=desc), None


class FactExtractor:
    """Extracts facts and rules from incident text using Azure OpenAI tool calling."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        deployment: str | None = None,
        api_version: str | None = None,
    ) -> None:
        resolved_endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not resolved_endpoint:
            raise ConfigError("AZURE_OPENAI_ENDPOINT environment variable not set.")

        self.deployment = deployment or os.environ.get("AZURE_OPENAI_DEPLOYMENT")
        if not self.deployment:
            raise ConfigError("AZURE_OPENAI_DEPLOYMENT environment variable not set.")

        resolved_api_version = api_version or os.environ.get(
            "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
        )

        # Per TechBestPractices.md: explicit credential chain, NOT DefaultAzureCredential
        credential = ChainedTokenCredential(
            AzureCliCredential(),           # Local dev
            ManagedIdentityCredential(),    # Production (Azure)
        )

        self.client = AzureOpenAI(
            azure_endpoint=resolved_endpoint,
            azure_ad_token_provider=self._make_token_provider(credential),
            api_version=resolved_api_version,
        )

    @staticmethod
    def _make_token_provider(credential: ChainedTokenCredential):
        """Create a token provider callable for AzureOpenAI."""
        def get_token() -> str:
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        return get_token

    # ------------------------------------------------------------------
    # Public API — signature unchanged from v1
    # ------------------------------------------------------------------

    def extract(
        self,
        incident_text: str,
        ontology: list[OntologyNoun],
        *,
        max_turns: int = 10,
    ) -> LLMResponse:
        """Extract facts and rules from incident text via multi-turn tool calling.

        Args:
            incident_text: Raw incident report text.
            ontology: Current ontology nouns for context.
            max_turns: Maximum agentic loop iterations (default 10).

        Returns:
            LLMResponse with collected facts, rules, and root cause.

        Raises:
            LLMError: On API failure.
        """
        # State accumulators for the agentic loop
        collected_facts: list[Fact] = []
        collected_rules: list[Rule] = []
        root_cause: str | None = None
        total_tokens = 0
        total_tool_calls = 0
        total_rejections = 0

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Incident report:\n{incident_text}"},
        ]

        for turn in range(max_turns):
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                    tools=_TOOLS,
                    tool_choice="auto",
                )
            except Exception as e:
                raise LLMError(f"LLM API call failed: {e}") from e

            # Track tokens
            if response.usage:
                total_tokens += response.usage.total_tokens

            assistant_msg = response.choices[0].message
            tool_calls = assistant_msg.tool_calls

            # No tool calls → model is done
            if not tool_calls:
                break

            # Append the assistant message (with tool_calls) to history
            messages.append(assistant_msg)

            # Process each tool call
            for tc in tool_calls:
                total_tool_calls += 1
                fn_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {}

                # Dispatch to handler
                result_str, accepted = self._dispatch_tool(
                    fn_name, args, ontology, collected_facts, collected_rules,
                )

                if not accepted:
                    total_rejections += 1

                # Handle root_cause specially (returned via _dispatch_tool side channel)
                if fn_name == "set_root_cause" and accepted:
                    root_cause = args.get("name")

                # Append tool result message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })
        else:
            logger.warning(
                "Max turns (%d) reached during extraction. "
                "Returning %d facts, %d rules collected so far.",
                max_turns, len(collected_facts), len(collected_rules),
            )

        logger.info(
            "Extraction complete: turns=%d, tool_calls=%d, rejections=%d, "
            "facts=%d, rules=%d, tokens=%d",
            min(turn + 1, max_turns) if max_turns > 0 else 0,
            total_tool_calls,
            total_rejections,
            len(collected_facts),
            len(collected_rules),
            total_tokens,
        )

        return LLMResponse(
            facts=collected_facts,
            rules=collected_rules,
            root_cause=root_cause,
        )

    # ------------------------------------------------------------------
    # Tool dispatch
    # ------------------------------------------------------------------

    def _dispatch_tool(
        self,
        name: str,
        args: dict,
        ontology: list[OntologyNoun],
        collected_facts: list[Fact],
        collected_rules: list[Rule],
    ) -> tuple[str, bool]:
        """Dispatch a tool call to its handler.

        Returns (result_string, accepted).  accepted=False means validation
        failed and the result_string contains an error message.
        """
        try:
            if name == "get_ontology":
                return self._handle_get_ontology(ontology), True
            elif name == "get_existing_rules":
                return self._handle_get_existing_rules(), True
            elif name == "submit_fact":
                return self._handle_submit_fact(args, ontology, collected_facts)
            elif name == "submit_rule":
                return self._handle_submit_rule(args, collected_rules)
            elif name == "set_root_cause":
                return self._handle_set_root_cause(args)
            else:
                return (
                    f"Unknown tool: '{name}'. Available tools: "
                    f"{', '.join(sorted(_KNOWN_TOOLS))}",
                    False,
                )
        except Exception as e:
            logger.debug("Tool handler error for %s: %s", name, e)
            return f"Internal error processing {name}: {e}", False

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_get_ontology(ontology: list[OntologyNoun]) -> str:
        """Return ontology as JSON."""
        if not ontology:
            return json.dumps({"nouns": [], "message": "No ontology exists yet. You may create new nouns."})
        data = [
            {"name": n.name, "properties": [p.name for p in n.properties]}
            for n in ontology
        ]
        return json.dumps({"nouns": data})

    @staticmethod
    def _handle_get_existing_rules() -> str:
        """Return existing rules. Currently returns empty (no rules parameter on extract)."""
        return json.dumps([])

    @staticmethod
    def _handle_submit_fact(
        args: dict,
        ontology: list[OntologyNoun],
        collected_facts: list[Fact],
    ) -> tuple[str, bool]:
        """Validate and collect a fact."""
        noun = args.get("noun", "")
        instance = args.get("instance", "*")
        prop = args.get("property", "")
        operator = args.get("operator", "")
        value = args.get("value", "")
        scope = args.get("scope", "rule")

        # Validate operator
        if operator not in VALID_OPERATORS:
            return (
                f"Invalid operator '{operator}'. Valid operators: {', '.join(VALID_OPERATORS)}",
                False,
            )

        # Reject variables in facts
        if Fact.is_variable(instance):
            return "Facts must not contain variables. Use '*' or a specific instance name.", False
        if Fact.is_variable(value):
            return "Facts must not contain variables in the value field.", False

        # Build fact
        fact = Fact(
            noun=noun,
            instance=instance,
            property=prop,
            operator=operator,
            value=value,
            scope=scope,
        )
        collected_facts.append(fact)

        # Ontology warning (accepted but noted)
        warnings: list[str] = []
        known_nouns = {n.name.lower(): n for n in ontology}
        if noun.lower() not in known_nouns:
            warnings.append(f"Note: noun '{noun}' is not in the current ontology. It will be created.")
        elif not known_nouns[noun.lower()].has_property(prop):
            warnings.append(f"Note: property '{prop}' is new for noun '{noun}'.")

        msg = f"Fact accepted: {fact.to_display()}"
        if warnings:
            msg += " | " + " | ".join(warnings)
        return msg, True

    @staticmethod
    def _handle_submit_rule(
        args: dict,
        collected_rules: list[Rule],
    ) -> tuple[str, bool]:
        """Validate and collect a rule with v2 grammar."""
        # Validate because
        because = args.get("because", "")
        if not because:
            return "Rule must have a 'because' explanation.", False

        # Validate conditions
        cond_data = args.get("conditions", {})
        items_data = cond_data.get("items", [])
        if not items_data:
            return "Rule must have at least one condition.", False

        # Validate each condition's operator
        for i, item in enumerate(items_data):
            op = item.get("operator", "")
            if op not in VALID_OPERATORS:
                return f"Invalid operator '{op}' in condition {i + 1}. Valid: {', '.join(VALID_OPERATORS)}", False

        # Build condition items
        condition_facts = [
            Fact(
                noun=it.get("noun", ""),
                instance=it.get("instance", "*"),
                property=it.get("property", ""),
                operator=it.get("operator", ""),
                value=it.get("value", ""),
            )
            for it in items_data
        ]
        conditions = RuleConditions(logic=cond_data.get("logic", "AND"), items=condition_facts)

        # Validate then branch
        then_data = args.get("then", {})
        then_output, err = _validate_output_branch(then_data, "THEN")
        if err:
            return err, False

        # Validate optional else branch
        else_output: RuleOutput | None = None
        else_data = args.get("else")
        if else_data:
            else_output, err = _validate_output_branch(else_data, "ELSE")
            if err:
                return err, False

        rule = Rule(
            rule_id="",  # assigned later by rule_generator
            conditions=conditions,
            then=then_output,
            else_=else_output,
            because=because,
        )
        collected_rules.append(rule)
        return f"Rule accepted: IF ... THEN {then_kind}('{then_desc}')", True

    @staticmethod
    def _handle_set_root_cause(args: dict) -> tuple[str, bool]:
        """Set root cause. Last call wins."""
        name = args.get("name", "")
        if not name:
            return "Root cause name must not be empty.", False
        return f"Root cause set to: {name}", True
