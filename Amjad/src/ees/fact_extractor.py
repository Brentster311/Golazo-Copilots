"""Fact extractor — LLM integration via Azure OpenAI with Azure Identity auth."""
from __future__ import annotations

import json
import os
from pathlib import Path

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
    RuleThen,
)


_SYSTEM_PROMPT = """\
You are an expert system fact extractor. Given an incident report and an existing ontology, \
extract structured facts and propose troubleshooting rules.

Output JSON with this exact schema:
{
  "facts": [
    {"noun": "<NounName>", "instance": "*", "property": "<PropertyName>", "operator": "<op>", "value": "<val>", "scope": "rule"}
  ],
  "rules": [
    {
      "type": "positive",
      "conditions": {
        "logic": "AND",
        "items": [{"noun": "...", "instance": "*", "property": "...", "operator": "...", "value": "..."}]
      },
      "then": {"noun": "...", "instance": "*", "property": "...", "value": "..."},
      "because": "Human-readable explanation"
    }
  ],
  "root_cause": "Root cause name or null"
}

For RULEOUT rules (elimination reasoning like "we ruled out X because..."):
{
  "type": "ruleout",
  "conditions": {
    "logic": "AND",
    "items": [{"noun": "...", "instance": "*", "property": "...", "operator": "...", "value": "..."}]
  },
  "then": {"noun": "RULEOUT", "instance": "*", "property": "Target", "value": "<RootCauseName>"},
  "because": "Why this root cause is ruled out"
}

Fact scope classification:
- Each fact MUST include a "scope" field: "rule" or "context".
- "rule" = generalizable across incidents (use in troubleshooting rules).
- "context" = instance-specific documentation (saved but NOT used in rules).

Extract as "scope": "rule":
- Error codes, result codes, failure categories
- VM SKU sizes, operation types, service names
- Boolean states (success/failure flags)
- Error message patterns (use 'contains' operator)

Extract as "scope": "context" (or DO NOT extract at all):
- Resource group names, resource names, cluster names, node names
- GUIDs (activity IDs, correlation IDs, request IDs, subscription IDs)
- Specific timestamps or dates
- Region names (unless the root cause IS region-specific)

Rules:
- Default instance to "*" (generalized) unless the incident clearly requires a specific instance.
- Valid operators: ==, !=, >, <, >=, <=, contains, !contains
- Use flat AND or flat OR logic only (never mix).
- Every rule must have a BECAUSE clause.
- Reuse existing ontology noun/property names when they match (case-insensitive).
- Identify the root cause if present in the incident, or set to null.
- Only use "scope": "rule" facts in rule conditions.
"""


class FactExtractor:
    """Extracts facts and rules from incident text using Azure OpenAI."""

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

    def extract(self, incident_text: str, ontology: list[OntologyNoun]) -> LLMResponse:
        """Send incident text to LLM and parse the response.

        Retries once on parse failure. Raises LLMError on API or persistent parse failure.
        """
        ontology_context = self._format_ontology(ontology)
        user_msg = f"Existing ontology:\n{ontology_context}\n\nIncident report:\n{incident_text}"

        raw = ""
        for attempt in range(2):  # initial + 1 retry
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    response_format={"type": "json_object"},
                )
            except Exception as e:
                raise LLMError(f"LLM API call failed: {e}") from e

            raw = response.choices[0].message.content
            try:
                parsed = json.loads(raw)
                return self._parse_response(parsed)
            except (json.JSONDecodeError, KeyError, TypeError):
                if attempt == 0:
                    # Retry with simplified prompt
                    user_msg = (
                        f"Previous response was not valid JSON. "
                        f"Please respond with ONLY valid JSON.\n\n{user_msg}"
                    )
                    continue

        # Both attempts failed
        raise LLMError(f"Could not parse LLM response. Raw output:\n{raw}")

    def _format_ontology(self, ontology: list[OntologyNoun]) -> str:
        """Format ontology as text for the LLM prompt."""
        if not ontology:
            return "(empty — no existing ontology)"
        lines = []
        for noun in ontology:
            props = ", ".join(p.name for p in noun.properties)
            lines.append(f"- {noun.name}: {props}")
        return "\n".join(lines)

    def _parse_response(self, data: dict) -> LLMResponse:
        """Parse the JSON response into an LLMResponse."""
        facts = [
            Fact.from_dict({**f, "instance": f.get("instance", "*")})
            for f in data.get("facts", [])
        ]

        rules = []
        for r in data.get("rules", []):
            cond = r["conditions"]
            items = [
                Fact.from_dict({**it, "instance": it.get("instance", "*")})
                for it in cond["items"]
            ]
            then_data = r["then"]
            rule_type = r.get("type", "positive")
            rules.append(
                Rule(
                    rule_id="",  # assigned later
                    type=rule_type,
                    conditions=RuleConditions(logic=cond["logic"], items=items),
                    then=RuleThen(
                        noun=then_data["noun"],
                        instance=then_data.get("instance", "*"),
                        property=then_data["property"],
                        value=then_data["value"],
                    ),
                    because=r.get("because", ""),
                )
            )

        return LLMResponse(
            facts=facts,
            rules=rules,
            root_cause=data.get("root_cause"),
        )
