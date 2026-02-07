# SFI-020 Design Document: Right-Click KPI Row → Analyze with LLM

**Work Item**: SFI-020  
**Author**: Program Manager  
**Date**: 2026-02-06  
**Status**: DRAFT

---

## 1. Overview

Add a right-click context menu to KPI/Action Item treeviews in SFIReporter that sends action item data to Azure OpenAI for structured analysis. The LLM response is displayed in a modal and saved to disk as JSON under `%LOCALAPPDATA%`.

### User Flow

```
User right-clicks KPI row → Context menu appears → "🤖 Analyze with LLM"
  → Progress spinner modal → Background thread:
      1. Look up action item data from _kpi_id_map + detailed_items
      2. Build structured prompt
      3. Call Azure OpenAI
      4. Save response JSON to %LOCALAPPDATA%/sfireporter/analyses/
      5. root.after(0, ...) → display AnalysisModal
```

---

## 2. Architecture

### 2.1 New Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| `llm_client.py` | `SFIReporter/src/sfi_reporter/llm_client.py` | Azure OpenAI wrapper: config, prompt building, API call |
| `llm_storage.py` | `SFIReporter/src/sfi_reporter/llm_storage.py` | Save/load analysis JSON to `%LOCALAPPDATA%/sfireporter/analyses/` |

### 2.2 Modified Modules

| Module | Changes |
|--------|---------|
| `tk_app.py` | Add right-click bindings to `tree_kpis` + `DrillDownModal._tree`; add `AnalysisModal` class; add `_on_analyze_with_llm()` handler; add `_show_analysis_progress()` |
| `pyproject.toml` | Add `openai>=1.0.0` dependency |

### 2.3 Component Diagram

```
┌──────────────────────────────────────────────────────┐
│  tk_app.py                                           │
│  ┌──────────────┐   ┌───────────────┐                │
│  │ SFIReporter   │   │ DrillDownModal │                │
│  │ .tree_kpis    │   │ ._tree         │                │
│  │ <Button-3> ──►│   │ <Button-3> ──►│                │
│  └──────┬───────┘   └───────┬───────┘                │
│         └────────┬──────────┘                        │
│                  ▼                                    │
│        _on_analyze_with_llm(item_data)               │
│                  │                                    │
│         ┌────────┴────────┐                          │
│         │ threading.Thread │                          │
│         └────────┬────────┘                          │
│                  ▼                                    │
│  ┌───────────────────────────┐                       │
│  │ AnalysisProgressModal     │  (spinner/status)     │
│  └───────────────────────────┘                       │
│                  │ root.after(0, ...)                 │
│                  ▼                                    │
│  ┌───────────────────────────┐                       │
│  │ AnalysisModal             │  (result display)     │
│  └───────────────────────────┘                       │
└──────────────────────────────────────────────────────┘
              │                        │
              ▼                        ▼
┌──────────────────┐    ┌──────────────────────┐
│  llm_client.py   │    │  llm_storage.py      │
│  - LLMConfig     │    │  - save_analysis()   │
│  - build_prompt()│    │  - load_analysis()   │
│  - analyze_item()│    │  - get_analysis_path()│
└──────────────────┘    └──────────────────────┘
         │                         │
         ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│  Azure OpenAI    │    │  %LOCALAPPDATA%/     │
│  (GPT-4o)        │    │  sfireporter/analyses│
└──────────────────┘    └──────────────────────┘
```

---

## 3. Detailed Design

### 3.1 Context Menu Binding

**Pattern**: Follows tkinter `<Button-3>` convention. A `tk.Menu` is created on-demand at the click position.

**In `SFIReporterApp._build_ui()`:**
```python
self.tree_kpis.bind("<Button-3>", self._on_kpi_right_click)
```

**In `DrillDownModal.__init__()`:**
```python
self._tree.bind("<Button-3>", self._on_item_right_click)
```

**Handler pattern:**
```python
def _on_kpi_right_click(self, event):
    iid = self.tree_kpis.identify_row(event.y)
    if not iid:
        return
    self.tree_kpis.selection_set(iid)
    menu = tk.Menu(self.root, tearoff=0)
    menu.add_command(
        label="🤖 Analyze with LLM",
        command=lambda: self._on_analyze_with_llm(iid),
    )
    menu.tk_popup(event.x_root, event.y_root)
```

### 3.2 `llm_client.py` — LLM Integration

#### Configuration

```python
@dataclass
class LLMConfig:
    endpoint: str       # AZURE_OPENAI_ENDPOINT env var
    api_key: str        # AZURE_OPENAI_API_KEY env var
    deployment: str     # AZURE_OPENAI_DEPLOYMENT env var (default: "gpt-4o")
    api_version: str    # default: "2024-10-21"
    timeout: int        # default: 30 seconds

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load config from environment variables. Raises LLMConfigError if missing."""
```

**Environment variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | — | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Yes | — | API key |
| `AZURE_OPENAI_DEPLOYMENT` | No | `gpt-4o` | Deployment/model name |
| `AZURE_OPENAI_API_VERSION` | No | `2024-10-21` | API version |

#### Prompt Construction

`build_prompt(item: dict) -> list[dict]`

The system prompt instructs the LLM to produce a structured analysis with exactly four sections:

```
You are an SFI (Security, Fundamentals, and Infrastructure) remediation analyst.
Analyze the following action item data and produce a structured assessment.

## Output Format (use these exact section headers):

### 🎯 Mission
What is being asked? Summarize the remediation objective in 2-3 sentences.

### ✅ Steps to Done
Provide a concise, numbered list of actionable steps to complete remediation.

### 🔧 Resources Needing Repair
List the specific resources, services, or assets that need attention.
Include resource type, name/ID, and subscription if available.

### ⚠️ Risk of Delay
What are the consequences of not completing this on time?
Consider SLA impact, compliance implications, and downstream effects.
```

The user message includes formatted action item data:
- Title, KPI ID, Status, SLA Type, Due Date, ETA
- Service tree (Division → Group → Organization → Service)
- Ownership (Assigned To, Action Owner)
- Remediation text, Details
- Cloud/Environment info
- Asset types and resource URIs

#### API Call

`analyze_item(item: dict, config: LLMConfig) -> AnalysisResult`

Uses the `openai` Python SDK with Azure configuration:
```python
client = AzureOpenAI(
    azure_endpoint=config.endpoint,
    api_key=config.api_key,
    api_version=config.api_version,
)
response = client.chat.completions.create(
    model=config.deployment,
    messages=build_prompt(item),
    temperature=0.3,  # Low for factual analysis
    max_tokens=2000,
)
```

#### Return Type

```python
@dataclass
class AnalysisResult:
    action_item_id: str
    kpi_id: str
    title: str
    analysis_text: str      # Raw LLM response (markdown)
    mission: str             # Parsed section
    steps_to_done: str       # Parsed section
    resources: str           # Parsed section
    risk_of_delay: str       # Parsed section
    model: str               # Model used
    timestamp: str           # ISO 8601
    prompt_tokens: int
    completion_tokens: int
```

### 3.3 `llm_storage.py` — Persistent Storage

#### Storage Location

```
%LOCALAPPDATA%/sfireporter/analyses/<action_item_id>.json
```

Uses `%LOCALAPPDATA%` (durable) rather than `%TEMP%` (volatile), consistent with `s360_client` cache pattern.

#### File Format

```json
{
    "schema_version": 1,
    "action_item_id": "AI-12345",
    "kpi_id": "KPI-67890",
    "title": "Remediate Azure SQL TDE encryption",
    "analysis_text": "### 🎯 Mission\n...",
    "mission": "...",
    "steps_to_done": "...",
    "resources": "...",
    "risk_of_delay": "...",
    "model": "gpt-4o",
    "timestamp": "2026-02-06T14:30:00Z",
    "prompt_tokens": 450,
    "completion_tokens": 800
}
```

#### Functions

```python
def get_analyses_dir() -> Path:
    """Return %LOCALAPPDATA%/sfireporter/analyses/, creating if needed."""

def save_analysis(result: AnalysisResult) -> Path:
    """Write analysis to JSON file. Returns the file path."""

def load_analysis(action_item_id: str) -> AnalysisResult | None:
    """Load analysis from disk. Returns None if not found or corrupted."""

def analysis_exists(action_item_id: str) -> bool:
    """Check if a saved analysis exists for this action item."""
```

#### Write Strategy

Atomic write (write to `.tmp`, then `os.replace()`) — consistent with the column metadata cache pattern in `data.py`.

### 3.4 `AnalysisModal` — Result Display

Follows the `ItemDetailsModal` pattern:

- `tk.Toplevel` with `transient()`, `grab_set()`
- Scrollable `tk.Text` widget with tagged text
- **Section headers** use emoji + bold tags (same pattern as detail modal's group headers)
- **Sections**: 🎯 Mission, ✅ Steps to Done, 🔧 Resources Needing Repair, ⚠️ Risk of Delay
- **Footer**: timestamp, model name, token usage
- **Buttons**: "Close", "📋 Copy to Clipboard"
- Read-only (`state=tk.DISABLED`)

### 3.5 Progress Indication

While the LLM call is in flight:
- A small `tk.Toplevel` modal with a `ttk.Progressbar(mode='indeterminate')` and status label
- Text updates: "Preparing analysis..." → "Calling Azure OpenAI..." → "Saving result..."
- Modal is destroyed when analysis completes (success or error)
- Follows the existing `_update_status` pattern for thread-safe UI updates via `root.after(0, ...)`

### 3.6 Error Handling

| Error | User Experience |
|-------|----------------|
| Missing env vars (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`) | `messagebox.showerror` with setup instructions |
| Network timeout / API error | `messagebox.showerror` with error details |
| Rate limited (429) | `messagebox.showwarning` with "Try again in a moment" |
| LLM response unparseable | Show raw response in modal with warning banner |
| File write failure | Show analysis in modal + log warning (best-effort save) |

### 3.7 Threading Model

```
Main Thread                    Background Thread
───────────                    ─────────────────
_on_analyze_with_llm()
  ├─ look up item data
  ├─ show AnalysisProgressModal
  ├─ Thread(target=_do_analysis).start()
  │                            _do_analysis():
  │                              ├─ LLMConfig.from_env()
  │                              ├─ analyze_item(item, config)
  │                              ├─ save_analysis(result)
  │                              └─ root.after(0, _on_analysis_complete)
  │
_on_analysis_complete(result):
  ├─ close AnalysisProgressModal
  ├─ open AnalysisModal(result)
  └─ (or show error if failed)
```

---

## 4. Dependencies

### New Runtime Dependency

```toml
dependencies = [
    "accia-s360>=0.1.0",
    "openai>=1.0.0",
]
```

The `openai` package supports both OpenAI and Azure OpenAI via `AzureOpenAI` client. No additional Azure SDK needed.

### PyInstaller Impact

The `openai` package and its transitive deps (`httpx`, `pydantic`, etc.) must be included in the `.spec` file for the packaged build. This may increase the bundle size by ~5-10 MB.

---

## 5. Security Considerations

- API key read from environment variable only — never logged, never displayed in UI
- `LLMConfig.__repr__` masks the API key: `api_key=****`
- Action item data sent to Azure OpenAI stays within the Microsoft tenant (Azure OpenAI, not public OpenAI)
- No PII beyond what's already in the action item data (aliases, service names)

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM produces inaccurate analysis | User acts on wrong info | Include disclaimer footer: "AI-generated analysis — verify before acting" |
| Token limit exceeded for large items | API error or truncated response | Truncate input data to ~3000 tokens; prioritize key fields |
| Azure OpenAI endpoint changes | Feature breaks | Config via env vars makes endpoint easily updatable |
| `openai` package bloats PyInstaller build | Larger installer | Monitor size; consider lazy import if needed |
| Saved JSON format needs to evolve | Old files unreadable | `schema_version` field enables migration logic |

---

## 7. Future Considerations (Out of Scope)

- **SFI-021**: URL content enrichment — adds a `url_content` field to the prompt
- **SFI-022**: View saved analyses — adds "View Saved Analysis" to context menu
- Version history for analyses
- Configurable prompt templates
- Streaming response display
