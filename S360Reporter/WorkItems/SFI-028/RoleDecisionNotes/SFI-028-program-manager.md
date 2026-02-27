# SFI-028 PM Decision Notes
- Algorithm maps chain position to OrgAncestry using index math on `get_manager_chain()` output
- Owner alias resolution piggybacks on existing `get_service_owners()` S360 search (no extra calls)  
- Existing SFI-026 tests need mock updates but output semantics remain identical
