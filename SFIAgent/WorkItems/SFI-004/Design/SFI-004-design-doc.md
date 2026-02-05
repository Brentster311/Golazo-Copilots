# Design Doc: SFI-004 - SFIReporter Flet Desktop App

## Summary
Convert SFIReporter from Streamlit web application to Flet native Windows desktop application while maintaining feature parity.

## Problem Statement
The current Streamlit implementation requires:
1. Running a web server process
2. Opening a browser tab
3. Port management (localhost:8501)

Users want a simpler experience: double-click to launch a native window.

## Business Case
- **Why now:** Immediate feedback from SFI-003 deployment
- **Impact:** Improved user experience, reduced friction
- **KPIs:** Launch time, user adoption

## Stakeholders
- Service owners (primary users)
- brentj (developer/owner)

## Functional Requirements
| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | Launch as native window | User Story |
| FR-2 | Auto-detect user alias | AC-2 |
| FR-3 | Editable user alias field | AC-2 |
| FR-4 | Refresh data button | AC-3 |
| FR-5 | Display services table | AC-4 |
| FR-6 | Display action items table | AC-5 |
| FR-7 | Show cache age indicator | AC-6 |
| FR-8 | Clear cache button | AC-7 |

## Non-Functional Requirements
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-1 | Resizable window | Manual test |
| NFR-2 | Fast startup | < 3s with cache |
| NFR-3 | Responsive during fetch | Loading indicator visible |

## Proposed Approach

### Architecture
```
sfi_reporter/
├── __init__.py      # (existing)
├── cache.py         # (existing, reuse)
├── data.py          # (existing, reuse)
├── app.py           # (REPLACE: Streamlit → Flet)
└── flet_app.py      # (NEW: Flet implementation)
```

### Key Design Decisions

1. **Keep Both Implementations**: Create `flet_app.py` alongside `app.py` to allow choice
2. **Shared Core**: cache.py and data.py are framework-agnostic
3. **Entry Point**: Update pyproject.toml to use Flet version as default

### Flet UI Components
| Component | Flet Widget |
|-----------|-------------|
| User alias input | `ft.TextField` |
| Refresh button | `ft.ElevatedButton` |
| Services table | `ft.DataTable` |
| Action items table | `ft.DataTable` |
| Cache age | `ft.Text` with conditional color |
| Loading indicator | `ft.ProgressRing` |

### Threading Model
- UI runs on main thread
- Data fetching in background thread via `threading.Thread`
- UI updates via `page.update()` callback

## Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Flet | Modern, easy, can build to web later | Newer framework | ✅ Selected |
| PyQt6 | Mature, full-featured | Complex, GPL license | Rejected |
| Tkinter | Built-in | Dated appearance | Rejected |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Flet version incompatibility | Build failure | Pin version in pyproject.toml |
| Threading issues | UI freeze | Use proper thread synchronization |

## Dependencies
- flet >= 0.21.0
- accia-s360 (SFI-002)
- Existing cache.py, data.py modules

## Migration / Rollout Plan
1. Add flet dependency to pyproject.toml
2. Create flet_app.py with Flet implementation
3. Update entry point to use Flet version
4. Keep Streamlit version available as fallback

## Rollback Plan
- Revert entry point to use Streamlit app.py
- No data migration needed (same cache format)

## Observability Plan
- Console logging for debugging
- No telemetry in first iteration

## Test Strategy
- Unit tests for UI components (if feasible)
- Manual integration testing
- Verify all acceptance criteria
