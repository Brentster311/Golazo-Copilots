# S360Reporter

A desktop application to view and manage your SFI/QEI action items.

## Quick Start (Exe)

Download `S360Reporter.zip`, extract, and run **S360Reporter.exe**. No Python installation required.

The app will open a browser window for Microsoft login if no `az login` session is available.

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
- **Filter**: Curated filter builder (🔍 Filter button) — filter by Service Name, Assigned To, Program, Action Owner, Due Date, ETA Date (+ Service Owner for managers). Clauses persist across sessions.
- **In-app Azure login**: Uses `az login` session if available; otherwise opens a browser window for Microsoft login
- **Update ETAs**: Update ETAs and statuses for all items (Manual review) or auto-fix invalid ETAs (Bulk) from the home screen via 📋 Update ETAs button. Individual ETA editing available from the detail view (📅 Update ETA).
- **Drill-down ETA editing**: Each drill-down view (service, KPI, program, owner) has its own 📋 Update ETAs button. Multi-select rows and click "📋 Update ETAs for N selected" to update just those items.
- **View Details in Manual Review**: While stepping through items in Manual ETA review, click 🔍 View Details to see the full item detail modal.
- **SLA Status & ETA Status columns**: Drill-down views show SLA Status (In SLA / Approaching / Out of SLA) and ETA Status columns.
- **Diagnostic logging**: Rotating log file at `%TEMP%\GUI\\s360_reporter.log` (DEBUG+)
- **🤖 Analyze with LLM**: Right-click any KPI row → "Analyze with LLM" sends action item data to Azure OpenAI for a structured analysis (Mission, Steps to Done, Resources Needing Repair, Risk of Delay). Results are saved to `%LOCALAPPDATA%\GUI\\analyses\`.

## LLM Analysis Setup

To use the "Analyze with LLM" feature, set these environment variables:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o        (optional, defaults to gpt-4o)
AZURE_OPENAI_API_VERSION=2024-10-21   (optional)
```

## Requirements

- Azure CLI optional (app opens browser login if `az login` session unavailable)
