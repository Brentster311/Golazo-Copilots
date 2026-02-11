# LLM-0012 — Program Manager Decision Notes

## Key Design Decisions

### 1. 403-based filtering over explicit RBAC check
Instead of calling the Authorization API to check role assignments (which requires `azure-mgmt-authorization` and understanding inherited roles), we simply attempt to list deployments. A 403 means "skip this resource." This is the pattern used by Azure Portal itself and avoids a significant dependency.

### 2. New module `discovery.py` rather than adding to `client.py`
Keeps `client.py` focused on the LLM facade. Discovery is a separate concern with different dependencies. The `LLMClient.discover()` classmethod is a thin delegation.

### 3. Subscription enumeration via `azure-mgmt-resource`
We need to list all subscriptions the user has access to. `azure-mgmt-resource.SubscriptionClient` is the standard way. The `subscription_id` filter parameter lets users skip the enumeration if they know their target.

### 4. Optional dependency group name
Chose `[azure-discover]` to be specific. Could also be `[azure]` to bundle all Azure-related optional deps, but that's a broader change for a future story.
