# SFI-028 Review Comments
**Verdict: APPROVED** — Design is a clean swap from S360 search to Graph API. 

## Issue 1: Owner alias map must handle duplicates (INFO)
Multiple S360 services may list the same owner name with different aliases (rare but possible). Use first match.

## Issue 2: Graph API errors should fall back gracefully (SHOULD FIX)
If `get_manager_chain(alias)` raises `S360ApiError` for one owner, that owner should map to "Unknown Owner" rather than crashing the entire batch. The existing code already catches exceptions per-owner — keep that pattern.

## Architect Notes
- **Contract preserved**: `get_org_mapping()` signature and return type unchanged. Consumers (`aggregate_by_owner`, `aggregate_by_level2`, `collect_services_for_owner`) require no changes.
- **Signature change**: `get_org_mapping` needs owner aliases in addition to display names. Add `owner_aliases: dict[str, str]` parameter mapping display_name → alias.
- **Thread safety**: `S360Client` singleton is shared across `ThreadPoolExecutor` threads. Graph token acquisition in accia-s360 is already thread-safe (cached with expiry check).
- **Rollback safe**: Additive change to existing function. Revert tk_app.py to restore S360 behavior.
