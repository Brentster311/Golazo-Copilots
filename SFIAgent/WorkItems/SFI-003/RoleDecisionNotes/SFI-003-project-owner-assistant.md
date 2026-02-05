# SFI-003 Project Owner Assistant Notes

## Work Item Summary
Create a new Streamlit web application (SFIReporter) that displays SFI/QEI action items for the current user's services.

## Scope Decisions

### Included
- Auto-detect current user from Azure CLI
- Editable user alias text box
- Display all SFI/QEI items in a table
- Local caching for performance

### Excluded
- Editing action items (read-only view)
- Multi-user support
- Export functionality
- Detailed filtering

## Assumptions Made
1. **Streamlit** - User confirmed web interface preference
2. **Cross-platform** - User confirmed
3. **Local cache** - User confirmed; will use JSON in temp directory
4. **End users** - Non-technical users, so UI should be simple
5. **Dependency on SFI-002** - Must use accia-s360 package

## Questions Resolved
- Interface: Streamlit web app (user confirmed)
- Platform: Cross-platform (user confirmed)
- Cache: Local (user confirmed)
- Users: End users / non-technical (user confirmed)

## User Flow
1. User runs `streamlit run app.py`
2. App auto-detects user alias from Azure CLI
3. App displays alias in editable text box
4. App fetches and displays all SFI/QEI items for user's services
5. User can change alias and click refresh to see different user's items

## Risks
- Dependency on SFI-002 being completed first
- Azure CLI must be authenticated before running
- Large number of action items may slow down the UI

## Next Role
Program Manager to create design document for application architecture.
