# S360 Client

A Python library for direct access to Microsoft S360 (Service 360) APIs.

## Features

- **Azure CLI Authentication**: Uses your existing `az login` session for seamless authentication
- **40+ S360 API Endpoints**: Comprehensive coverage of S360 v1 and v2 APIs
- **API Discovery**: Probe and discover additional S360 API endpoints
- **Local Caching**: Cache API responses to reduce load and improve performance
- **Type Safety**: Full type hints throughout the codebase
- **Comprehensive Error Handling**: Clear error messages for auth, API, and cache failures

## Installation

### From Source (Development)

```bash
# Clone the repository
cd SFIAgent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Prerequisites

1. **Azure CLI**: Install from https://docs.microsoft.com/cli/azure/install-azure-cli
2. **Azure Login**: Run `az login` to authenticate with your Microsoft account
3. **Python 3.10+**: Required for type hint syntax

## Quick Start

```python
from s360_client import S360Client

# Initialize client (uses default configuration)
client = S360Client()

# Test connection
status = client.test_connection()
print(f"S360 Auth: {status['s360_auth']}")
print(f"User: {status.get('user_alias', 'N/A')}")

# Get current user info
user = client.get_current_user()
print(f"Logged in as: {user.display_name} ({user.alias})")

# Search for services or users
results = client.search("EventHawk")
for item in results:
    print(f"{item['Name']} ({item['Group']})")

# Get forums and domains
forums = client.get_forums()
domains = client.get_domains()
print(f"Found {len(forums['Forums'])} forums, {len(domains['Domains'])} domains")

# Get action items summary
summary = client.get_action_items_summary(audience=["brentj"])
print(f"Programs: {len(summary.get('ProgramsLookup', {}))}")

# Get ETA history for an action item
history = client.get_eta_history(
    kpi_id="your-kpi-id",
    action_item_id="your-action-item-id"
)
for item in history:
    print(f"ETA: {item.eta}, Status: {item.status}, Notes: {item.notes}")

# Save an ETA update
from datetime import datetime, timezone

result = client.save_eta(
    kpi_id="your-kpi-id",
    service_id="your-service-id",
    action_item_id="your-action-item-id",
    new_eta=datetime(2026, 3, 15, tzinfo=timezone.utc),
    notes="Updated via S360 Client",
)
print(f"Save successful: {result.success}")

# Get KPI costs
costs = client.get_kpi_costs(["kpi-id-1", "kpi-id-2"])

# Get reliability KPI data
reliability = client.get_reliability_kpi_values(audience=["your-service-id"])

# Discover available endpoints
endpoints = client.discover_endpoints()
for ep in endpoints:
    print(f"{ep.method} {ep.path} - {ep.description}")
```

## Configuration

```python
from s360_client import S360Client, S360Config
from pathlib import Path

config = S360Config(
    # API Settings
    base_url="https://api.vnext.s360.msftcloudes.com/v1",  # Default
    timeout_seconds=30,  # Request timeout
    retry_count=1,  # Retries on transient failures
    
    # Cache Settings
    cache_enabled=True,
    cache_expiry_minutes=60,
    cache_directory=Path("./my_cache"),  # Custom cache location
    
    # Logging
    log_level="INFO",  # DEBUG, INFO, WARNING, ERROR
)

client = S360Client(config)
```

## API Reference

### S360Client

#### Core Methods

| Method | Description |
|--------|-------------|
| `get_current_user()` | Get authenticated user info |
| `get_eta_history(kpi_id, action_item_id)` | Get ETA history for action item |
| `save_eta(...)` | Save a single ETA update |
| `save_etas(updates)` | Save multiple ETA updates |
| `discover_endpoints()` | Discover available API endpoints |
| `get_swagger_spec()` | Try to retrieve OpenAPI spec |
| `test_connection()` | Test auth and API connectivity |
| `clear_cache()` | Clear all cached data |

#### Search & Discovery

| Method | Description |
|--------|-------------|
| `search(search_text)` | Search for users, services, or entities |
| `get_action_owner_history(kpi_id, action_item_id)` | Get owner history for action item |
| `save_action_owners(...)` | Save action owners for action items |

#### Action Items Grid

| Method | Description |
|--------|-------------|
| `get_action_items_grid(kpi_id, audience, ...)` | Get customized action items grid data |
| `query_grid_filters(kpi_id, audience, ...)` | Query available grid filter options |

#### KPI & Costs

| Method | Description |
|--------|-------------|
| `get_kpi_costs(kpi_ids)` | Query cost information for KPIs |
| `get_ado_metadata(kpi_id, target_id)` | Get Azure DevOps work item metadata |
| `get_code_transformations(...)` | Query code transformations |

#### Common Components

| Method | Description |
|--------|-------------|
| `get_notification_alerts()` | Get notification alerts |
| `get_forums()` | Get all forums |
| `get_domains()` | Get all domains (Security, Reliability, etc.) |
| `get_action_items_per_policy(...)` | Get action items per policy |
| `get_user_search_groups(user_alias)` | Get search groups for a user |
| `get_default_landing_view(user_alias)` | Get default landing view for user |
| `get_all_action_item_metadata()` | Get all action item metadata |
| `query_people_hierarchy(audience)` | Query people hierarchy nodes |

#### Feature Flags

| Method | Description |
|--------|-------------|
| `get_kpi_feature_flags()` | Get KPI feature flags configuration |
| `query_feature_flags(audience)` | Query feature flags for audience |

#### Reliability KPI

| Method | Description |
|--------|-------------|
| `get_reliability_metadata()` | Get reliability KPI metadata |
| `get_reliability_kpi_values(audience, ...)` | Get reliability KPI values |

#### Action Items v2 API

| Method | Description |
|--------|-------------|
| `get_action_items_summary(audience, ...)` | Get action items summary (v2) |
| `get_eta_and_annotation_data(audience, ...)` | Get ETA and annotation data (v2) |
| `get_launch_criteria_summary(audience)` | Get launch criteria summary |

#### KPI Priority

| Method | Description |
|--------|-------------|
| `get_sub_services_priority_metadata(audience, ...)` | Get sub-services priority metadata |
| `query_audience_type(audience_ids)` | Query audience type |

#### Other

| Method | Description |
|--------|-------------|
| `get_product_launch_summary()` | Get product launch summary |
| `get_quarantined_jobs()` | Get quarantined data factory jobs (v2) |
| `query_costing_notification_eligibility(target_ids, ...)` | Query costing notification eligibility |

### Models

- `UserInfo`: User identity information
- `EtaHistoryItem`: Single ETA history entry
- `EtaUpdate`: Request model for saving ETAs
- `SaveResult`: Result of save operations
- `EndpointInfo`: Discovered endpoint information

### Exceptions

- `S360Error`: Base exception
- `S360AuthError`: Authentication/authorization failures
- `S360ApiError`: API call failures
- `S360CacheError`: Cache operation failures

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/s360_client --cov-report=html

# Run only unit tests (no az login required)
pytest tests/ -v -m "not integration"
```

## Cache Location

By default, cache files are stored in:
- **Windows**: `%LOCALAPPDATA%\s360_client\cache\`
- **Linux/Mac**: `~/.cache/s360_client/cache/`

⚠️ **Warning**: Do not commit cache files to version control. They may contain sensitive data.

## Troubleshooting

### "Azure CLI not logged in"
```bash
az login
```

### "Access denied" / 403 errors
- Ensure your account has access to S360
- Try `az login` again to refresh your session

### Cache issues
```python
client.clear_cache()  # Clear all cached data
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD)
4. Implement the feature
5. Submit a pull request
