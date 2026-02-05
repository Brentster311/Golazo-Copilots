# SFI-003 Program Manager Notes

## Design Decisions

### Framework Selection
Selected **Streamlit** because:
- User confirmed preference
- Rapid development for data-focused apps
- Built-in components for tables, inputs, buttons
- No frontend expertise required

### Cache Strategy
- **JSON file** chosen for simplicity
- **1 hour expiration** balances freshness vs. API load
- **Per-user cache** prevents data leakage between users

### Project as Separate Repository
Recommendation: Create SFIReporter as a **new project** rather than subdirectory because:
- Clean separation of concerns
- Can have its own dependencies
- Easier to share/distribute

## Scope Boundaries

### In Scope
- View action items
- Auto-detect user
- Edit user alias
- Local caching

### Out of Scope (Future Iterations)
- Filtering by KPI type
- Exporting to Excel
- Editing items
- Historical trends

## Dependencies
- **Critical:** SFI-002 must be completed first
- accia-s360 package must be installable

## UI/UX Considerations
- Keep it simple for end users
- Color-coding for quick status identification
- Single-page layout, no navigation complexity

## Recommendations for QA
1. Test with users who have many services (performance)
2. Test with users who have zero items (empty state)
3. Test on Windows, Mac, Linux
4. Test cache invalidation
