# SFI-028 Architect Notes
- `get_org_mapping` signature adds `owner_aliases: dict[str, str]` for name→alias mapping
- Thread safety: Graph token acquisition is thread-safe in accia-s360
- No new dependencies, no new security surface
