# SFI-028 Test Cases

## Primary verification: Existing SFI-026 tests (30 tests)
All 30 tests in `test_sfi_026.py` must pass. These test `OrgAncestry`, `get_org_mapping`, `aggregate_by_owner`, `aggregate_by_level2`, and `collect_services_for_owner`. Mock updates may be needed to provide `get_manager_chain` instead of `search`.

## New test cases for Graph-based get_org_mapping

| ID | Test | Expected |
|----|------|----------|
| T1 | `get_org_mapping` calls `get_manager_chain` not `search` for hierarchy | `get_manager_chain` called per owner |
| T2 | Owner whose chain contains manager_alias at position 0 → direct report | `OrgAncestry(owner_name, None)` |
| T3 | Owner 2 hops deep → level1=direct, level2=owner | `OrgAncestry(direct_name, owner_name)` |
| T4 | Owner 3+ hops → capped at 2 levels | `OrgAncestry(direct_name, sub_name)` |
| T5 | Owner not in manager's org → Unknown Owner | `OrgAncestry("Unknown Owner", None)` |
| T6 | Graph API error for one owner → graceful fallback | `OrgAncestry("Unknown Owner", None)` for that owner, others unaffected |
| T7 | Owner IS the manager → self-mapping | `OrgAncestry(self_name, None)` |
