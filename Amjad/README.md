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

### Process an Incident (Learning Phase)

```bash
ees process --incident path/to/incident.txt --data-dir data
```

### Evaluate Facts (Testing Phase)

```bash
# Evaluate with inline facts (semicolon-delimited)
ees evaluate --facts "Server(*).CPUUsage > 90; Server(*).MemoryFree < 5%" --data-dir data

# Evaluate with facts from a YAML file
ees evaluate --facts-file path/to/facts.yaml --data-dir data

# Write results to YAML file
ees evaluate --facts "Server(*).CPUUsage > 90" --data-dir data --output result.yaml
```

The evaluate command runs a forward-chaining rule evaluation engine that:
- Matches input facts against CONFIRMED rules using symbolic matching
- Chains derived facts through dependent rules (forward chaining to fixed-point)
- Reports identified root causes, eliminated candidates (RULEOUT), and GAP rules encountered
- Provides a full rule chain trace for auditability

### GUI Application

A desktop GUI for visual incident processing, knowledge base browsing, and rule evaluation:

```bash
ees-gui --data-dir data
# or
python -m ees.gui --data-dir data
```

**Tabs:**
- **Process Incident** — Load incident files, review AI-proposed facts (confirm/reject), preview generated rules, save all to YAML
- **Knowledge Base** — Browse rules (filter by status/type), ontology (tree view), and root causes
- **Evaluate** — Enter facts (one per line), run forward-chaining evaluation, view root causes, ruleouts, and GAPs

The GUI uses Tkinter (ships with Python, no extra dependencies). LLM calls run on background threads to keep the UI responsive.

Azure OpenAI settings can be configured via **File → Settings** in the GUI. Settings are saved to `data/settings.yaml` and override environment variables. Defaults: endpoint `open-ai-poc`, deployment `gpt-5.2`, API version `2024-12-01-preview`.

**Kusto Integration:** The Process Incident tab also supports fetching incident text directly from Azure Data Explorer (Kusto). Enter an Incident ID and click "Fetch from Kusto" to retrieve the description from the `IncidentDescriptions` table. Kusto cluster and database are configurable in Settings. If `accia-datacollection` is not installed, the Fetch button is disabled (graceful degradation).

### Process Workflow

1. **Load** — Validates and reads the incident text file
2. **Extract** — Sends text to Azure OpenAI, receives structured facts, rules, and root cause
3. **Confirm Facts** — Interactive review: confirm (c), edit (e), reject (r), or specialize (s) each fact
4. **Confirm Root Cause** — Confirm, edit, or reject the proposed root cause
5. **Confirm Rules** — Confirm, edit BECAUSE clause, or reject each proposed rule
6. **Detect GAPs** — Identifies confirmed facts that don't connect to the root cause through any rule; creates GAP rules for user confirmation
7. **Refine GAPs** — Checks if new rules narrow or resolve existing GAP rules
8. **Persist** — Saves incident, rules, GAP rules, ontology updates, and root causes as YAML

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

### Variable Binding

Rule conditions can use variables (`$varname`) in instance or value fields to express cross-condition relationships:

```
IF Error($op).ResultCode == ZonalAllocationFailed AND VMSeries($op).Name == $vmsize
THEN RootCause($op).Name == Zonal capacity exhaustion
BECASE ...
```

- `$op` binds consistently: both conditions must match facts with the **same** instance
- `$vmsize` captures whatever value matches and can be substituted into the conclusion
- Variables are rule-local (each rule evaluation starts with a fresh binding context)
- `*` remains a literal match — variables are a separate mechanism

### GAP Rule Format

When confirmed facts exist but don't connect to the root cause through known rules, a GAP rule is created:

```
REQUIRES: Noun(*).Property operator value, ...
PRODUCES: RootCause(*).Name == root cause name
NOTE: Unknown intermediate diagnostic steps
```

GAP rules have `status: GAP` and are refined as subsequent incidents fill in the missing steps:
- **Narrowed** — Some required facts are now connected via new rules
- **Resolved** — All required facts now connect to the root cause

The summary line reports: `GAPs: X created, Y narrowed, Z resolved`

### RULEOUT Rule Format

RULEOUT rules capture elimination reasoning — "we know it's NOT X because...":

```
IF Noun(*).Property operator value AND ...
THEN RULEOUT RootCauseName
BECAUSE Why this root cause is eliminated
```

RULEOUT rules:
- Are proposed by the LLM when elimination reasoning is detected in incident text
- Follow the same confirmation flow as positive rules (confirm/edit/reject)
- Are stored with `type: ruleout` in `rules/` YAML files
- Do NOT modify `rootcauses.yaml` (they reference, not create, root causes)
- Participate in GAP detection (their condition facts are considered connected)

## Testing

```bash
pytest tests/ -v
```

262 tests covering models, YAML persistence, ontology management, incident loading, LLM integration (mocked), rule generation, GAP detection, GAP refinement, RULEOUT rule handling, rule evaluation engine (including variable binding), GUI adapters/workers, settings management, and Kusto client integration.

## Project Structure

```
src/ees/
├── __init__.py          # Package init
├── exceptions.py        # Custom exceptions (IncidentLoadError, LLMError, ConfigError)
├── models.py            # Data models (Fact, Rule, GapRefinement, Incident, etc.)
├── yaml_store.py        # YAML persistence and ID generation
├── ontology_manager.py  # Case-insensitive ontology management
├── incident_loader.py   # File validation and text loading
├── fact_extractor.py    # Azure OpenAI LLM integration
├── rule_generator.py    # Rule deduplication and filtering
├── gap_detector.py      # GAP detection and refinement
├── rule_evaluator.py    # Forward-chaining rule evaluation engine
├── main.py              # CLI entry point (process + evaluate)
└── gui/                 # Desktop GUI application
    ├── __init__.py
    ├── __main__.py      # python -m ees.gui support
    ├── adapters.py      # Pure model → display-data converters
    ├── settings.py      # Settings persistence (Azure OpenAI + Kusto config)
    ├── kusto_client.py  # Azure Data Explorer incident fetch
    ├── workers.py       # Background thread utilities
    └── app.py           # Main Tkinter application (EESApp)
```
