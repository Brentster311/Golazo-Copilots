# GCP-0003: Architect Decision Notes

**Note**: This document was created retroactively to complete the artifact trail.

## Architecture Review

- Checklist state stored in state.json
- DoR and DoD are separate tools for clarity
- Resources provide read-only access

## API Contracts

```python
async def gcp_mark_dor(
    work_item_id: str,
    item: str = None,      # Single item
    items: dict = None,    # Bulk items
    complete: bool = True
) -> dict

async def gcp_mark_dod(...)  # Same pattern
```

## Approved

Clean separation between DoR and DoD tools.
