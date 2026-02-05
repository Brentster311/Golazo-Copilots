# SFI-003 Design Document: SFIReporter Streamlit Application

## Summary
Create a Streamlit web application that auto-detects the current user and displays all SFI/QEI action items for services they own, with local caching for performance.

## Problem Statement
Service owners need to check their SFI/QEI compliance status across multiple services. Currently this requires:
- Navigating to the S360 portal
- Manually filtering by each service
- No easy way to see aggregated view across all owned services

End users need a simple, self-service tool to quickly view their compliance status.

## Business Case

### Why Now
- SFI compliance is critical and time-sensitive
- Team members need quick access to their action items
- Reduces time spent navigating S360 portal

### Impact
- Faster identification of overdue items
- Better visibility for service owners
- Enables proactive compliance management

### KPIs
- Application loads in < 10 seconds (with cache)
- User can view all their items with one click
- Zero training required for end users

## Stakeholders
- **Owner:** Brent Jensen
- **Users:** ACCIA service owners and team members

## Functional Requirements
1. Auto-detect current user's alias from Azure CLI
2. Display alias in editable text box
3. Fetch all SFI/QEI items for user's services
4. Display items in sortable table
5. Show loading state during data fetch
6. Cache data locally with 1-hour expiration
7. Allow manual refresh of data

## Non-Functional Requirements
1. Cross-platform (Windows, Mac, Linux)
2. Initial load < 10 seconds with cache
3. Simple UI for non-technical users
4. Works on standard 1920x1080 displays

## Proposed Approach

### Technology Stack
- **Framework:** Streamlit 1.30+
- **S360 Client:** accia-s360 (SFI-002)
- **Cache:** JSON file in user's temp directory
- **Auth:** Azure CLI credentials (via accia-s360)

### Application Structure
```
SFIReporter/
├── pyproject.toml
├── README.md
├── src/
│   └── sfireporter/
│       ├── __init__.py
│       ├── app.py              # Main Streamlit app
│       ├── cache.py            # Local caching logic
│       └── data.py             # Data fetching/transformation
└── tests/
    └── test_cache.py
```

### User Interface Wireframe
```
┌─────────────────────────────────────────────────────────────┐
│  SFI Reporter                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: [brentj________] [🔄 Refresh]                        │
│                                                             │
│  Services: ACCIA Model Hosting, EventHawk Detection, ...    │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ KPI Name          │ Service    │ Due Date │ Status     ││
│  ├───────────────────┼────────────┼──────────┼────────────┤│
│  │ 1.05 Azure Tenant │ Azure Core │ 2025-12  │ 🔴 Overdue ││
│  │ Watson Onboarding │ EventHawk  │ 2026-03  │ 🟡 Due Soon││
│  │ ...               │ ...        │ ...      │ ...        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  Last refreshed: 2026-02-04 10:30 AM                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
1. App starts → Check cache
2. If cache valid (< 1 hour old) → Load from cache
3. If cache invalid → Fetch from S360 API → Save to cache
4. Transform data for display
5. Render in Streamlit table

### Cache Strategy
- **Location:** `{tempdir}/sfireporter/{user_alias}_cache.json`
- **Expiration:** 1 hour
- **Contents:** User info, services, action items
- **Invalidation:** Manual refresh button or cache expiry

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| CLI application | Simple, scriptable | Not user-friendly for end users | Rejected |
| Flask/Django web app | Full control | More complex, needs deployment | Rejected |
| Streamlit | Quick development, good UI | Limited customization | **Selected** |
| Power BI dashboard | Rich visualizations | Requires separate infrastructure | Rejected |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Azure CLI not authenticated | Medium | High | Show clear error message with instructions |
| S360 API rate limiting | Low | Medium | Cache aggressively, respect API limits |
| Large number of items slows UI | Low | Medium | Paginate or limit initial display |
| accia-s360 not available | Medium | High | Document dependency, version pinning |

## Open Questions
1. Should we show all items or just out-of-SLA? (Recommendation: All, with filter option)
2. Should we color-code by SLA status? (Recommendation: Yes, red/yellow/green)

## Dependencies
- **SFI-002:** accia-s360 package must be published first
- **Azure CLI:** Must be installed and authenticated
- **Python 3.10+:** Required for accia-s360

## Migration / Rollout Plan

### Phase 1: Development
1. Create project structure
2. Implement core data fetching
3. Build Streamlit UI
4. Add caching layer
5. Test locally

### Phase 2: Distribution
1. Share via Git repository
2. Document installation: `pip install -e .` then `streamlit run`
3. Optional: Publish to Azure Artifacts for easier distribution

## Rollback Plan
- Not applicable (standalone app, no deployment)
- Users can revert to previous Git commit if issues

## Observability Plan
- Display "Last refreshed" timestamp in UI
- Show error messages for API failures
- Log cache hits/misses to console (debug mode)

## Test Strategy Summary
1. **Unit tests:** Cache expiration logic, data transformation
2. **Integration tests:** S360 API connectivity (requires credentials)
3. **Manual testing:** UI verification, cross-platform testing
