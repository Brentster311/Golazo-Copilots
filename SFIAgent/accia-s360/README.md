# accia-s360

Python client for Microsoft S360 API.

## Installation

```bash
# From Azure Artifacts
pip install accia-s360 --index-url https://pkgs.dev.azure.com/msazure/_packaging/ACCIA/pypi/simple/

# From source
pip install -e .
```

## Quick Start

```python
from accia_s360 import S360Client

# Initialize client (uses Azure CLI credentials)
client = S360Client()

# Get current user
user = client.get_current_user()
print(f"Logged in as: {user.alias}")

# Get action items
items = client.get_action_items({"pageSize": 100})
for item in items:
    print(f"- {item.get('kpiName')}: {item.get('dueDate')}")
```

## Authentication

This library uses Azure CLI credentials. Make sure you're logged in:

```bash
az login
```

## API Reference

### S360Client

Main client class for S360 API access.

```python
from accia_s360 import S360Client

client = S360Client()

# User operations
user = client.get_current_user()
landing_view = client.get_default_landing_view(user.alias)

# Action items
items = client.get_action_items(params)
grid = client.get_action_items_grid(kpi_id=kpi_id, audience=service_ids)

# KPI metadata
kpi = client.get_kpi(kpi_id)
all_metadata = client.get_all_action_item_metadata()
```

### Exceptions

```python
from accia_s360 import S360Error, S360AuthError, S360ApiError

try:
    client = S360Client()
except S360AuthError:
    print("Please run 'az login' to authenticate")
except S360ApiError as e:
    print(f"API error: {e}")
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build package
python -m build
```

## License

MIT
