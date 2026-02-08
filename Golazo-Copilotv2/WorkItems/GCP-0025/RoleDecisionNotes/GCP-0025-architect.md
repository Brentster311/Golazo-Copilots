# GCP-0025 Architect Notes

## Decision Log

### Architectural review completed

| Area | Status | Notes |
|------|--------|-------|
| API contracts | ✓ Defined | New ValidationResult dataclass |
| Security | ✓ No concerns | Local only |
| Scalability | ✓ Addressed | Caching, soft limits |
| Resilience | ✓ Fail open | Missing role files don't block |
| Dependencies | ✓ None new | Uses stdlib only |

### Key architectural decisions

1. **Fail open on missing/malformed role files**
   - Rationale: Meta-issues shouldn't block actual work
   - Implementation: Log warning, return empty outputs list

2. **Cache validation results per call**
   - Rationale: Same file checked multiple times in one transition
   - Implementation: Memoize within `validate_outputs()` call

3. **Soft limit of 10 outputs per role**
   - Rationale: Prevent performance issues with many git commands
   - Implementation: Log warning if exceeded, don't block

4. **Git command handling**
   - Timeout: 5 seconds (existing)
   - Encoding: UTF-8 explicit
   - Missing git: Skip git validations with warning

### Module structure

```
golazo_copilot/
├── core/
│   ├── output_validator.py  # NEW
│   ├── persistence.py
│   ├── checklists.py       # TO BE REMOVED (Phase 3)
│   ├── evidence.py         # TO BE REMOVED (Phase 3)
│   └── types.py
├── tools/
│   ├── gcp_transition.py   # MODIFY
│   ├── gcp_status.py       # MODIFY  
│   ├── gcp_mark.py         # TO BE REMOVED (Phase 3)
│   └── ...
└── server.py               # MODIFY (remove mark tools)
```

### No new user stories needed

Design is architecturally sound. Ready for development.
