# SFI-027 — Program Manager Decision Notes

## Design Decisions

### Module placement: `endpoints/graph.py`
Follows existing pattern — `extended.py`, `action_items.py`, `discovery.py` are all under `endpoints/`. The new `GraphEndpoint` class parallels `ExtendedEndpoints`.

### Separate models module: `models/org.py`
OrgPerson and OrgTree are standalone data classes that may be used by multiple consumers. Keeping them in a models package avoids circular imports and makes them importable independently.

### UPN format: `{alias}@microsoft.com`
Graph API accepts UPN (User Principal Name) for user lookups. All Microsoft full-time employees use `alias@microsoft.com`. POC confirmed this works.

### Depth parameter default: 2
SFI-026 needs viewer → directs → directs' directs (2 levels). Making it configurable avoids a breaking change if future consumers need deeper trees.

### No caching in library
accia-s360 is a client library — caching strategy belongs to consumers. SFIReporter already has its own cache layer. Adding caching here would create staleness issues and complicate the API.

### SC ALT filter as default-on parameter
SC ALT accounts are never useful for org hierarchy. Default filter ON with option to disable (`exclude_sc_alts=True`).

## Rejected Approaches
- Combining `get_manager_chain` and `get_direct_reports` into a single method: they serve different use cases and callers shouldn't pay for both when they only need one direction.
- Using `$expand=directReports` on the user query: doesn't support recursive expansion and limits `$select` on expanded entities.
