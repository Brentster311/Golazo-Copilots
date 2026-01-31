# GolazoCPV2 - Golazo Copilot Version 2

## Overview

Programmatic workflow enforcement agent for GitHub Copilot.

## Installation

```bash
pip install -e .
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Project Structure

```
GolazoCPV2/
??? src/
?   ??? golazo/
?       ??? __init__.py
?       ??? state.py        # GCP2-003: State management
??? tests/
?   ??? test_state.py       # GCP2-003: State tests
??? WorkItems/              # Golazo workflow artifacts
??? pyproject.toml
??? README.md
```
