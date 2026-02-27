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

## S360 API Coverage

**Base URL:** `https://api.vnext.s360.msftcloudes.com/v1` (v2 endpoints use `/v2`)

### Action Items

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_eta_history(kpi_id, item_id)` | GET | `/ActionItems/GetEtaHistoryById` | Get ETA history for an action item |
| `save_etas(updates)` | POST | `/ActionItems/SaveETAsByIds` | Save ETA updates |
| `get_action_owner_history(kpi_id, item_id)` | GET | `/ActionItems/GetActionOwnerHistoryById` | Get action owner change history |
| `save_action_owners(payload)` | POST | `/ActionItems/SaveActionOwnersByIds` | Assign action owners to items |
| `get_customized_grid(payload)` | POST | `/ActionItems/GetCustomizedGrid` | Get customized action-items grid (columns + rows) |
| `query_grid_filters(payload)` | POST | `/ActionItems/QueryGridFilters` | Query available filter options for the grid |
| `get_details_summary(payload)` | POST | `/ActionItems/GetDetailsSummary` | Get action item details summary |
| `get_launch_criteria_summary(audience)` | POST | `/ActionItems/GetLaunchCriteriaSummary` | Get launch criteria summary |
| `get_action_items_summary(payload)` | POST | `/v2/ActionItems/ActionItemsSummary` | Get action items summary (v2) |
| `get_eta_and_annotation_data(payload)` | POST | `/v2/ActionItems/ETAAndAnnotationData` | Get ETA and annotation data (v2) |

### Common Components

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `search(text)` | GET | `/CommonComponents/GetSearchData` | Search for users, services, or other entities |
| `get_default_landing_view(alias)` | GET | `/CommonComponents/DefaultLandingView` | Get default landing view for a user |
| `get_all_action_item_metadata()` | GET | `/CommonComponents/GetAllActionItemMetadata` | Get all action item metadata |
| `get_all_kpi_action_item_type_metadata()` | GET | `/CommonComponents/GetAllKpiActionItemTypeMetadata` | Get all KPI action item type metadata |
| `query_people_hierarchy(audience)` | POST | `/CommonComponents/QueryPeopleHierarchyNodes` | Query people hierarchy nodes |
| `get_notification_alerts(type, count)` | POST | `/CommonComponents/GetNotificationAlerts` | Get notification/announcement alerts |
| `get_forums()` | GET | `/CommonComponents/GetForums` | Get all forums |
| `get_domains()` | GET | `/CommonComponents/GetDomains` | Get all domains |
| `get_action_items_per_policy(payload)` | POST | `/CommonComponents/GetAllActionItemPerPolicy` | Get action items grouped per policy |
| `get_user_search_groups(alias)` | GET | `/CommonComponents/graph/GetAllSearchGroups` | Get search groups for a user |

### KPIs & Costing

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `query_kpi_costs(kpi_ids)` | POST | `/Kpis/Costing/QueryCostOfKpis` | Query cost information for KPIs |
| `query_costing_notification_eligibility(payload)` | POST | `/Kpis/Costing/User/Notification/QueryEligibility` | Query costing notification eligibility |
| `get_kpi_target_type(kpi_id)` | GET | `/v2/Kpis/{kpiId}/TargetType` | Get KPI target type |
| `get_kpi_metadata_v2(kpi_id)` | GET | `/v2/Kpis/{kpiId}/Metadata` | Get KPI metadata |
| `get_all_kpis_metadata()` | GET | `/v2/Kpis/Metadata` | Get metadata for all KPIs |
| `query_kpi_metadata_fields(payload)` | POST | `/v2/Kpis/Metadata/QueryFields` | Query specific KPI metadata fields |

### Programs (v2)

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_programs()` | GET | `/v2/Programs` | Get all programs (objectives, KPIs, waves) |
| `get_programs(program_id)` | GET | `/v2/Programs/{programId}` | Get details for a single program |

### Code Transformations

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_code_transformation_scenarios()` | GET | `/CodeTransformations/Scenarios` | Get code transformation scenarios |
| `query_code_transformations(payload)` | POST | `/CodeTransformations/QueryCodeTransformations` | Query code transformations with filters |

### Feature Flags

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_kpi_feature_flags()` | GET | `/FeatureFlags/Kpis` | Get KPI feature flags |
| `query_feature_flags(audience)` | POST | `/FeatureFlags/QueryFeatureFlags` | Query feature flags for an audience |

### Reliability KPI

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_reliability_metadata()` | POST | `/ReliabilityKPI/GetReliabilityMetadata` | Get reliability KPI metadata |
| `get_reliability_kpi_values(payload)` | POST | `/ReliabilityKPI/GetReliabilityKPIValues` | Get reliability KPI values |

### KPI Priority

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_sub_services_priority_metadata(payload)` | POST | `/KpiPriority/GetSubServicesPriorityMetaData` | Get sub-services priority metadata |
| `query_audience_type(audience_ids)` | POST | `/KpiPriority/QueryAudienceType` | Query audience type |

### Other Endpoints

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_ado_work_item_metadata(kpi_id, target_id)` | GET | `/ADO/ADOWorkItemMetadata` | Get ADO work item metadata |
| `get_delegation_settings(alias)` | GET | `/Delegation/GetDelegationSettings` | Get delegation settings for a user |
| `get_kpi_security(kpi_id)` | GET | `/Onboarding/GetKpiSecurity` | Get KPI security/onboarding settings |
| `get_is_resolution_self_attested(kpi_id, item_id)` | GET | `/Attestations/GetIsResolutionSelfAttested` | Check if resolution is self-attested |
| `get_product_launch_summary()` | GET | `/Lifecycle/ProductLaunchSummary` | Get product launch summary |
| `get_quarantined_jobs()` | GET | `/v2/DataFactory/GetQuarantinedJobs` | Get quarantined data factory jobs |

### Microsoft Graph (Authentication & Org Hierarchy)

| Python Method | HTTP | URL Path | Description |
|---|---|---|---|
| `get_current_user()` | GET | `https://graph.microsoft.com/v1.0/me` | Get current user info via MS Graph |
| `get_manager_chain(alias)` | GET | `https://graph.microsoft.com/v1.0/users/{upn}/manager` | Walk manager chain upward to CEO |
| `get_direct_reports(alias)` | GET | `https://graph.microsoft.com/v1.0/users/{upn}/directReports` | Get direct reports (filters SC ALTs) |
| `get_org_tree(alias, depth=None)` | GET | (recursive directReports) | Build nested org tree (`None` = full tree) |

**Total: 43 API endpoints** (24 GET, 19 POST)

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

# Org hierarchy (via MS Graph)
chain = client.get_manager_chain("muralic")
for mgr in chain:
    print(f"{mgr.alias} — {mgr.display_name} ({mgr.job_title})")

reports = client.get_direct_reports("muralic")
tree = client.get_org_tree("muralic")  # full tree; use depth=2 to limit
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
