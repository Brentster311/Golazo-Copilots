# KustoMapper

A Windows GUI tool for discovering and visualizing table relationships in Azure Data Explorer (Kusto) clusters.

## Features

- **MCDEMO-001**: Connect to Kusto clusters and discover tables with their schemas
- **MCDEMO-002**: Detect relationships between tables based on column naming patterns
- **MCDEMO-003**: Visualize relationships as a graph (coming soon)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install accia-datacollection from Azure Artifacts
pip install --extra-index-url https://pkgs.dev.azure.com/msazure/One/_packaging/azinsights_accia_pkgs/pypi/simple/ accia-datacollection>=1.2.8
```

## Usage

```bash
# Run the GUI
cd KustoMapper
set PYTHONPATH=src
python -m kustomapper
```

## Requirements

- Python 3.9+
- Azure CLI (authenticated via `az login`)

## Project Structure

```
KustoMapper/
├── src/kustomapper/
│   ├── adapters/      # Data source adapters (Kusto, future: SQL, etc.)
│   ├── cache/         # Schema caching
│   ├── gui/           # tkinter GUI
│   └── models/        # Data models
├── tests/             # Unit tests
└── WorkItems/         # Golazo workflow artifacts
```

## Running Tests

```bash
cd KustoMapper
set PYTHONPATH=src
python -m pytest tests/ -v
```

## Architecture

The application uses a three-layer architecture:
1. **GUI Layer**: tkinter-based window for user interaction
2. **Adapter Layer**: `DataSourceAdapter` ABC for extensibility
3. **Cache Layer**: JSON-based local caching of schema metadata
