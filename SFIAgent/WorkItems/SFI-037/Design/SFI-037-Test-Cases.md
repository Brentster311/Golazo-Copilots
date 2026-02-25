# SFI-037 — Test Cases

## AC-1: Cost data fetched during refresh

### TC-037-01: Successful cost fetch
- **Setup:** Mock `get_action_items_summary` to return 3 KPIs; mock `query_kpi_costs` to return cost data for all 3.
- **Action:** Call `fetch_kpi_costs(kpi_ids)`.
- **Expected:** Returns `{"kpi-1": 180.0, "kpi-2": 1054.0, "kpi-3": 1962.0}`.
- **Failure msg:** "Cost map should contain all 3 KPI IDs with correct minute values"

### TC-037-02: Cost API returns partial data
- **Setup:** Query 3 KPI IDs; mock returns cost for only 2.
- **Action:** Call `fetch_kpi_costs(kpi_ids)`.
- **Expected:** Returns map with 2 entries. Missing KPI not in map.
- **Failure msg:** "Cost map should contain only KPIs with data, missing KPIs absent"

### TC-037-03: Cost API fails entirely
- **Setup:** Mock `query_kpi_costs` to raise an exception.
- **Action:** Call `fetch_kpi_costs(kpi_ids)`.
- **Expected:** Returns empty dict `{}`. No exception propagates.
- **Failure msg:** "Cost fetch failure should return empty dict, not raise"

### TC-037-04: Empty KPI list
- **Setup:** No KPI IDs.
- **Action:** Call `fetch_kpi_costs([])`.
- **Expected:** Returns `{}` without calling the API.
- **Failure msg:** "Empty KPI list should short-circuit and return empty dict"

## AC-2: Services view shows cost column

### TC-037-05: Service row cost = sum(kpi_cost × item_count)
- **Setup:** Service "SvcA" has 2 KPIs: KPI-1 (cost=180, items=3) and KPI-2 (cost=1054, items=2).
- **Action:** Compute `compute_row_cost(service_items, kpi_cost_map)`.
- **Expected:** `180*3 + 1054*2 = 2648`.
- **Failure msg:** "Service cost should be sum of (kpi_cost × item_count) across all KPIs"

### TC-037-06: Service with no cost data shows dash
- **Setup:** Service has items but no KPI IDs in cost map.
- **Action:** Compute and format cost.
- **Expected:** Display value is "—".
- **Failure msg:** "Service with no cost data should display '—'"

## AC-3: KPIs view shows cost column

### TC-037-07: KPI row cost = kpi_cost × item_count
- **Setup:** KPI-1 has cost=180, item_count=5.
- **Action:** Compute KPI row cost.
- **Expected:** `180*5 = 900`.
- **Failure msg:** "KPI row cost should be kpi_cost × item_count"

## AC-4: Programs view shows cost column

### TC-037-08: Program row sums costs across all items in program
- **Setup:** Program has items from KPI-1 (cost=180, 2 items) and KPI-2 (cost=1054, 1 item).
- **Action:** Compute program row cost.
- **Expected:** `180*2 + 1054*1 = 1414`.
- **Failure msg:** "Program cost should sum across all KPI items in the program"

## AC-5: Owners view shows cost column

### TC-037-09: Owner row sums costs for all owned items
- **Setup:** Owner "Alice" owns items from KPI-1 (cost=180, 3 items).
- **Action:** Compute owner row cost.
- **Expected:** `180*3 = 540`.
- **Failure msg:** "Owner cost should sum costs for all items under that owner"

## AC-6: Drill-down shows per-item cost

### TC-037-10: Individual item shows its KPI's AverageCostInMin
- **Setup:** Item belongs to KPI-1 with cost=180.
- **Action:** Get item cost.
- **Expected:** `180`.
- **Failure msg:** "Individual item cost should equal its KPI's AverageCostInMin"

## AC-7: Graceful degradation

### TC-037-11: Missing KPI shows dash, doesn't break sum
- **Setup:** 3 items: KPI-1 (cost=180), KPI-2 (no cost), KPI-3 (cost=1054).
- **Action:** Compute row cost for all 3 items.
- **Expected:** `180 + 0 + 1054 = 1234`. KPI-2 contributes 0, not "—".
- **Failure msg:** "Items with missing cost should contribute 0 to sums"

### TC-037-12: Format with thousands separator
- **Setup:** Cost = 12500.
- **Action:** Format for display.
- **Expected:** `"12,500"`.
- **Failure msg:** "Cost should be formatted with thousands separator"

### TC-037-13: Zero cost shows 0, not dash
- **Setup:** KPI has cost=0 in the cost map (present but zero).
- **Action:** Format for display.
- **Expected:** `"0"`.
- **Failure msg:** "Zero cost should display '0', not '—'"
