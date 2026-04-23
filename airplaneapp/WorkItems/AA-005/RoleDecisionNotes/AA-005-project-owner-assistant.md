# AA-005 — Project Owner Assistant Decision Notes

## Scope Decision
AA-005 delivers maintenance scheduling with pre-loaded FAA intervals, editable schedules, tech-only completion, and in-app alerting. This is the most regulation-heavy feature and a core value proposition of the app.

## Why This Scope
- Maintenance compliance is the #2 priority feature (after Hobbs tracking) per the brainstorm.
- The auto-provisioning of FAA schedules differentiates this app — users don't have to manually set up every interval.
- Document/photo uploads were split out to keep AC count manageable (5 ACs). This can be a fast follow-up (AA-005b).
- FAA AD database import is a complex integration that deserves its own work item — for now, ADs can be added as custom maintenance items manually.

## Key Design Decisions
- **Auto-provisioning:** When an aircraft is created, the system seeds 6 standard FAA maintenance items. This happens at the database/service level, not requiring admin action.
- **Dual tracking (hours + calendar):** Some items track by Hobbs hours (100-hr, oil change) and others by calendar (annual, transponder, ELT, pitot-static). The maintenance item model stores `intervalType` (hobbs | calendar | both) and the interval value.
- **10% alert threshold:** Per brainstorm. For a 100-hour inspection, alert at 90 hours (10 hours remaining). For a 12-month annual, alert at ~328 days (~36 days remaining). The threshold is stored per-item so it can be customized.
- **Append-only completion log:** When a tech marks an item complete, a MaintenanceLog record is created with the date and Hobbs at completion. The maintenance item's `lastCompletedAt` and `lastCompletedHobbs` are updated. History is never deleted.

## Decomposition Note
Document/photo uploads for maintenance records were deferred. If the user wants them, they should be scoped as:
- **AA-005b (future):** Maintenance Record Document & Photo Uploads

## Dependency Chain
AA-005 requires both AA-003 (aircraft model) and AA-004 (current Hobbs values for hours-based calculations).
