# SFI-012: Project Owner Assistant Role Notes

## Work Item Summary
User requested a feature to annotate columns in the column picker that have no data for any rows, helping users identify which columns won't be useful.

## User Story Creation
Created user story with 4 acceptance criteria:
1. Visual annotation on columns with no data
2. Clear "(empty)" indicator
3. Empty columns still toggleable
4. Non-empty columns unannotated

## Scope Decisions
- **In scope**: Visual annotation of empty columns at dialog open time
- **Out of scope**: 
  - Auto-hiding empty columns (user might want them)
  - Persisting empty state across sessions (computed fresh each time)
  - Column statistics (count of non-empty, etc.)

## Assumptions Made
1. **Visual indicator**: "(empty)" suffix - simple and clear
2. **Single item context**: Check is for current item being viewed
3. **Empty definition**: Column value is null, empty string, or None
