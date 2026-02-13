# Expert System (EES)

An expert system that reverse-engineers documented incidents into structured troubleshooting rules using AI-assisted fact extraction.

## Overview

EES processes free-text incident reports through an LLM to extract structured facts in `Noun(instance).Property operator value` format, then generates IF/THEN troubleshooting rules. All data is persisted as human-readable YAML.

## Prerequisites

- Python 3.10+
- Azure OpenAI Service access with a deployed model (GPT-4o, GPT-4-turbo, or GPT-5 series)
- Azure CLI authenticated (`az login`) for local development, or Managed Identity for production

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -e ".[dev]"
```

## Configuration

Set these environment variables before running:

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI service endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Deployed model name (e.g., `gpt-4o`) |
| `AZURE_OPENAI_API_VERSION` | No | API version (default: `2024-12-01-preview`) |

Authentication uses `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())` — no API keys required.

## Usage

```bash
ees process --incident path/to/incident.txt --data-dir data
```

### Workflow

1. **Load** — Validates and reads the incident text file
2. **Extract** — Sends text to Azure OpenAI, receives structured facts, rules, and root cause
3. **Confirm Facts** — Interactive review: confirm (c), edit (e), reject (r), or specialize (s) each fact
4. **Confirm Root Cause** — Confirm, edit, or reject the proposed root cause
5. **Confirm Rules** — Confirm, edit BECAUSE clause, or reject each proposed rule
6. **Persist** — Saves incident, rules, ontology updates, and root causes as YAML

### Data Directory Structure

```
data/
├── incidents/       # Processed incident files (INC-001.yaml, ...)
├── rules/           # Generated rules (R-001.yaml, ...)
├── ontology.yaml    # Noun/Property definitions
└── rootcauses.yaml  # Identified root causes
```

### Fact Format

```
Noun(instance).Property operator value
```

- Instance defaults to `*` (generalized); specialize during confirmation
- Operators: `==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `!contains`

### Rule Format

```
IF Noun(*).Property operator value AND Noun(*).Property operator value
THEN Noun(*).Property = value
BECAUSE Human-readable explanation
```

Rules use flat AND or flat OR logic only (no nesting).

## Testing

```bash
pytest tests/ -v
```

69 tests covering models, YAML persistence, ontology management, incident loading, LLM integration (mocked), and rule generation.

## Project Structure

```
src/ees/
├── __init__.py          # Package init
├── exceptions.py        # Custom exceptions (IncidentLoadError, LLMError, ConfigError)
├── models.py            # Data models (Fact, Rule, Incident, OntologyNoun, etc.)
├── yaml_store.py        # YAML persistence and ID generation
├── ontology_manager.py  # Case-insensitive ontology management
├── incident_loader.py   # File validation and text loading
├── fact_extractor.py    # Azure OpenAI LLM integration
├── rule_generator.py    # Rule deduplication and filtering
└── main.py              # CLI entry point
```
