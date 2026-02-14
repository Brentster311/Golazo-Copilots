"""Fact extractor — multi-turn tool-calling via Azure OpenAI (EES-00013).

Uses an agentic loop: the model inspects ontology/rules via read-only tools,
then submits facts and rules through schema-validated tool calls.  Invalid
submissions return validation errors so the model can self-correct.
"""
from __future__ import annotations

import json
import logging
import os
from collections import Counter
from typing import Any, Callable

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


def _conditions_key(conditions: RuleConditions) -> tuple:
    """Return a hashable key for conditions to detect duplicates.

    Normalises noun/property/operator to lowercase and sorts items so
    that the same set of conditions in different order still matches.
    """
    items = tuple(sorted(
        (f.noun.lower(), f.property.lower(), f.operator.lower(), f.value.lower())
        for f in conditions.items
    ))
    return (conditions.logic.upper(), items)


# ---------------------------------------------------------------------------
# System prompt — intentionally brief; schema is enforced by tool parameters
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert system fact extractor. Given an incident report, your job is to:

1. Call get_ontology() to see existing entity types and properties.
2. Call get_existing_rules() to see what rules already exist (avoid duplicates).
3. Read the incident report and extract facts using submit_fact().
4. Propose troubleshooting rules using submit_rule().
5. STOP (do not call any more tools) only after you have submitted at least one rule.

Guidelines:
- Facts use scope="rule" for generalizable patterns, scope="context" for instance-specific data.
- Do NOT extract GUIDs, timestamps, resource names, or subscription IDs as rule-scoped facts.
- Rules use variables ($op, $vm, etc.) in instance fields when conditions must match the same entity.
- Facts never use variables — only rules do.
- Prefer reusing existing ontology nouns/properties (case-insensitive match).
- Default instance to "*" unless a specific instance is required.
- Valid operators: ==, !=, >, <, >=, <=, contains, !contains
- Use flat AND or flat OR logic only (never mix).
- EFFICIENCY: Submit ALL facts in a single turn by calling submit_fact() multiple times \
in parallel. Do the same for rules. Do NOT submit one fact per turn.

Rule Quality Requirements:
- Every hypothesis rule MUST have an ELSE RULED_OUT("...") branch to eliminate that \
cause when the condition is NOT met.
- Conditions must ONLY reference Noun.Property pairs that you already submitted as facts. \
Do NOT invent new nouns or properties in rule conditions that have no corresponding fact.
- CHANGE_STATE description must be a concise state assignment: "Noun.property => new_value" \
(e.g., "User.role => admin-escalated"). It describes WHAT STATE CHANGES, not what action \
to take or who to engage. Wrong: "Exchange team engaged". Right: "Permission.mailSend => granted".
- RULED_OUT description must be a concise elimination statement.
- Build a CHAIN of diagnostic rules: \
  (a) Individual hypothesis rules (R1, R2, R3...) that each test one condition and \
  produce CHANGE_STATE in THEN + RULED_OUT in ELSE. \
  (b) A FINAL catch-all rule (R4) that chains the RULED_OUT outputs from the earlier \
  rules as its conditions. The catch-all condition nouns must be RULED_OUT with operator \
  "contains" matching the RULED_OUT descriptions from earlier rules. \
  The catch-all fires GAP("All known causes eliminated") with NO ELSE branch.
- Do NOT submit duplicate rules. Each rule must have unique conditions.

Example — Jira/AAD app-registration incident:
  Facts submitted first:
    User(*).role == "non-admin" [rule]
    AppRegistration(*).adminConsent == "not granted" [rule]
    AppRegistration(*).permissions !contains "Mail.Send" [rule]
  Then rules referencing those exact facts:
  R1: IF User($u).role == "non-admin"
      THEN CHANGE_STATE("User.role => admin-escalated")
      ELSE RULED_OUT("User access is not the issue")
  R2: IF AppRegistration($app).adminConsent == "not granted"
      THEN CHANGE_STATE("AppRegistration.adminConsent => granted")
      ELSE RULED_OUT("Admin consent is not the issue")
  R3: IF AppRegistration($app).permissions !contains "Mail.Send"
      THEN CHANGE_STATE("AppRegistration.permissions => Mail.Send granted")
      ELSE RULED_OUT("Mail.Send permission is already present")
  R4 (catch-all — NO ELSE, conditions use RULED_OUT noun):
      IF RULED_OUT(*).description contains "User access is not the issue" \
      AND RULED_OUT(*).description contains "Admin consent is not the issue" \
      AND RULED_OUT(*).description contains "Mail.Send permission is already present"
      THEN GAP("All known causes eliminated — investigate further")
Follow this exact pattern. R4 must reference RULED_OUT outputs, not original facts.
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
                },
                "required": ["conditions", "then"],
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
        max_turns: int = 20,
        on_status: Callable[[str], None] | None = None,
    ) -> LLMResponse:
        """Extract facts and rules from incident text via multi-turn tool calling.

        Args:
            incident_text: Raw incident report text.
            ontology: Current ontology nouns for context.
            max_turns: Maximum agentic loop iterations (default 20).
            on_status: Optional callback for live status updates.

        Returns:
            LLMResponse with collected facts, rules, and root cause.

        Raises:
            LLMError: On API failure.
        """

        def _emit(msg: str) -> None:
            """Safely emit a status message, isolating callback errors."""
            if on_status is not None:
                try:
                    on_status(msg)
                except Exception:
                    logger.debug("on_status callback error (ignored)", exc_info=True)
        # State accumulators for the agentic loop
        collected_facts: list[Fact] = []
        collected_rules: list[Rule] = []
        total_tokens = 0
        total_tool_calls = 0
        total_rejections = 0

        # Friendly descriptions for each tool
        _TOOL_LABELS = {
            "get_ontology": "Reading ontology",
            "get_existing_rules": "Checking existing rules",
            "submit_fact": "Submitting fact",
            "submit_rule": "Submitting rule",
        }

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Incident report:\n{incident_text}"},
        ]

        # Track what the LLM did last turn (for descriptive status)
        last_turn_summary = "Analyzing incident"

        for turn in range(max_turns):
            _emit(
                f"Turn {turn + 1}/{max_turns}: {last_turn_summary} "
                f"({len(collected_facts)} facts, {len(collected_rules)} rules)..."
            )
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                    tools=_TOOLS,
                    tool_choice="auto",
                    parallel_tool_calls=True,
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

            # Build a summary of this turn's actions for the next status
            turn_actions: list[str] = []

            # Process each tool call
            for tc in tool_calls:
                total_tool_calls += 1
                fn_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {}

                # Build descriptive status for this tool call
                label = _TOOL_LABELS.get(fn_name, fn_name)
                if fn_name == "submit_fact":
                    noun = args.get("noun", "?")
                    prop = args.get("property", "?")
                    _emit(f"Turn {turn + 1}: {label} — {noun}.{prop}")
                elif fn_name == "submit_rule":
                    kind = (args.get("then") or {}).get("kind", "?")
                    _emit(f"Turn {turn + 1}: {label} — {kind}")
                else:
                    _emit(f"Turn {turn + 1}: {label}")

                turn_actions.append(label)

                # Dispatch to handler
                result_str, accepted = self._dispatch_tool(
                    fn_name, args, ontology, collected_facts, collected_rules,
                )

                if not accepted:
                    total_rejections += 1

                # Append tool result message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })

            # Summarize what happened for the next turn's "calling LLM" status
            if turn_actions:
                # Deduplicate and count: ["Submitting fact", "Submitting fact"] → "Submitting fact ×2"
                counts = Counter(turn_actions)
                parts = []
                for action, count in counts.items():
                    parts.append(f"{action} ×{count}" if count > 1 else action)
                last_turn_summary = ", ".join(parts)

            _emit(
                f"Turn {turn + 1}/{max_turns} done: "
                f"{len(collected_facts)} facts, {len(collected_rules)} rules"
            )
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
                return self._handle_submit_rule(args, collected_facts, collected_rules)
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
        collected_facts: list[Fact],
        collected_rules: list[Rule],
    ) -> tuple[str, bool]:
        """Validate and collect a rule with v2 grammar."""
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

        # Validate that condition nouns+properties reference submitted facts
        # (skip RULED_OUT/CHANGE_STATE/GAP conditions used for chaining)
        known_np = {
            (f.noun.lower(), f.property.lower())
            for f in collected_facts
        }
        chaining_nouns = {"ruled_out", "change_state", "gap",
                         "diagnosticstate"}
        warnings: list[str] = []
        for cf in condition_facts:
            if cf.noun.lower() in chaining_nouns:
                continue  # chaining condition — no fact needed
            key = (cf.noun.lower(), cf.property.lower())
            if key not in known_np:
                warnings.append(
                    f"Condition '{cf.noun}.{cf.property}' has no matching "
                    f"submitted fact. Submit the fact first, then resubmit "
                    f"this rule."
                )
        if warnings:
            return " | ".join(warnings), False

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
        )

        # Dedup: reject if conditions match an existing rule
        new_cond_key = _conditions_key(conditions)
        for existing in collected_rules:
            if _conditions_key(existing.conditions) == new_cond_key:
                return (
                    f"Duplicate rule rejected — a rule with the same "
                    f"conditions already exists. Do not resubmit.",
                    False,
                )

        collected_rules.append(rule)
        return f"Rule accepted: IF ... THEN {then_output.kind}('{then_output.description}')", True
