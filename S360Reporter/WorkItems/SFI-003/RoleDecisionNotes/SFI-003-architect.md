# SFI-003 Architect Notes

## Architectural Review Summary
Reviewed design and QA comments for S360Reporter Streamlit application.

## Key Architectural Decisions

### 1. Module Separation
Approved three-module structure:
- `app.py` - UI only (Streamlit components)
- `data.py` - API calls and data transformation
- `cache.py` - Local file caching

This enables unit testing of data and cache without Streamlit.

### 2. Caching Strategy
- File-based JSON cache in temp directory
- 1-hour expiration
- Per-user cache files
- Graceful fallback to API on cache failure

### 3. State Management
Must use `st.session_state` for:
- User alias persistence across reruns
- Cache data to avoid re-reading file
- Error state tracking

### 4. Security Considerations
- No credentials stored (Azure CLI)
- Cache is user-local, OS-protected
- Input validation on user alias
- No additional PII exposure beyond S360

## Implicit Assumptions Surfaced

| Assumption | Default Behavior | Recommendation |
|------------|------------------|----------------|
| Streamlit reruns | Every widget triggers rerun | Use session_state |
| Streamlit port | 8501 | Document, allow CLI override |
| File paths | OS-specific separators | Use pathlib.Path |
| JSON encoding | May vary | Explicit UTF-8 |

## Cross-Platform Requirements
- Use `pathlib.Path` for all file operations
- Use `tempfile.gettempdir()` for cache location
- Test on Windows and Mac/Linux

## Dependencies
- `streamlit>=1.30.0` - Stable
- `accia-s360>=0.1.0` - Internal (SFI-002)

## Data Contracts Defined
- UserInput: alias string
- ActionItemDisplay: display-ready action item
- CacheData: JSON-serializable cache structure

## Error Handling Strategy
- Catch specific exceptions (S360AuthError, S360ApiError)
- Show user-friendly messages via st.error()
- Log unexpected errors for debugging

## Decision
✅ **Approved for development**

## Recommendations for Developer
1. Use `st.session_state` for all persistent state
2. Use `pathlib.Path` for cross-platform paths
3. Show cache age prominently (color if > 30 min)
4. Validate user alias input (alphanumeric only)

## Next Role
Developer to implement application
