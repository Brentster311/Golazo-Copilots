# SFI-026 — Test Cases

## Test Strategy
All tests use pytest with mocked S360 API responses. No live API calls.
Tests are organized by the function/component being tested, mapping to each acceptance criterion.

---

## 1. `get_org_mapping()` — Multi-Level Mapping (AC-1, AC-2, AC-3)

### TC-1.1: Two-Level Manager — Owner Two Levels Deep
**Setup**: Manager = alexhowells. Owner = brentj. Chain: `[CEO, ..., alexhowells, muralic, brentj]`
**Action**: Call `get_org_mapping(["Brent Jensen"], "alexhowells")`
**Expected**: `{"Brent Jensen": ("Muralic Name", "Brent Jensen")}` — level1=muralic, level2=brentj
**Failure msg**: "Owner 2 levels below manager should map to (direct, sub-report) tuple"

### TC-1.2: Two-Level Manager — Owner Is Direct Report
**Setup**: Manager = alexhowells. Owner = muralic. Chain: `[CEO, ..., alexhowells, muralic]`
**Action**: Call `get_org_mapping(["Muralic Name"], "alexhowells")`
**Expected**: `{"Muralic Name": ("Muralic Name", None)}` — level1=muralic, level2=None (they ARE the direct)
**Failure msg**: "Direct report should map to (self, None) tuple"

### TC-1.3: One-Level Manager — Owner Is Direct Report
**Setup**: Manager = muralic. Owner = brentj. Chain: `[CEO, ..., alexhowells, muralic, brentj]`
**Action**: Call `get_org_mapping(["Brent Jensen"], "muralic")`
**Expected**: `{"Brent Jensen": ("Brent Jensen", None)}` — level1=brentj, level2=None
**Failure msg**: "For 1-level manager, all owners should have level2=None (backward compatible)"

### TC-1.4: Owner Not in Manager's Org
**Setup**: Manager = alexhowells. Owner = "External Person". Chain does NOT contain alexhowells.
**Action**: Call `get_org_mapping(["External Person"], "alexhowells")`
**Expected**: `{"External Person": ("Unknown Owner", None)}`
**Failure msg**: "Owner outside manager's org should map to ('Unknown Owner', None)"

### TC-1.5: Manager's Own Services (SFI-014 Regression)
**Setup**: Manager = alexhowells. Owner = alexhowells. Chain: own alias = manager_alias.
**Action**: Call `get_org_mapping(["Alex Howells"], "alexhowells")`
**Expected**: `{"Alex Howells": ("Alex Howells", None)}` — self-maps as Level-1 with no Level-2
**Failure msg**: "Manager owning services directly should self-map to (self, None), not 'Unknown Owner'"

### TC-1.6: Owner Three Levels Deep (Beyond Scope)
**Setup**: Manager = alexhowells. Owner = "Deep Person". Chain: `[CEO, ..., alexhowells, muralic, brentj, deep_person]`
**Action**: Call `get_org_mapping(["Deep Person"], "alexhowells")`
**Expected**: `{"Deep Person": ("Muralic Name", "Brent Jensen")}` — maps to level1=muralic, level2=brentj (the 2-level ceiling)
**Failure msg**: "Owners deeper than 2 levels should map to the first 2 ancestors only"

### TC-1.7: Empty Owner List
**Setup**: No owners.
**Action**: Call `get_org_mapping([], "alexhowells")`
**Expected**: `{}`
**Failure msg**: "Empty owner list should return empty dict"

### TC-1.8: Multiple Owners — Parallel Without Errors
**Setup**: 10 owners, all with valid chains under alexhowells.
**Action**: Call `get_org_mapping([10 names], "alexhowells")`
**Expected**: All 10 mapped correctly; no threading errors.
**Failure msg**: "Parallel org mapping should handle multiple owners without race conditions"

---

## 2. `aggregate_by_owner()` — Two-Tier Rollup (AC-4)

### TC-2.1: Level-1 Stats Are Sum of All Level-2 Children
**Setup**: org_mapping maps 3 owners under muralic (level1) with varying level2 values. 10 action items across those owners.
**Action**: Call two-tier aggregate.
**Expected**: `level1_stats["Muralic Name"].count == 10` (sum of all children). Each level2 stat sums correctly.
**Failure msg**: "Level-1 stats must equal sum of all Level-2 children's stats"

### TC-2.2: SLA and Invalid ETA Roll Up Correctly at Both Levels
**Setup**: Items with mixed SLA/ETA statuses across multiple Level-2 owners.
**Action**: Call two-tier aggregate.
**Expected**: Level-1 sla = sum of all child sla. Level-1 invalid_eta = sum of all child invalid_eta. Same for Level-2.
**Failure msg**: "SLA and invalid ETA counts must roll up correctly at both levels"

### TC-2.3: Unknown Owner Bucket
**Setup**: Some items whose owners are not in org_mapping.
**Action**: Call two-tier aggregate.
**Expected**: Items assigned to `("Unknown Owner", None)`.
**Failure msg**: "Unmapped owners should fall into Unknown Owner bucket"

### TC-2.4: One-Level Manager — Backward Compatible
**Setup**: org_mapping where all level2 values are None (1-level manager scenario).
**Action**: Call two-tier aggregate.
**Expected**: level1_stats populated; no level2 entries with non-None level2.
**Failure msg**: "When all level2 are None, aggregate should behave identically to current 1-level logic"

---

## 3. `_update_tables()` — Treeview Rendering (AC-1, AC-2, AC-3)

### TC-3.1: Two-Level Manager — Three-Tier Treeview
**Setup**: Mock data with is_manager=True, org_mapping with mixed level1/level2 values.
**Action**: Call `_update_tables(data)`.
**Expected**: 
- Treeview root has Level-1 rows (👤 direct reports)
- Each Level-1 row has Level-2 children (👤 sub-reports) where applicable
- Each Level-2 row has service leaf rows
- Level-1 rows with no distinct Level-2 children show services directly (collapse rule)
**Failure msg**: "Two-level manager view must show 3-tier treeview with correct nesting"

### TC-3.2: One-Level Manager — Two-Tier Treeview (Regression)
**Setup**: Mock data with is_manager=True, org_mapping where all level2 are None.
**Action**: Call `_update_tables(data)`.
**Expected**: Same as current behavior — Level-1 owner rows → service rows. No Level-2 rows.
**Failure msg**: "One-level manager view must be unchanged from pre-SFI-026 behavior"

### TC-3.3: IC View — Flat List (Regression)
**Setup**: Mock data with is_manager=False.
**Action**: Call `_update_tables(data)`.
**Expected**: Flat list of services, no owner rows at all.
**Failure msg**: "IC view must remain flat with no grouping rows"

### TC-3.4: Counts Displayed on Owner Rows
**Setup**: Known item counts per Level-1 and Level-2.
**Action**: Call `_update_tables(data)`, inspect row values.
**Expected**: Each owner row's "count" column matches the aggregated count from the stats dict.
**Failure msg**: "Owner row counts must match aggregated stats"

### TC-3.5: Sort Order — Both Levels by Count Descending
**Setup**: Multiple Level-1 and Level-2 owners with varying counts.
**Action**: Call `_update_tables(data)`, inspect row order.
**Expected**: Level-1 rows sorted by total count desc. Within each Level-1, Level-2 rows sorted by count desc. Within each Level-2, services sorted by count desc.
**Failure msg**: "Rows at all levels must be sorted by count descending"

---

## 4. `_on_service_double_click()` — Drill-Down (AC-5, AC-6)

### TC-4.1: Double-Click Level-1 Owner — Shows All Subtree Items
**Setup**: Level-1 owner "muralic" has 3 Level-2 sub-reports, each with services.
**Action**: Simulate double-click on muralic's Level-1 row.
**Expected**: DetailModal shows ALL action items from ALL services under muralic's entire subtree (not just services directly owned by muralic).
**Failure msg**: "Level-1 drill-down must include ALL items from the entire subtree, not just directly owned services"

### TC-4.2: Double-Click Level-2 Owner — Shows That Owner's Items
**Setup**: Level-2 owner "brentj" owns 2 services.
**Action**: Simulate double-click on brentj's Level-2 row.
**Expected**: DetailModal shows only action items from brentj's services.
**Failure msg**: "Level-2 drill-down must show only that sub-report's service items"

### TC-4.3: Double-Click Service Row — Shows That Service's Items (Regression)
**Setup**: Any service row.
**Action**: Simulate double-click on service row.
**Expected**: DetailModal shows only that service's action items (unchanged behavior).
**Failure msg**: "Service row drill-down must not be affected by 2-level grouping"

### TC-4.4: Double-Click "Unknown Owner" Row
**Setup**: "Unknown Owner" at Level-1.
**Action**: Simulate double-click.
**Expected**: DetailModal shows items from services not in service_owners or not resolvable in org_mapping.
**Failure msg**: "Unknown Owner drill-down must show items from unmapped services"

---

## 5. Regression — SFI-014 Bug Fixes (AC-7)

### TC-5.1: Manager's Own Services Not "Unknown Owner"
**Setup**: Manager = muralic. muralic directly owns a service. 
**Action**: Full refresh and table update.
**Expected**: Service appears under "👤 Muralic Name" row, NOT under "Unknown Owner".
**Failure msg**: "SFI-014 regression: manager's own services must not appear under Unknown Owner"

### TC-5.2: Service Drill-Down Filter Correct After Grouping
**Setup**: Double-click a specific service row under an owner group.
**Action**: Check filtered items.
**Expected**: Only items matching that service_id, not all items under the owning group.
**Failure msg**: "SFI-014 regression: service drill-down must filter by service_id, not by owner"

---

## 6. Edge Cases

### TC-6.1: Owner Maps to Level-1 Direct Who Is Also Level-2 Owner
**Setup**: muralic (Level-1 direct of alexhowells) also directly owns services.
**Action**: Check treeview rendering.
**Expected**: Services owned directly by muralic appear under "👤 muralic" without a redundant Level-2 sub-row for muralic.
**Failure msg**: "When a Level-1 direct owns services directly, they should not appear as their own Level-2 child"

### TC-6.2: All Owners Under Single Level-1 Direct
**Setup**: alexhowells has 3 directs, but ALL services belong to owners under muralic.
**Action**: Check treeview.
**Expected**: Only "👤 muralic" Level-1 row shown (other directs have no services → not displayed). Level-2 rows under muralic.
**Failure msg**: "Directs with no services should not appear as empty Level-1 rows"

### TC-6.3: Mixed Depth — Some Owners Are L1 Directs, Some Are L2
**Setup**: alexhowells has directs A and B. A owns services directly (level2=None). B has sub-reports C and D who own services (level2=C, level2=D).
**Action**: Check treeview.
**Expected**: "👤 A" with services directly underneath (no Level-2). "👤 B" with "👤 C" and "👤 D" underneath, each with their services.
**Failure msg**: "Mixed depth must render correctly — some L1 with direct services, some L1 with L2 children"

---

## Coverage Matrix

| AC | Test Cases | Coverage |
|----|-----------|----------|
| AC-1 (2-level treeview) | TC-1.1, TC-1.2, TC-1.6, TC-3.1, TC-6.3 | Happy path + edge cases |
| AC-2 (1-level backward compat) | TC-1.3, TC-2.4, TC-3.2 | Regression |
| AC-3 (IC flat view) | TC-3.3 | Regression |
| AC-4 (Aggregated counts) | TC-2.1, TC-2.2, TC-2.3, TC-3.4 | Stats correctness |
| AC-5 (Owner drill-down) | TC-4.1, TC-4.2, TC-4.4 | Both levels + edge |
| AC-6 (Service drill-down) | TC-4.3, TC-5.2 | Regression |
| AC-7 (Unknown Owner) | TC-1.4, TC-2.3, TC-5.1, TC-4.4 | Edge + regression |
