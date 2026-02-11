# SFI-027 Test Cases

**Work Item**: SFI-027 — MS Graph People Hierarchy  
**Date**: 2025-07-20  

---

## Test File: `accia-s360/tests/test_graph_endpoint.py`

All unit tests mock the Graph API responses. No live network calls.

---

### AC-1: `get_manager_chain(alias)` — Manager chain upward

| ID | Test Name | Description | Expected Result |
|----|-----------|-------------|-----------------|
| T01 | `test_get_manager_chain_returns_ordered_list` | Mock 3-level chain: user → mgr1 → mgr2 → CEO (404) | Returns `[OrgPerson(mgr1), OrgPerson(mgr2), OrgPerson(ceo)]` in order |
| T02 | `test_get_manager_chain_single_manager` | User's manager returns 404 on their manager call | Returns `[OrgPerson(manager)]` — single-element list |
| T03 | `test_get_manager_chain_ceo_has_no_manager` | Target is CEO — first `/manager` call returns 404 | Returns empty list `[]` |
| T04 | `test_get_manager_chain_org_person_fields` | Verify each OrgPerson has `display_name`, `alias`, `job_title`, `department`, `object_id` | All fields populated from Graph `$select` response |
| T05 | `test_get_manager_chain_alias_uses_upn_format` | Verify the request URL uses `{alias}@microsoft.com` | Request made to `/users/testalias@microsoft.com/manager` |
| T06 | `test_get_manager_chain_cycle_protection` | Mock a graph cycle: A→B→A | Terminates after detecting cycle, does not loop infinitely. Max 10 iterations. |

---

### AC-2: `get_direct_reports(alias)` — Direct reports with SC ALT filtering

| ID | Test Name | Description | Expected Result |
|----|-----------|-------------|-----------------|
| T07 | `test_get_direct_reports_returns_list` | Mock 3 direct reports, no SC ALTs | Returns 3 `OrgPerson` objects |
| T08 | `test_get_direct_reports_filters_sc_alt_by_alias` | Mock reports include alias `sc-pj467` | Filtered out — returned list excludes that entry |
| T09 | `test_get_direct_reports_filters_sc_alt_by_display_name` | Mock report with displayName containing "NON EA SC ALT" | Filtered out |
| T10 | `test_get_direct_reports_sc_alt_case_insensitive` | Aliases `SC-xxx`, `sc-xxx`, `Sc-xxx` all filtered | All three excluded |
| T11 | `test_get_direct_reports_exclude_sc_alts_false` | Call with `exclude_sc_alts=False` | SC ALT accounts included in results |
| T12 | `test_get_direct_reports_empty` | User has no direct reports | Returns empty list `[]` |
| T13 | `test_get_direct_reports_pagination` | Mock `@odata.nextLink` in first response, second page has more results | Both pages combined into single list |
| T14 | `test_get_direct_reports_org_person_fields` | Verify each OrgPerson from reports has all required fields | All fields populated correctly |

---

### AC-3: `get_org_tree(alias, depth)` — Nested org tree

| ID | Test Name | Description | Expected Result |
|----|-----------|-------------|-----------------|  
| T15 | `test_get_org_tree_default_depth_2` | Mock user with 2 directs, each with 2 sub-directs | Returns `OrgTree` with 2 levels of `direct_reports` |
| T16 | `test_get_org_tree_depth_0` | Call with `depth=0` | Returns `OrgTree` with person info only, `direct_reports=[]` |
| T17 | `test_get_org_tree_depth_1` | Call with `depth=1` | Returns person + direct reports, but directs have no sub-reports |
| T18 | `test_get_org_tree_filters_sc_alts` | Sub-tree contains SC ALT accounts | SC ALTs excluded at all levels |
| T19 | `test_get_org_tree_person_is_target_user` | Verify `OrgTree.person` is the target alias | `tree.person.alias == target_alias` |
| T20 | `test_get_org_tree_leaf_nodes_have_empty_reports` | Leaf-level people (at max depth) | `direct_reports == []` even if they have real reports |

---

### AC-4: Error handling and rate limiting

| ID | Test Name | Description | Expected Result |
|----|-----------|-------------|-----------------|
| T21 | `test_auth_error_raises_s360_auth_error` | Mock 401 response from Graph | Raises `S360AuthError` |
| T22 | `test_forbidden_raises_s360_auth_error` | Mock 403 response | Raises `S360AuthError` |
| T23 | `test_api_error_raises_s360_api_error` | Mock 500 response | Raises `S360ApiError` with status code |
| T24 | `test_rate_limit_429_retries` | Mock 429 then 200 on retry | Succeeds on retry, no exception raised |
| T25 | `test_rate_limit_respects_retry_after_header` | Mock 429 with `Retry-After: 2` header | Waits at least 2 seconds before retry (mock `time.sleep`) |
| T26 | `test_rate_limit_max_3_retries` | Mock 429 four consecutive times | Raises `S360ApiError` after 3 retries |
| T27 | `test_rate_limit_exponential_backoff` | Mock 429 three times then 200 | Sleep durations increase exponentially (verify via mock) |
| T28 | `test_network_error_raises_api_error` | Mock `requests.ConnectionError` | Raises `S360ApiError` |
| T29 | `test_timeout_raises_api_error` | Mock `requests.Timeout` | Raises `S360ApiError` |
| T30 | `test_user_not_found_404` | Mock 404 for a non-existent alias in `get_direct_reports` | Raises `S360ApiError` (not silently returns empty) |

---

### AC-5: Unit test infrastructure

| ID | Test Name | Description | Expected Result |
|----|-----------|-------------|-----------------|
| T31 | `test_org_person_from_graph_response` | Verify `OrgPerson.from_graph_response()` classmethod | Creates correct `OrgPerson` from raw dict |
| T32 | `test_org_person_from_graph_response_missing_fields` | Response missing `jobTitle`, `department` | Fields default to `None` |
| T33 | `test_org_tree_recursive_structure` | Build an `OrgTree` manually, verify nesting | `tree.direct_reports[0].direct_reports` is accessible |
| T34 | `test_graph_endpoint_uses_correct_select_params` | Verify `$select=displayName,mailNickname,jobTitle,department,id` | Request params include correct `$select` |

---

### AC-6: Live integration tests (separate file)

## Test File: `accia-s360/tests/test_graph_live.py`

These require real Azure CLI credentials. Mark with `@pytest.mark.live`.

| ID | Test Name | Description | Expected Result |
|----|-----------|-------------|-----------------|
| T35 | `test_live_get_manager_chain_muralic` | `get_manager_chain('muralic')` | Chain contains `alexhowells` |
| T36 | `test_live_get_direct_reports_muralic` | `get_direct_reports('muralic')` | Contains `brentj` |
| T37 | `test_live_get_direct_reports_excludes_sc_alts` | `get_direct_reports('muralic')` | No alias starts with `sc-` |
| T38 | `test_live_get_org_tree_muralic` | `get_org_tree('muralic', depth=1)` | Tree root is `muralic`, has direct reports |
| T39 | `test_live_manager_chain_reaches_ceo` | `get_manager_chain('muralic')` | Last person in chain is `satyan` |
| T40 | `test_live_get_manager_chain_unknown_alias` | `get_manager_chain('nonexistent_alias_zzz')` | Raises `S360ApiError` |

---

## Coverage Matrix

| AC | Test IDs | Count |
|----|----------|-------|
| AC-1 | T01–T06 | 6 |
| AC-2 | T07–T14 | 8 |
| AC-3 | T15–T20 | 6 |
| AC-4 | T21–T30 | 10 |
| AC-5 | T31–T34 | 4 |
| AC-6 | T35–T40 | 6 |
| **Total** | | **40** |

Every acceptance criterion has multiple tests covering happy path, edge cases, and error conditions.
