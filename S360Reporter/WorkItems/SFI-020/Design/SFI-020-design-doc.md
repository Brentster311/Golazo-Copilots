# SFI-020 Design Document

## Right-Click KPI Row → Analyze with LLM (Core)

| Field | Value |
|-------|-------|
| **Work Item** | SFI-020 |
| **Author** | Program Manager (Golazo) |
| **Status** | DRAFT |
| **Date** | 2026-02-06 |

---

## 1. Summary

Add a right-click "Analyze with LLM" option to KPI/Action Item rows in the S360Reporter desktop app. When triggered, the action item's structured data fields are sent to Azure OpenAI, which returns a structured analysis (Mission, Steps to Done, Resources Needing Repair, Risk of Delay). The result is displayed in a modal and automatically persisted as a JSON file under `%LOCALAPPDATA%`.

---

## 2. Problem Statement

SFI engineers must manually read through action item fields, follow links, and mentally synthesize what a KPI is asking, what steps are needed, which resources are affected, and how urgent it is. This is time-consuming and error-prone, especially across dozens of action items. There is no way to get a quick, structured summary of an action item's ask.

---

## 3. Business Case

| Dimension | Detail |
|-----------|--------|
| **Why now** | LLM APIs (Azure OpenAI) are stable and enterprise-approved; action item volume is growing |
| **Impact** | Reduces per-item triage time from 5–15 min to ~30 sec |
| **KPIs** | Analysis invocation count, avg response time, error rate |
| **Revenue/Cost** | Azure OpenAI pay-per-token cost (~$0.005/analysis est.) |

---

## 4. Stakeholders

| Role | Interest |
|------|----------|
| SFI Engineers | Primary users — need fast triage |
| SFI Managers | Benefit from team using tool efficiently |
| Security/Compliance | API key handling, data sent to LLM |

---

## 5. Functional Requirements

### FR-1: Right-Click Context Menu
- Bind `<Button-3>` on `self.tree_kpis` (main KPI treeview) and on the treeview inside `DetailModal` (drill-down)
- Show a `tk.Menu` with a single option: "🤖 Analyze with LLM"
- Menu appears at the clicked row; the row is selected on right-click

### FR-2: LLM Integration
- New module `sfi_reporter/llm_client.py`
- `LLMConfig` dataclass for Azure OpenAI settings (endpoint, API key, deployment, API version) sourced from environment variables
- `build_prompt(item: dict) → str` — constructs a structured prompt from action item fields
- `analyze_item(item: dict, config: LLMConfig) → AnalysisResult` — calls Azure OpenAI Chat Completions API
- `AnalysisResult` dataclass with fields: `mission`, `steps_to_done`, `resources_needing_repair`, `risk_of_delay`, `raw_response`, `timestamp`, `model`, `action_item_id`

### FR-3: Prompt Structure
System prompt instructs the LLM to return four labeled sections:
1. **Mission** — What is being asked
2. **Steps to Done** — Concise numbered steps to remediate
3. **Resources Needing Repair** — Specific resources/services affected
4. **Risk of Delay** — Business impact of not acting

Input data includes: title, status, SLA type, due date, ETA, owner, service name, service tree hierarchy, remediation text, clouds/environments, asset types.

### FR-4: Result Display
- New `AnalysisModal(tk.Toplevel)` — displays the four sections with labeled headers
- Scrollable text widget (consistent with `ItemDetailsModal` pattern)
- Shows model name, timestamp, and action item title in the header
- Copy-to-clipboard button for the full analysis text

### FR-5: Persistent Storage
- New module `sfi_reporter/llm_storage.py`
- Save path: `%LOCALAPPDATA%/GUI/analyses/<action_item_id>.json`
- JSON schema:
  ```json
  {
    "schema_version": 1,
    "action_item_id": "...",
    "action_item_title": "...",
    "analysis": {
      "mission": "...",
      "steps_to_done": "...",
      "resources_needing_repair": "...",
      "risk_of_delay": "..."
    },
    "model": "gpt-4o",
    "timestamp": "2026-02-06T12:00:00Z",
    "raw_response": "..."
  }
  ```
- Functions: `save_analysis(result: AnalysisResult)`, `load_analysis(action_item_id: str) → dict | None`, `analysis_exists(action_item_id: str) → bool`

### FR-6: Background Threading
- Follow the existing `_do_refresh` pattern: `threading.Thread(daemon=True)` + `root.after(0, callback)`
- Show a progress modal (`AnalysisProgressModal`) with a message like "Analyzing action item…" and a pulsing progress bar
- Disable the "Analyze with LLM" menu option while an analysis is in progress

---

## 6. Non-Functional Requirements

| NFR | Target |
|-----|--------|
| **Latency** | LLM response < 30s |
| **Security** | API key from env var only; never logged/displayed |
| **Persistence** | Valid JSON; survives reboots (uses `%LOCALAPPDATA%`) |
| **Compatibility** | Windows primary; Python ≥ 3.10 |
| **Dependency** | `openai>=1.0.0` (already added to pyproject.toml) |
| **Error handling** | Graceful degradation on LLM failure with user-visible error message |

---

## 7. Proposed Approach (High Level)

### New Files
| File | Purpose |
|------|---------|
| `GUI/src/sfi_reporter/llm_client.py` | LLMConfig, build_prompt, analyze_item, AnalysisResult |
| `GUI/src/sfi_reporter/llm_storage.py` | save_analysis, load_analysis, analysis_exists |

### Modified Files
| File | Changes |
|------|---------|
| `GUI/src/sfi_reporter/tk_app.py` | Add `<Button-3>` bindings, AnalysisModal, AnalysisProgressModal, context menu handler, `_analyze_with_llm()` method |
| `pyproject.toml` | Add `openai>=1.0.0` dependency |

### Architecture Flow
```
Right-click KPI row
  → tk.Menu("Analyze with LLM")
    → _analyze_with_llm(item_dict)
      → Show AnalysisProgressModal
      → threading.Thread:
          → build_prompt(item)
          → analyze_item(item, config)  # Azure OpenAI call
          → save_analysis(result)       # Write to %LOCALAPPDATA%
          → root.after(0, show_result)
            → Close AnalysisProgressModal
            → Open AnalysisModal(result)
```

### Environment Variables
| Variable | Purpose | Example |
|----------|---------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource URL | `https://my-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | API key | `sk-...` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4o` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-15-preview` |

---

## 8. Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| Local LLM (Ollama/llama.cpp) | Larger footprint; not enterprise-standardized; inconsistent quality |
| Sidebar panel instead of modal | More complex layout changes; modal is consistent with existing `ItemDetailsModal` pattern |
| Store analyses in SQLite | Over-engineered for this use case; JSON files are simpler and consistent with existing `CacheManager` pattern |
| Store analyses in `%TEMP%` | Volatile; user explicitly wants durability |

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Azure OpenAI rate limiting | Medium | Degraded UX | Show retry message; exponential backoff |
| API key not configured | High (first run) | Feature unusable | Clear error message with setup instructions |
| Token limit exceeded | Low | Truncated analysis | Limit prompt size; exclude low-value fields |
| Azure OpenAI cost overrun | Low | Budget impact | Token usage is minimal per call (~$0.005) |

---

## 10. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| `openai>=1.0.0` | Python package | Azure OpenAI client |
| Azure OpenAI resource | Cloud service | User must provision and configure |
| Existing `detail_items` data | Internal | Action item dicts from `data.py` |

---

## 11. Migration / Rollout / Rollback

| Phase | Action |
|-------|--------|
| **Rollout** | Feature is additive; ship with next S360Reporter build |
| **Rollback** | Remove context menu bindings + new modules; saved JSONs are inert |
| **Migration** | None — new feature, no existing data to migrate |

---

## 12. Observability Plan

| Signal | How |
|--------|-----|
| Analysis invocations | Counter logged per session |
| LLM response time | Logged per call (INFO level) |
| Errors | Logged with tracebacks (ERROR level) |
| Token usage | Logged per call from API response |

---

## 13. Test Strategy Summary

| Test Type | Scope |
|-----------|-------|
| **Unit** | `build_prompt` output structure, `LLMConfig` from env vars, `save/load/exists` storage operations |
| **Unit (mocked)** | `analyze_item` with mocked OpenAI client, error handling paths |
| **Integration** | Right-click binding fires handler, handler passes correct item data, modal displays result |
| **Manual** | End-to-end with live Azure OpenAI (smoke test) |
