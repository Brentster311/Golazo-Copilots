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
- **Column toggle**: Customize visible columns in drill-down views via "Columns" button
- **Empty column indicators**: Column picker shows "(empty)" suffix for columns with no data

## Requirements

- Python 3.10+
- Azure CLI authenticated (`az login`)
- accia-s360 package installed

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```
