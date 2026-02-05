# SFI-007: Project Owner Assistant Notes

## Date: 2026-02-04

## Request Analysis
User requested a full details view when double-clicking a row in the drill-down modal from SFI-006.

## Data Available
From the cached `detailed_items`, each action item has 30 fields:

**Core Identity:**
- `id` - Unique action item identifier (hash)
- `title` - Action item title
- `_kpi_id` - KPI identifier

**Ownership:**
- `assignedTo` - Assigned user alias
- `S360_AssignedTo` - S360-specific assigned user
- `S360_AssignedToLogic` - Assignment logic
- `ActionOwnerAlias` - Action owner alias
- `ActionOwnerName` - Action owner display name
- `IsActionOwnerActiveEmployee` - Boolean

**Dates:**
- `dueDate` - Due date (lowercase)
- `DueDate` - Due date (PascalCase)
- `EtaDate` - ETA date
- `EtaStatus` - ETA status
- `S360_TwoWayEta` - Two-way ETA flag
- `OriginalPublishTime` - When item was published

**Status:**
- `SlaType` - SLA status (InSla, OutOfSla, ApproachingSla)
- `classificationType` - Classification (Critical, etc.)
- `ActionItemType` - Item type
- `myExceptionStatus` - Exception status

**Service/Program:**
- `serviceTreeId` - Service tree ID
- `S360_ServiceId` - S360 service ID
- `myExceptionServiceTreeId` - Exception service ID
- `S360_ProgramIds` - List of program IDs
- `S360_WavesMetadata` - Waves metadata

**Other:**
- `EventId` - Event ID
- `IsServiceInAGC` - AGC flag
- `S360_IsShadow` - Shadow item flag
- `XDivSecurityTeamId` - Security team ID
- `TotalRowCount` - Row count

## Design Decisions
- Show all non-empty fields to avoid missing relevant data
- Group fields logically for readability
- Use scrollable text widget for potentially long content

## Next Steps
Proceed to Program Manager for design doc.
