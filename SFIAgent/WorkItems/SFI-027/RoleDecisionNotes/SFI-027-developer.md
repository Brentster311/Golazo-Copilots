# SFI-027 Developer Decision Notes

**Role**: Developer  
**Date**: 2025-07-20  

## Implementation Summary

### Files Created
- `accia-s360/src/accia_s360/endpoints/graph.py` — `GraphEndpoint` class (3 public methods + retry helper)
- `accia-s360/tests/test_graph_endpoint.py` — 34 unit tests (all mocked)
- `accia-s360/tests/test_graph_live.py` — 6 live integration tests (`@pytest.mark.live`)

### Files Modified
- `accia-s360/src/accia_s360/models.py` — Added `OrgPerson`, `OrgTree` dataclasses
- `accia-s360/src/accia_s360/__init__.py` — Export `OrgPerson`, `OrgTree`
- `accia-s360/src/accia_s360/endpoints/__init__.py` — Export `GraphEndpoint`
- `accia-s360/src/accia_s360/client.py` — Added `_graph` instance, 3 delegate methods

## TDD Cycle
1. Wrote 34 unit tests (red phase) — tests imported `GraphEndpoint` before it existed
2. Added `OrgPerson`/`OrgTree` models to `models.py`
3. Implemented `GraphEndpoint` in `graph.py`
4. First run: 31/34 passed, 3 failed (CEO-vs-user-not-found 404 disambiguation mock issue)
5. Fixed test mocks to account for the verify-user-exists call
6. Final: **34/34 unit tests pass, 63/63 total accia-s360 tests pass (0.65s)**

## Key Implementation Decisions

### 1. 404 disambiguation
The biggest implementation decision was how to distinguish "CEO has no manager" (valid 404) from "user doesn't exist" (error 404). Solution: when the first `/manager` call returns 404 and the chain is empty, issue a verification `GET /users/{upn}` call. If that 404s too → user not found error. If 200 → user is CEO, return empty chain.

### 2. Retry-After parsing
`int(resp.headers.get("Retry-After", str(2 ** attempt)))` — uses Retry-After header when present, falls back to exponential backoff (1s, 2s, 4s).

### 3. Pagination via full URL
`@odata.nextLink` returns fully qualified URLs from Graph. The `while url:` loop in `get_direct_reports` passes these directly to `_graph_get`. On first call, we construct the URL; for subsequent pages, we use the nextLink as-is.

### 4. SC ALT detection in model
`OrgPerson.is_sc_alt()` method on the dataclass keeps the filtering logic close to the data model rather than scattering regex checks across endpoint code.

### 5. Keyword-only params
`exclude_sc_alts` and `depth` are keyword-only (using `*` separator) per architect decision, preventing positional misuse.

## Test Results
```
63 passed in 0.65s
```
- 34 new GraphEndpoint tests (T01–T34)
- 29 existing tests — zero regressions
- 6 live tests defined (not run — require Azure CLI auth)

## Acceptance Criteria Status
| AC | Status | Evidence |
|----|--------|----------|
| AC-1 | ✅ | T01–T06: manager chain ordered, fields, UPN format, cycle protection |
| AC-2 | ✅ | T07–T14: direct reports, SC ALT filtering, pagination |
| AC-3 | ✅ | T15–T20: org tree depth control, SC ALT filtering, leaf nodes |
| AC-4 | ✅ | T21–T30: auth errors, API errors, 429 retry, network failures |
| AC-5 | ✅ | T31–T34: model factory, missing fields, recursive structure, $select params |
| AC-6 | ✅ | T35–T40 defined in test_graph_live.py (require live Azure CLI credentials) |
