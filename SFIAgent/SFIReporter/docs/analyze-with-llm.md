# Analyze with LLM — Feature Overview

## Summary

The **Analyze with LLM** feature sends an SFI action item's data to Azure OpenAI
for a structured remediation analysis. The result includes four sections:
Mission, Steps to Done, Resources Needing Repair, and Risk of Delay.

Authentication uses **Azure CLI credential** (`az login`) — no API keys are needed.

## UML Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant UI as tk_app.py<br/>(Tkinter UI)
    participant Config as _load_llm_config()
    participant Progress as AnalysisProgressModal
    participant Thread as Background Thread
    participant Fetcher as fetch_action_item_urls()<br/>(llm_client.py)
    participant URLFetch as llm_extender.fetch_url()
    participant Prompt as build_prompt()<br/>(llm_client.py)
    participant Analyzer as analyze_item()<br/>(llm_client.py)
    participant AzCLI as AzureCliCredential<br/>(azure.identity)
    participant OpenAI as AzureOpenAI Client<br/>(openai SDK)
    participant Azure as Azure OpenAI<br/>API Endpoint
    participant Storage as save_analysis()<br/>(llm_storage.py)
    participant Result as AnalysisModal

    User->>UI: Right-click KPI row →<br/>"🤖 Analyze with LLM"
    UI->>Config: _load_llm_config()
    
    alt Saved config exists (settings.json)
        Config-->>UI: LLMConfig(endpoint, deployment, api_version)
    else No saved config
        Config->>Config: LLMConfig.from_env()<br/>reads AZURE_OPENAI_ENDPOINT
        Config-->>UI: LLMConfig from env vars
    end

    alt Config missing
        UI->>User: ❌ "LLM Configuration Required" error dialog
    end

    UI->>Progress: Show modal spinner<br/>"Analyzing..."
    UI->>Thread: threading.Thread(do_analysis).start()

    Note over Thread: ── Phase 1: URL Context Enrichment ──

    Thread->>Progress: update_status("Fetching URL context...")
    Thread->>Fetcher: fetch_action_item_urls(item)
    Fetcher->>Fetcher: _extract_urls(item)<br/>ResourceURIs, ActionWikiLink,<br/>CustomGroupingLink, AssetTypeLink0-2

    loop Each URL (up to 6 concurrent)
        Fetcher->>URLFetch: fetch_url(url, timeout=10)
        URLFetch-->>Fetcher: text content (or skip on failure)
    end

    Fetcher-->>Thread: dict[url → content]

    Note over Thread: ── Phase 2: LLM Call ──

    Thread->>Progress: update_status("Calling Azure OpenAI...")
    Thread->>Analyzer: analyze_item(item, config, url_content)
    Analyzer->>Prompt: build_prompt(item, url_content)

    Prompt->>Prompt: _format_item_for_prompt(item)<br/>Title, KPI ID, SLA, Dates,<br/>Ownership, Remediation, etc.
    Prompt->>Prompt: Append URL content sections<br/>(truncated to 1500 chars each)
    Prompt-->>Analyzer: [system_msg, user_msg]

    Analyzer->>AzCLI: get_bearer_token_provider(<br/>AzureCliCredential(),<br/>"cognitiveservices.azure.com/.default")
    AzCLI-->>Analyzer: token_provider callable

    Analyzer->>OpenAI: AzureOpenAI(<br/>azure_endpoint, azure_ad_token_provider,<br/>api_version)
    Analyzer->>OpenAI: chat.completions.create(<br/>model, messages,<br/>temperature=0.3,<br/>max_completion_tokens=2000)
    OpenAI->>Azure: POST /openai/deployments/{model}/chat/completions
    Azure-->>OpenAI: completion response
    OpenAI-->>Analyzer: response (choices, usage)

    Analyzer->>Analyzer: _parse_sections(response_text)<br/>→ mission, steps_to_done,<br/>resources, risk_of_delay
    Analyzer-->>Thread: AnalysisResult

    Note over Thread: ── Phase 3: Save & Display ──

    Thread->>Progress: update_status("Saving result...")
    Thread->>Storage: save_analysis(result)
    Storage->>Storage: Atomic write to<br/>%LOCALAPPDATA%/sfireporter/analyses/<br/>{action_item_id}.json
    Storage-->>Thread: saved path

    Thread->>UI: root.after(0, _on_analysis_complete)
    UI->>Progress: close()
    UI->>Result: AnalysisModal(root, result)
    Result->>User: Display structured analysis<br/>🎯 Mission<br/>✅ Steps to Done<br/>🔧 Resources Needing Repair<br/>⚠️ Risk of Delay

    Note over Thread,UI: ── Error Path ──

    alt LLMError or Exception
        Thread->>UI: root.after(0, _on_analysis_error)
        UI->>Progress: close()
        UI->>User: ❌ Error dialog with message
    end
```

## Key Components

| Component | File | Role |
|-----------|------|------|
| `_launch_llm_analysis()` | `tk_app.py` | Entry point — validates config, spawns background thread |
| `_load_llm_config()` | `tk_app.py` | Loads config from saved settings or env vars |
| `ConfigureLLMDialog` | `tk_app.py` | UI dialog to configure/detect endpoint settings |
| `fetch_action_item_urls()` | `llm_client.py` | Extracts & fetches URLs from action item fields |
| `build_prompt()` | `llm_client.py` | Constructs system + user messages for the LLM |
| `analyze_item()` | `llm_client.py` | Authenticates via Azure CLI, calls Azure OpenAI, parses response |
| `_parse_sections()` | `llm_client.py` | Splits LLM response into 4 named sections |
| `save_analysis()` | `llm_storage.py` | Atomic write of result to local JSON file |
| `AnalysisProgressModal` | `tk_app.py` | Spinner dialog shown during processing |
| `AnalysisModal` | `tk_app.py` | Displays the structured analysis result |

## Authentication

No API keys are used. The `AzureOpenAI` client authenticates via
`azure.identity.AzureCliCredential` with a token scoped to
`https://cognitiveservices.azure.com/.default`. Users must run `az login` first.

## Configuration Sources (priority order)

1. **Saved settings** — `%TEMP%/sfireporter/settings.json` (set via ⚙️ Configure LLM dialog)
2. **Environment variables** — `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`
