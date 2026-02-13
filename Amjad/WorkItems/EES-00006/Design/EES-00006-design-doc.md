# EES-00006 — Design Doc

## Summary

Add a Settings dialog to the EES GUI that allows configuring Azure OpenAI connection parameters (endpoint, deployment, API version). Settings are persisted to `settings.yaml` in the data directory and override environment variables when present.

## Problem Statement

Currently, Azure OpenAI settings must be configured as environment variables before launching the app. This is inconvenient for users who want to switch deployments, and requires terminal/shell knowledge.

## Business Case

- **Why now:** The GUI (EES-00005) is in place but requires env vars for LLM calls — this is the primary usability friction.
- **Impact:** Eliminates the need for users to manage environment variables.
- **KPIs:** User can launch the GUI and configure LLM access entirely within the app.

## Stakeholders

- Technical users running the EES GUI on Windows

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | File → Settings opens a modal Settings dialog |
| FR-2 | Dialog fields: Endpoint URL, Deployment Name, API Version |
| FR-3 | Dialog shows current effective value and source (config/env/default) for each field |
| FR-4 | Save button persists values to `data/settings.yaml` |
| FR-5 | On app launch, settings.yaml is loaded; values override env vars |
| FR-6 | Blank fields fall back to env vars, then built-in defaults |

## Non-Functional Requirements

- Settings file is human-readable YAML
- No encryption needed — local desktop app

## Proposed Approach

### 1. Settings Manager (`src/ees/gui/settings.py`)

A pure-Python class with no Tkinter dependency:
- `load(data_dir) -> dict` — reads `settings.yaml`, merges with env vars and defaults
- `save(data_dir, settings: dict)` — writes to `settings.yaml`
- `get_effective(key) -> (value, source)` — returns the value and where it came from

**Resolution order:** settings.yaml → env var → built-in default

**Built-in defaults:**
| Setting | Default |
|---------|---------|
| endpoint | `https://open-ai-poc.openai.azure.com/` |
| deployment | `gpt5.2` |
| api_version | `2025-12-11` |

### 2. Settings Dialog (`SettingsDialog` in `app.py`)

A `tk.Toplevel` modal dialog with:
- Three labeled entry fields (endpoint, deployment, api_version)
- Each field shows current effective value pre-filled
- Source label next to each field (e.g., "(from config)" / "(from env)" / "(default)")
- Save and Cancel buttons

### 3. FactExtractor Integration

Modify `FactExtractor.__init__()` to accept optional `endpoint`, `deployment`, `api_version` kwargs. When provided, they override env-var lookup. The GUI passes the effective settings to `FactExtractor`.

### 4. settings.yaml Format

```yaml
azure_openai:
  endpoint: "https://open-ai-poc.openai.azure.com/"
  deployment: "gpt5.2"
  api_version: "2025-12-11"
```

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| In-app env var fields (session only) | Not persistent across launches |
| JSON config | YAML is consistent with rest of project |
| Separate config file location | Data dir keeps everything together |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| User saves invalid endpoint | Validation happens at LLM call time; error message shown |
| Env var users confused by override | Source labels in dialog make precedence clear |

## Dependencies

- EES-00005 (GUI application) — complete

## Migration / Rollback

- Additive: if `settings.yaml` doesn't exist, env-var behavior is unchanged
- Deleting `settings.yaml` reverts to env-var-only mode

## Test Strategy

- Unit tests for `SettingsManager`: load/save/merge/fallback
- Unit tests for `FactExtractor` kwargs override
- Manual test: Settings dialog open/edit/save/relaunch cycle
