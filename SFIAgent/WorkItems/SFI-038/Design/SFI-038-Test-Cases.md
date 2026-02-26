# SFI-038 — Test Cases

## TC-1: CSV Loading
### TC-1.1: `load_kpi_scores` returns dict keyed by KPI name
- Input: Valid kpi.csv with 3 rows
- Expected: Dict with 3 entries, values are integers

### TC-1.2: `load_kpi_scores` handles missing CSV gracefully
- Input: Non-existent file path
- Expected: Returns empty dict, no exception

### TC-1.3: `load_kpi_scores` also provides KPIID-keyed lookup
- Input: Valid kpi.csv
- Expected: Can look up by KPIID (GUID)

## TC-2: Score Computation
### TC-2.1: KPI score = KPIScore × count
- Input: KPI with score=93, count=16
- Expected: score = 1488

### TC-2.2: Missing KPI defaults to score 0
- Input: KPI name not in CSV
- Expected: score = 0

### TC-2.3: KPI with score=0 returns 0
- Input: KPI with score=0, count=5
- Expected: score = 0

## TC-3: Service Aggregation
### TC-3.1: Service score = sum of per-KPI scores
- Input: Service with 2 KPIs (score 93×10=930, score 80×5=400)
- Expected: service score = 1330

## TC-4: Program Aggregation
### TC-4.1: Program score = sum of per-KPI scores across services in that program
- Input: Program with items from 2 KPIs
- Expected: program score = sum of both KPI scores

## TC-5: Integration
### TC-5.1: `_update_tables` includes score column values
- Input: Mock data with kpi_stats containing score field
- Expected: Treeview insert calls include score values

### TC-5.2: format_score formats with comma separator
- Input: 1488
- Expected: "1,488"
