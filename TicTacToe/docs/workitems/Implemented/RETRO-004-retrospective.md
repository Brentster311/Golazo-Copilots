# Retrospective: RETRO-004 - Work Item Status Not Visible

**Status: ? IMPLEMENTED**

## Trigger
User asked "How can I tell which work items are implemented?" - there was no easy way to determine implementation status from user story documents.

## What Happened

### Current State (Before Fix)
- Retrospective documents have status headers: `**Status: ? IMPLEMENTED**`
- User Story documents have no status indicator
- Only way to determine status was to check if builder doc exists

### Root Cause
1. Status header pattern was established for RETROs but not applied to User Stories
2. No explicit requirement in Golazo instructions for status tracking
3. Inconsistency between RETRO and WIP document formats

## Impact

- Difficult to quickly assess project backlog state
- Must check multiple files to determine if work item is complete
- Inconsistent document formatting between RETROs and WIPs

## Resolution

1. Added status header to all existing User Story documents
2. Updated Golazo instructions to require status in User Story template

## Process Improvement Proposal

### Change: Add Status to User Story Template

Update Project Owner section to include status in template:

```markdown
### 1) Project Owner — User Story

If the request is not already a user story, convert it into the following format:

**Status**: ?? BACKLOG | ?? IN PROGRESS | ? IMPLEMENTED

**User Story**
- Title:
- As a:
...
```

### Status Values
| Status | Meaning |
|--------|---------|
| ?? BACKLOG | Work item created, not yet started |
| ?? IN PROGRESS | Currently being implemented |
| ? IMPLEMENTED | All Golazo roles complete, Builder verified |

## Files Updated

| File | Status Added |
|------|--------------|
| `docs\workitems\WIP-001-user-story.md` | ? IMPLEMENTED |
| `docs\workitems\WIP-002-user-story.md` | ? IMPLEMENTED |
| `docs\workitems\WIP-003-user-story.md` | ?? BACKLOG |
| `docs\workitems\WIP-004-user-story.md` | ?? BACKLOG |
| `docs\workitems\WIP-005-user-story.md` | ?? BACKLOG |
| `docs\workitems\WIP-006-user-story.md` | ?? BACKLOG |
| `docs\workitems\WIP-007-user-story.md` | ?? BACKLOG |

## Lessons Learned

1. Document format consistency matters for project visibility
2. Status tracking should be built into templates from the start
3. Patterns established in one document type should be considered for others
