# SFI-003 Design Review Comments

## Overall Assessment
✅ **APPROVED** - Design is clear and appropriate for a Streamlit application. Minor recommendations below.

---

## Clarity and Completeness

### ✅ Strengths
- UI wireframe is clear and helpful
- Data flow is well-documented
- Cache strategy is appropriate

### ⚠️ Recommendations

1. **Empty State Handling**
   - Design should specify what to show when user has zero items
   - Recommendation: Show "No action items found" message
   
2. **Error State UI**
   - Design mentions error handling but not UI representation
   - Recommendation: Use `st.error()` for clear error messages

---

## Feasibility and Sequencing

### ✅ Strengths
- Dependency on SFI-002 is clearly stated
- Technology stack is appropriate

### ⚠️ Recommendations

1. **Fallback for Missing accia-s360**
   - If package not installed, show clear installation instructions
   
2. **First-Run Experience**
   - Document behavior when Azure CLI is not authenticated

---

## Risk Coverage

### ✅ Addressed
- API rate limiting mentioned
- Performance with many items considered

### ⚠️ Missing

1. **Stale Cache Warning**
   - Risk: User viewing old data without realizing
   - Mitigation: Show cache age prominently, color-code if > 30 min old

2. **Session State Management**
   - Risk: Streamlit reruns can cause unexpected behavior
   - Mitigation: Use `st.session_state` for user alias and cache

---

## Edge Cases and Failure Modes

### Must Handle

1. **No Azure CLI installed**
   - Show: "Azure CLI not found. Please install from https://aka.ms/azure-cli"

2. **Azure CLI not authenticated**
   - Show: "Please run 'az login' to authenticate"

3. **User has no services**
   - Show: "No services found for this user in ServiceTree"

4. **S360 API timeout**
   - Show: "S360 API is slow to respond. Please try again."

5. **Invalid user alias entered**
   - Show: "User 'xyz' not found. Please check the alias."

---

## Performance Considerations

### ✅ Good
- 1-hour cache is reasonable
- Local JSON cache is fast

### ⚠️ Recommendation
- Consider showing cached data immediately, then refreshing in background
- This provides instant feedback while keeping data fresh

---

## Naming Clarity

### ✅ Good
- `S360Reporter` is descriptive
- File names are clear

### ⚠️ Recommendation
- Consider `sfi_reporter` (snake_case) for Python package name consistency

---

## Folder Structure

### ✅ Approved
- Structure follows Python best practices
- Separation of app.py, cache.py, data.py is appropriate

---

## Sign-off
- **Reviewer:** QA Role
- **Date:** 2026-02-04
- **Status:** Approved with recommendations

---

# Architect Notes

## Architectural Review
**Status:** ✅ APPROVED for implementation

## Architectural Alignment

### Application Boundaries
- **Clear:** Single-purpose application (view SFI/QEI items)
- **Good:** Clean separation of data fetching, caching, and UI
- **Dependency:** Properly depends on accia-s360 for API access

### Module Responsibilities
```
sfi_reporter/
├── app.py      # Streamlit UI only, no business logic
├── data.py     # Data fetching and transformation
└── cache.py    # Cache read/write/validation
```

This separation allows:
- Testing data.py and cache.py independently
- Replacing UI framework if needed (unlikely but possible)

## Security & Privacy

### ✅ Addressed
- Uses Azure CLI credentials (no credentials in app)
- Local cache only (no server-side data storage)

### ⚠️ Recommendations

1. **Cache Location Security**
   - Cache stored in temp directory is readable by same user only (OS enforced)
   - Document: "Cache may contain service names and user aliases"
   
2. **No Sensitive Data in UI**
   - Action items shown are already visible to user in S360
   - No additional exposure

3. **User Input Validation**
   - Sanitize user alias input before API call
   - Prevent injection (though S360 API likely handles this)

## Data Contracts

### Input Contract (User → App)
```python
@dataclass
class UserInput:
    alias: str  # Azure AD alias, e.g., "brentj"
```

### Output Contract (App → UI)
```python
@dataclass
class ActionItemDisplay:
    kpi_name: str
    service_name: str
    due_date: str  # ISO format
    status: str  # "Overdue", "Due Soon", "On Track"
    cloud: str
```

### Cache Contract
```python
@dataclass
class CacheData:
    timestamp: str  # ISO format
    user_alias: str
    services: list[dict]
    action_items: list[dict]
```

## Streamlit Implicit Assumptions

| Assumption | Default Behavior | Recommendation |
|------------|------------------|----------------|
| Reruns | Every interaction triggers full rerun | Use `st.session_state` |
| Caching | `@st.cache_data` has 10min TTL | Use explicit TTL or file cache |
| Secrets | `.streamlit/secrets.toml` | Not needed (using Azure CLI) |
| Port | 8501 | Document, allow override via CLI |

## Dependency Review

| Dependency | Version | Risk | Notes |
|------------|---------|------|-------|
| streamlit | >=1.30.0 | Low | Stable, well-maintained |
| accia-s360 | >=0.1.0 | Medium | Internal package, SFI-002 |

## Failure Isolation

### Blast Radius
- **Minimal:** Local application, no shared state
- **Cache failure:** Falls back to live API call
- **API failure:** Shows error message, doesn't crash

### Error Handling Strategy
```python
try:
    data = fetch_from_api()
except S360AuthError:
    st.error("Please run 'az login' to authenticate")
except S360ApiError as e:
    st.error(f"S360 API error: {e}")
except Exception as e:
    st.error(f"Unexpected error: {e}")
    logging.exception("Unhandled error")
```

## Scalability Notes
- N/A for local application
- If many users needed: Consider deploying to Azure App Service (future work item)

## Cross-Platform Considerations
- **File paths:** Use `pathlib.Path` for cross-platform compatibility
- **Temp directory:** Use `tempfile.gettempdir()` (works on all OS)
- **Encoding:** Explicit UTF-8 for JSON read/write

## Final Recommendation
✅ **Proceed to Developer role**

Recommendations to implement:
1. Use `st.session_state` for user alias persistence
2. Use `pathlib.Path` for all file operations
3. Add input validation for user alias
4. Show cache age prominently in UI

---

## Architect Sign-off
- **Architect:** Architect Role
- **Date:** 2026-02-04
- **Decision:** Approved for development