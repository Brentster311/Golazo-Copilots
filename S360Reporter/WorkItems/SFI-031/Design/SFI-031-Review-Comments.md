# SFI-031 — Review Comments

## Design Review

### Clarity & Completeness
- Design is clear and well-scoped. Single function, single concern.
- Serialization format for `OrgTree`/`OrgPerson` dataclasses needs definition — the design doc says "convert to nested dicts" but should specify the exact schema so tests can assert structure.

### Feasibility
- Straightforward. All building blocks exist (`get_cache_dir`, `json`, `datetime`).
- `OrgTree` is a recursive dataclass — serialization must handle arbitrary depth. A simple recursive `_tree_to_dict` / `_dict_to_tree` pair suffices.

### Edge Cases
- Manager alias with mixed case (e.g., `BrentJ` vs `brentj`) — cache key should be normalized (`.lower()`).
- Empty `direct_reports` list in cached tree — must deserialize correctly as empty list, not `None`.

### Risks
- No new risks beyond those in the design doc. All mitigated.

### Verdict
**APPROVED** — no blocking issues. Proceed to Architect.

---

## Architect Notes

### Architectural Alignment
- Change is isolated to `services.py` — no new modules, no API surface changes. Good containment.
- Reuses `get_cache_dir()` from `cache.py` as the only cross-module dependency. No coupling issues.

### Data Contract (Cache File Schema)
```json
{
  "timestamp": "2026-02-11T10:30:00",
  "manager_alias": "brentj",
  "tree": {
    "person": {"alias": "...", "display_name": "...", "job_title": "...", "department": "...", "object_id": "..."},
    "direct_reports": [ ...recursive... ]
  }
}
```

### Security / Privacy
- Cache contains org hierarchy (names, aliases, titles). Stored in `tempdir/GUI/` — same location as existing caches. No new exposure surface.
- No credentials or tokens cached.

### Failure Isolation
- Cache read failure → fallback to API (existing behavior preserved).
- Cache write failure → logged warning, no user impact.
- Atomic write (temp file + rename) prevents partial writes.

### Verdict
**APPROVED** — architecturally sound. Proceed to Developer.
