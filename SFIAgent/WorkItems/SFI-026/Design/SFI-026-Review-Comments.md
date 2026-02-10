# SFI-026 — Design Review Comments

## Reviewer: Quality Assurance
## Date: 2025-07-24

---

## Overall Assessment
The design is **solid and well-grounded**. The phased approach (extend mapping → extend aggregation → extend treeview → extend drill-down) is the right sequence. A few gaps need addressing before implementation.

---

## Issues Found

### Issue 1: Drill-Down for Level-1 Owners Needs Org Mapping (Severity: High)

**Location**: Design Phase 4 (drill-down), current code at tk_app.py lines 2920-2953

**Problem**: The current drill-down in `_on_service_double_click()` matches by checking `owner_name in owners` against `service_owners`. For a Level-1 owner row (e.g., clicking "👤 muralic" in alexhowells' view), we need ALL services where the org_mapping maps the owner to muralic as the Level-1 ancestor — not just services directly owned by muralic.

**Current code** (line 2943):
```python
owner_services = {svc for svc, owners in service_owners.items() if owner_name in owners}
```

This only finds services where the raw `service_owners` dict contains the name. It does NOT look up the org_mapping to find all owners mapped to that Level-1 ancestor.

**Recommendation**: The drill-down must use the `org_mapping` to collect all owner aliases whose Level-1 ancestor matches the clicked owner, then collect all services owned by any of those aliases. The design doc should explicitly call this out.

### Issue 2: Return Type Backward Compatibility (Severity: Medium)

**Location**: Design Phase 1 (get_org_mapping return type)

**Problem**: The design proposes changing `get_org_mapping()` to return `{owner → (level1, level2)}` tuples. The current callers expect `{owner → str}`. Three call sites consume this:
1. `aggregate_by_owner()` at line ~477: `org_mapping.get(owner)` — expects a string
2. `_update_tables()` at line ~2819: `org_mapping.get(owner)` — expects a string
3. `do_refresh()` at line ~781: passes to `aggregate_by_owner`

**Recommendation**: Either:
- **(A)** Return a new structure (e.g., `OrgMapping` class or named tuple) so callers fail loudly at dev time, OR
- **(B)** Add a `hierarchy_depth` field to the return dict and keep the tuple approach but update all callers in the same PR

Option (A) is safer — a type change causes immediate failures rather than silent bugs.

### Issue 3: Manager's Own Services at Level-0 (Severity: Medium)

**Location**: Not addressed in design

**Problem**: SFI-014 fixed the case where the manager (e.g., muralic) owns services directly — they were falling to "Unknown Owner". The fix mapped `manager_alias → manager_alias`. For 2-level, if alexhowells directly owns a service, what is the mapping? `(alexhowells, None)`? This creates a Level-1 row for alexhowells themselves, which is conceptually correct but should be explicitly documented and tested.

**Recommendation**: Add an explicit handling rule in the design: "If the viewer directly owns a service, they appear as a Level-1 row with no Level-2 children."

### Issue 4: Level-1 Direct with No Sub-Reports (Severity: Low)

**Location**: Design Phase 3 (treeview)

**Problem**: If one of alexhowells' directs (e.g., muralic) has owner-service entries but ALL of muralic's service owners are muralic themselves (no sub-reports), the treeview should show "👤 muralic → services" (2-tier, same as today) rather than "👤 muralic → 👤 muralic → services" (redundant 3-tier).

**Recommendation**: Add a rule: if a Level-1 owner has no distinct Level-2 children (all mapped owners are the Level-1 direct themselves), collapse to 2-tier for that subtree.

### Issue 5: Sorting Across Levels (Severity: Low)

**Location**: Design Phase 3 (treeview)

**Problem**: The design doesn't specify sort order for Level-2 rows. Current Level-1 rows are sorted by count descending (line 2840). Level-2 rows should follow the same convention.

**Recommendation**: Explicitly state: "Level-1 rows sorted by total count descending. Level-2 sub-rows sorted by count descending within their parent."

---

## Positive Observations

1. **Same API calls**: Reusing existing management-chain data is the right call — no new API surface needed.
2. **Auto-detection of depth**: Elegant solution that avoids configuration complexity.
3. **Backward compatibility gate**: The 1-level code path preservation via "all level2 is None" check is sound.
4. **Capability impact analysis**: Only `reporter-tk-app` needs code changes — good scoping.

---

## Summary

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 1 | Drill-down needs org_mapping traversal | High | Update design Phase 4 |
| 2 | Return type backward compatibility | Medium | Adopt explicit type (Option A) |
| 3 | Manager's own services at Level-0 | Medium | Add handling rule to design |
| 4 | L1 direct with no sub-reports | Low | Add collapse rule |
| 5 | Sorting across levels | Low | Document sort order |

---

## Architect Notes (added during Architect review)

### Architectural Alignment
The change is **well-scoped to a single module** (tk_app.py). No new external dependencies, no new API surfaces, no persistence changes. The blast radius is limited to the Services treeview rendering and its drill-down — other tables (Programs, Action Items, KPIs) are unaffected.

### Data Contract: `get_org_mapping()` Return Type

**Current contract**: `dict[str, str]` — `{owner_name: direct_report_name}`

**Proposed contract**: `dict[str, tuple[str, str | None]]` — `{owner_name: (level1_name, level2_name)}`

**Recommendation**: Use a `NamedTuple` for the mapping value to make the contract self-documenting:

```python
from typing import NamedTuple, Optional

class OrgAncestry(NamedTuple):
    level1: str          # Viewer's direct report (or "Unknown Owner")
    level2: Optional[str]  # Sub-report under the direct, or None
```

**Why**: Positional tuples are fragile — `mapping[owner][0]` vs `mapping[owner].level1` communicates intent. The NamedTuple is zero-cost at runtime and backward-compatible with tuple unpacking.

### Contract Compatibility for Transitive Dependents

Per capability impact analysis:
- **reporter-build**: No contract change — just builds the same .exe
- **reporter-tests**: Tests will need updating for the new return type (covered in test cases)
- **reporter-web-app**: Does NOT use `get_org_mapping()` — no impact
- **reporter-eta-logic**: Independent of grouping — no impact
- **reporter-query-builder**: Independent of grouping — no impact

### Security & Privacy
- No new data exposed. The management chain data is already queried and displayed.
- Owner names are already visible in the UI. Adding Level-2 nesting doesn't expose additional PII.
- No new API scopes or auth changes needed.

### Failure Isolation
- If `get_org_mapping()` fails for any owner, that owner maps to `("Unknown Owner", None)` — same isolation as today.
- If the entire org mapping step fails, the code should fall back to the flat IC view (existing fallback branch at line ~2871).
- **New risk**: If the management chain returns an unexpectedly short chain (e.g., only contains the CEO and the manager), the level2 extraction should default to `None` rather than index out of bounds.

### Threading Safety
- The parallel `ThreadPoolExecutor` in `get_org_mapping()` writes to a shared `org_mapping` dict via a lock. The lock protects `dict[str] = str` writes today. With tuples, it's `dict[str] = tuple` — same thread-safety profile, no change needed.
- The `completed` counter increment is also lock-protected — unchanged.

### Default Behavior Audit
- **Tkinter Treeview `open=True`**: Currently all Level-1 owner rows start expanded (line 2841). For 2-level, consider:
  - Level-1 rows: `open=True` (expanded to show Level-2 children) — consistent with current behavior
  - Level-2 rows: `open=True` (expanded to show services) — matches Level-1 behavior at current depth
  - **Decision**: Keep `open=True` at both levels. Users can manually collapse if the tree is too long. This is the expected default for a "see everything at a glance" manager tool.

### Scalability Note
- Maximum observed org size is ~50 service owners across ~100 services. Even with 2-level nesting, the treeview will have at most ~60 rows (10 L1 + 50 L2/service). This is well within Tkinter Treeview performance limits (thousands of rows).

### No New User Stories Required
All QA issues (1-5) are implementable within the existing user story scope. No architectural changes or scope expansions needed.
