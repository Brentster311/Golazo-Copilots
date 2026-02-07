# SFI Reporter

A desktop application to view your SFI/QEI action items.

## Installation

```bash
# Install dependencies
pip install -e .

# Or install with web (Streamlit) support
pip install -e ".[web]"

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Run the desktop app (Tkinter)
sfi-reporter
# or: python -m sfi_reporter.tk_app

# Or run the web app (Streamlit) - requires [web] extra
streamlit run src/sfi_reporter/app.py
```

## Features

- Native desktop window (no browser required)
- Auto-detects your user alias from Azure CLI
- Shows all SFI/QEI action items for your services
- Local caching for fast load times
- Color-coded cache age indicator
- **Detail modal color indicators**: Section headers use colored circle emojis (🔴 Status, 🔵 Dates, 🟣 Ownership, ⚫ Service & Program)
- **Column toggle**: Customize visible columns in drill-down views via "Columns" button
- **Empty column indicators**: Column picker shows "(empty)" suffix for columns with no data
- **KPI failure notification**: Orange warning when individual KPI fetches fail, with failed KPI names listed
- **Retry failed KPIs**: One-click retry for just the failed KPIs — recovered items merge into existing data
- **Filter**: Curated filter builder (\ud83d\udd0d Filter button) \u2014 filter by Service Name, Assigned To, Program, Action Owner, Due Date, ETA Date (+ Service Owner for managers). Apply filters the entire app; clauses persist across sessions.
- **In-app Azure login**: Automatically uses `az login` session if available; otherwise opens a browser window for Microsoft login \u2014 no external scripts needed- **Update ETAs**: Bulk or manual update of invalid ETAs/statuses from the main screen (📋 Update ETAs button); individual ETA editing from the detail view (📅 Update ETA button)- **Diagnostic logging**: Rotating log file at `%TEMP%\sfireporter\sfi_reporter.log` (DEBUG+)
- **🤖 Analyze with LLM**: Right-click any KPI row → "Analyze with LLM" sends action item data to Azure OpenAI for a structured analysis (Mission, Steps to Done, Resources Needing Repair, Risk of Delay). Results are saved to `%LOCALAPPDATA%\sfireporter\analyses\` for later review.

## LLM Analysis Setup

To use the "Analyze with LLM" feature, set these environment variables:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o        (optional, defaults to gpt-4o)
AZURE_OPENAI_API_VERSION=2024-10-21   (optional)
```

## Requirements

- Python 3.10+
- Azure CLI optional (app opens browser login if `az login` session unavailable)
- accia-s360 package installed

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```
