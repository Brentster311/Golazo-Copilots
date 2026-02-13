# EES-00001 — Design Doc

## Summary

Build the core learning loop of an expert system that converts free-text incident reports into structured troubleshooting rules. The system loads an incident, uses an LLM to propose `Noun(instance).Property operator value` facts, lets the user confirm/edit/reject/specialize each fact, generates IF/THEN rules from confirmed facts, and persists everything to local YAML files. An iteratively-defined ontology ensures consistent naming across incidents.

## Problem Statement

Troubleshooting knowledge currently lives in free-text incident reports. This knowledge is:
- **Implicit** — diagnostic steps and root causes are buried in narrative text
- **Non-reusable** — each incident is read once and rarely referenced again
- **Inconsistent** — different engineers describe the same symptoms differently

There is no structured, machine-readable representation of the diagnostic logic that can be reused, validated, or built upon over time.

## Business Case

**Why now:** The organization has a growing corpus of documented incidents. Each one contains latent troubleshooting knowledge that degrades as institutional memory fades. Capturing this knowledge now preserves it before it's lost.

**Impact:** 
- Faster incident resolution by reusing proven diagnostic paths
- Knowledge transfer from senior to junior engineers via explicit rules
- Foundation for automated diagnostics (future work items)

**KPIs:**
- Number of incidents successfully processed into rules
- Ontology growth rate (new Noun.Property entries per incident)
- Rule generation rate (rules per incident)
- User acceptance rate (confirmed vs. rejected facts)

## Stakeholders

| Role | Interest |
|------|----------|
| Technical user (developer/engineer) | Primary user — processes incidents and curates rules |
| Project Owner | Defines scope and priorities across work items |

## Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | Load a free-text incident from a local file | User Story AC-1 |
| FR-2 | Send incident text to LLM, receive proposed facts as `Noun(instance).Property operator value`, defaulting to `*` instance | User Story AC-1 |
| FR-3 | Present proposed facts to user for confirm/edit/reject/specialize | User Story AC-2 |
| FR-4 | Persist confirmed facts + source text to `incidents/<id>.yaml` | User Story AC-3 |
| FR-5 | Check ontology for existing Noun.Property matches (case-insensitive); add new entries | User Story AC-4 |
| FR-6 | Generate flat AND-only or OR-only IF/THEN rules from confirmed facts | User Story AC-5 |
| FR-7 | Persist rules to `rules/<id>.yaml` with status CONFIRMED, source IDs, BECAUSE clause | User Story AC-5 |
| FR-8 | If root cause identified, add/update entry in `rootcauses.yaml` (Name + placeholder ActionPlan) | User Story AC-6 |
| FR-9 | Validate all YAML output is parseable | User Story AC-7 |

## Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-1 | YAML files must be human-readable | User Story NFR |
| NFR-2 | System must not silently drop or modify user-confirmed facts | User Story NFR |
| NFR-3 | Ontology matching must be case-insensitive | User Story NFR |

## Proposed Approach (High Level)

### Architecture

The system is a Python CLI application with three main components:

1. **Incident Loader** — Reads a free-text file, validates it, assigns an incident ID
2. **Fact Extractor** — Sends text to LLM with the current ontology as context, receives proposed facts AND proposed rules, presents to user for confirmation via CLI prompts
3. **Rule Generator** — Takes LLM-proposed rules (confirmed by user), persists to YAML
4. **Ontology Manager** — Maintains the Noun.Property registry with case-insensitive matching
5. **YAML Persistence** — Atomic writes to all YAML files

### Data Flow

```
[Incident File (.txt)] 
    → Incident Loader → raw text + incident ID
    → Fact Extractor → LLM call → proposed facts
    → User Confirmation (CLI) → confirmed facts
    → Ontology Manager → update ontology.yaml
    → Rule Generator → generate rules
    → YAML Persistence → incidents/*.yaml, rules/*.yaml, rootcauses.yaml
```

### YAML Schema Designs

**incidents/<incident-id>.yaml:**
```yaml
incident_id: "INC-001"
source_text: |
  Full free text of the incident...
facts:
  - noun: "Server"
    instance: "*"           # "*" = generalized (any), or specific e.g. "WebApp01"
    property: "CPUUsage"
    operator: ">"
    value: "90"
    status: "confirmed"    # confirmed | rejected
  - noun: "App"
    instance: "*"
    property: "ResponseTime"
    operator: ">"
    value: "10s"
    status: "confirmed"
root_cause_identified: "Resource Exhaustion"  # or null
processed_at: "2026-02-12T10:30:00"
```

**rules/<rule-id>.yaml:**
```yaml
rule_id: "R-001"
status: "CONFIRMED"
type: "positive"
sources:
  - "INC-001"
conditions:
  logic: "AND"  # AND | OR
  items:
    - noun: "Server"
      instance: "*"          # "*" = applies to any Server
      property: "CPUUsage"
      operator: ">"
      value: "90"
    - noun: "Server"
      instance: "*"
      property: "MemoryFree"
      operator: "<"
      value: "5%"
then:
  noun: "Server"
  instance: "*"
  property: "ResourceExhausted"
  value: "TRUE"
because: "High CPU combined with low memory indicates resource exhaustion"
```

**ontology.yaml:**
```yaml
nouns:
  - name: "Server"
    properties:
      - name: "CPUUsage"
        type: "numeric"
      - name: "MemoryFree"
        type: "percentage"
      - name: "ResourceExhausted"
        type: "boolean"
  - name: "App"
    properties:
      - name: "ResponseTime"
        type: "duration"
```

**rootcauses.yaml:**
```yaml
root_causes:
  - name: "Resource Exhaustion"
    action_plan: null  # placeholder for Problem Solving phase
  - name: "Connection Pool Exhaustion"
    action_plan: null
```

### LLM Integration

The LLM prompt will include:
1. The incident free text
2. The current ontology (so the LLM reuses existing Noun.Property names)
3. Instructions to extract facts as `Noun(instance).Property operator value` — defaulting to `*` (generalized) unless the incident context demands a specific instance
4. Instructions to identify the root cause if present
5. Instructions to propose a BECAUSE clause for each rule

**Parameterized Noun Model:**
- Nouns use a single parameter for instance identity: `Noun(instance).Property`
- `*` is the wildcard — means "any instance of this noun type"
- LLM defaults to generalized (`*`) proposals; user can specialize during confirmation
- Examples: `Server(*).CPUUsage > 90` (any server), `Server(WebApp01).CPUUsage > 90` (specific)
- Single parameter only — no multi-parameter constructors

The specific LLM provider is deferred to the Architect role.

### CLI Interaction Flow

```
$ python main.py process --incident path/to/incident.txt

Loading incident from: path/to/incident.txt
Incident ID: INC-001

Extracting facts via LLM...

Proposed facts (LLM defaults to generalized *):
  1. Server(*).CPUUsage > 90     [confirm/edit/reject/specialize] (c/e/r/s): c
  2. Server(*).MemoryFree < 5%   [confirm/edit/reject/specialize] (c/e/r/s): c
  3. App(*).ResponseTime > 10s   [confirm/edit/reject/specialize] (c/e/r/s): e
     Enter edited fact: App(*).ResponseTime > 8s
  4. Network(*).Latency > 100ms  [confirm/edit/reject/specialize] (c/e/r/s): s
     Enter instance: PrimaryLink
     → Network(PrimaryLink).Latency > 100ms  [confirm/reject] (c/r): r

Proposed root cause: "Resource Exhaustion"  [confirm/edit/reject] (c/e/r): c

Ontology updates:
  + Server.CPUUsage (new)
  + Server.MemoryFree (new)
  + App.ResponseTime (new)

Generated rules:
  R-001: IF Server(*).CPUUsage > 90 AND Server(*).MemoryFree < 5% THEN Server(*).ResourceExhausted = TRUE
  R-002: IF Server(*).ResourceExhausted = TRUE AND App(*).ResponseTime > 8s THEN RootCause = "Resource Exhaustion"

Summary:
  Facts: 3 proposed → 2 confirmed, 1 corrected, 1 rejected
  Ontology: 3 new entries
  Rules: 2 generated

All files saved.
```

### Rule Generation Strategy (MJ-3 Resolution)

The **LLM proposes complete rules** (not just facts). The prompt asks the LLM to:
1. Extract individual facts as `Noun(instance).Property operator value`
2. Propose IF/THEN rules that chain those facts toward a root cause, with BECAUSE clauses
3. Identify the root cause if present

The user confirms facts AND rules separately:
- **Phase 1:** Confirm/edit/reject/specialize individual facts
- **Phase 2:** Confirm/edit/reject proposed rules (which reference the confirmed facts)

This avoids the need for a rule composition algorithm — the LLM uses its understanding of the incident narrative to propose meaningful rule chains, and the human validates them.

### Error Handling (MJ-1, MJ-2, MJ-5 Resolution)

**Incident file validation (MJ-1):**
- File not found → `Error: Incident file not found: <path>` → exit code 1
- Empty file (0 bytes) → `Error: Incident file is empty: <path>` → exit code 1
- Binary file (non-UTF-8) → `Error: Incident file is not valid text: <path>` → exit code 1
- File > 500KB → `Warning: Large incident file (>500KB). Proceeding may be slow.` → proceed with user confirmation

**LLM response parsing (MJ-2):**
- LLM returns unparseable output → retry once with a simplified prompt
- Second failure → `Error: Could not parse LLM response. Raw output saved to <path>` → exit without modifying YAML
- LLM API unreachable → `Error: LLM API call failed: <details>` → exit without modifying YAML
- LLM returns empty facts → `No facts extracted from incident. No changes made.` → exit

**User input validation (MJ-5):**
- Edited facts are validated against the pattern: `Noun(instance).Property operator value`
- Invalid input → `Invalid fact format. Expected: Noun(instance).Property operator value` → re-prompt (up to 3 attempts, then skip fact)

**General principle:** No YAML files are modified until all user confirmations are complete and all data is validated. Persistence is a single atomic step at the end.

### Root Cause is Not Parameterized (MJ-4 Resolution)

Root causes are **type-level concepts**, not instance-level. `RootCause = "Resource Exhaustion"` applies regardless of which specific server is exhausted. Therefore:
- Root cause confirmation offers `c/e/r` only (no specialize)
- Root causes are simple string names in `rootcauses.yaml`

### ID Generation Strategy

**Incident IDs:** `INC-<sequential-number>` — auto-incremented by reading existing files in `incidents/` and finding the highest number. Padded to 3 digits minimum (INC-001, INC-002, ..., INC-999, INC-1000).

**Rule IDs:** `R-<sequential-number>` — same strategy, reading `rules/` directory. Padded to 3 digits minimum.

### LLM Provider Decision

**Provider:** Azure OpenAI Service via the `openai` Python package (Azure mode).

**Available models:** GPT-4o, GPT-4-turbo, GPT-5 series, and others as deployed. The model is determined by the Azure OpenAI deployment name — code does not hardcode a specific model.

**Rationale:**
- Native Azure Identity integration — uses `ChainedTokenCredential` per best practices
- Model flexibility — deployment-level choice, swap models without code changes
- Enterprise-grade — content filtering, private networking, data residency
- Same `openai` Python SDK, just configured with `AzureOpenAI` client
- Supports JSON mode / structured outputs for reliable parsing

**Alternative considered:** GitHub Copilot API (viable, uses GitHub token auth). Rejected for v1 because Azure OpenAI offers more control over model selection and deployment configuration. Can be revisited if needed.

**Authentication (per TechBestPractices.md):**
```python
from azure.identity import ChainedTokenCredential, AzureCliCredential, ManagedIdentityCredential

credential = ChainedTokenCredential(
    AzureCliCredential(),           # Local dev
    ManagedIdentityCredential()     # Production (Azure)
)
```

**DO NOT** use `DefaultAzureCredential` — it has unpredictable behavior per best practices.

**Configuration (environment variables):**
- `AZURE_OPENAI_ENDPOINT` — Azure OpenAI resource endpoint (e.g., `https://my-resource.openai.azure.com/`)
- `AZURE_OPENAI_DEPLOYMENT` — deployment name (e.g., `gpt-4o`, `gpt-5`)
- `AZURE_OPENAI_API_VERSION` — API version (default: `2024-12-01-preview`)

If `AZURE_OPENAI_ENDPOINT` is missing, exit with `Error: AZURE_OPENAI_ENDPOINT environment variable not set.`
If `AZURE_OPENAI_DEPLOYMENT` is missing, exit with `Error: AZURE_OPENAI_DEPLOYMENT environment variable not set.`

**LLM Response Format:** JSON mode with a defined schema:
```json
{
  "facts": [
    {
      "noun": "Server",
      "instance": "*",
      "property": "CPUUsage",
      "operator": ">",
      "value": "90"
    }
  ],
  "rules": [
    {
      "conditions": {
        "logic": "AND",
        "items": [
          {"noun": "Server", "instance": "*", "property": "CPUUsage", "operator": ">", "value": "90"},
          {"noun": "Server", "instance": "*", "property": "MemoryFree", "operator": "<", "value": "5%"}
        ]
      },
      "then": {"noun": "Server", "instance": "*", "property": "ResourceExhausted", "value": "TRUE"},
      "because": "High CPU combined with low memory indicates resource exhaustion"
    }
  ],
  "root_cause": "Resource Exhaustion"
}
```

### Project Structure

```
amjad/
├── src/
│   └── ees/
│       ├── __init__.py
│       ├── main.py              # CLI entry point (argparse)
│       ├── incident_loader.py   # File loading + validation
│       ├── fact_extractor.py    # LLM integration + fact proposal
│       ├── rule_generator.py    # Rule confirmation + persistence
│       ├── ontology_manager.py  # Ontology CRUD + matching
│       ├── yaml_store.py        # Atomic YAML read/write
│       └── models.py            # Dataclasses: Fact, Rule, RootCause, OntologyEntry
├── data/
│   ├── incidents/               # Processed incident YAMLs
│   ├── rules/                   # Generated rule YAMLs
│   ├── ontology.yaml            # Noun.Property registry
│   └── rootcauses.yaml          # RootCause entities
├── tests/
│   ├── __init__.py
│   ├── test_incident_loader.py
│   ├── test_fact_extractor.py
│   ├── test_rule_generator.py
│   ├── test_ontology_manager.py
│   ├── test_yaml_store.py
│   └── fixtures/                # Sample incidents, mock LLM responses
├── pyproject.toml
└── README.md
```

### Dependency Choices

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >=1.0 | LLM API client (Azure OpenAI mode) |
| `azure-identity` | >=1.15 | Azure auth — ChainedTokenCredential (AzureCli + MSI) |
| `ruamel.yaml` | >=0.17 | YAML read/write (preserves comments, round-trips cleanly) |
| `pytest` | >=7.0 | Testing framework |
| `pytest-mock` | >=3.0 | LLM mocking in tests |

**Why `ruamel.yaml` over `PyYAML`:** ruamel.yaml preserves comments and formatting on round-trip, which matters for human-edited YAML files. PyYAML strips comments.

**Why `azure-identity`:** Required for `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())` per TechBestPractices.md. `DefaultAzureCredential` is explicitly forbidden.

### Security & Privacy

- **Authentication:** Azure Identity via `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())`. No API keys stored in files or environment variables — auth is token-based.
- **Incident data:** Stays local. Incident text is sent to Azure OpenAI — data stays within the Azure tenant's boundary (no external OpenAI calls). Users should still be aware that incident content is transmitted to the LLM.
- **No PII handling:** System does not attempt to detect or redact PII in incidents. If incidents contain PII, that's the user's responsibility. A future enhancement could add PII scrubbing before LLM submission.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Database (SQLite) instead of YAML | YAML is more human-readable, easier to hand-edit, diffs cleanly in git. Database adds complexity without benefit at this scale. |
| Batch processing of multiple incidents | Adds complexity. Single-incident processing validates the core loop first. |
| Pre-defined ontology | Restricts the system to known domains. Iterative growth captures emergent terminology. |
| Fully automatic fact extraction (no user confirmation) | LLM output is not reliable enough. User confirmation is the quality gate. |

## Risks, Mitigations, Open Questions

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM proposes low-quality facts | Medium | Medium | User confirmation step filters bad extractions |
| Ontology drift (same concept, different names) | Medium | High | Case-insensitive matching; LLM receives current ontology as context |
| LLM API unavailability | Low | High | Graceful error handling; no data loss on failure |
| YAML files corrupted by partial writes | Low | High | Write to temp file, then atomic rename |
| Rule generation logic produces incorrect rules | Medium | Medium | User reviews generated rules during CLI interaction |

**Open Questions:**
- LLM provider selection (deferred to Architect role)
- Incident ID generation strategy (auto-increment, UUID, user-provided?)
- Rule ID generation strategy (auto-increment, hash-based?)

## Dependencies

| Dependency | Type | Risk |
|------------|------|------|
| Python 3.x | Runtime | Low — widely available |
| Azure OpenAI Service | External service | Medium — requires Azure subscription, endpoint, deployment, network access |
| azure-identity | Library | Low — stable, Microsoft-maintained |
| ruamel.yaml | Library | Low — stable, well-maintained |

## Migration / Rollout / Rollback Plan

- **Rollout:** Local Python installation. No deployment infrastructure needed.
- **Migration:** N/A — greenfield project, no existing data to migrate.
- **Rollback:** Delete generated YAML files or `git revert`. No external state to clean up.

## Observability Plan

- CLI prints a summary after each incident processing (facts proposed/confirmed/rejected, ontology additions, rules generated)
- Metrics are informational only in v1 — no external telemetry system
- Errors are printed to stderr with actionable messages

## Test Strategy Summary

| Level | What | How |
|-------|------|-----|
| Unit tests | YAML read/write, ontology matching (case-insensitive), rule generation logic, fact parsing | pytest with fixtures |
| Integration tests | End-to-end incident processing with mocked LLM responses | pytest with LLM mock |
| Manual testing | CLI interaction flow, user confirmation UX | Manual walkthrough with sample incidents |
| Acceptance tests | Each acceptance criterion verified against sample data | One test per AC |
