# GCP-0033 Design Document: Guard Against Incomplete Work Items

## Summary

Add a "Role Progress" section to `gcp_status` output showing which roles have been completed, which is in-progress, and which are pending. Include a completion summary line.

## Problem Statement

Work items can be abandoned mid-workflow with no indication of what was completed. Users have no visibility into overall progress without inspecting state.json directly.

## Business Case

### Why Now
- GCP-0027 retrospective AI-3 identified this gap
- Multiple work items (GCP-0026, GCP-0028) were discovered incomplete in prior sessions

### Impact
- Clear visibility into role progress for any work item
- Easy detection of abandoned work items

## Functional Requirements

### FR1: Compute role progress from role_history
- Build role progress from `state.role_history` entries
- Roles with `exited_at` set = completed
- Current role (matching `state.current_role` with no `exited_at`) = in-progress
- Roles not in history = pending

### FR2: Add role_progress to gcp_status return dict
- New field: `role_progress` — list of `{"role": str, "status": "completed"|"in-progress"|"pending"}`
- New field: `roles_completed` — count of completed roles
- New field: `roles_total` — total workflow roles (9 for complete profile)

### FR3: Render role progress in server.py
- Show after version/work-item header, before required outputs
- Format: `- Role Progress: 6/9 complete`
- Compact single-line summary (avoid clutter)

## Proposed Approach

### Step 1: Add `_compute_role_progress()` helper in `gcp_status.py`
- Takes state and ALL_ROLES list
- Returns progress list and counts

### Step 2: Add to gcp_status return dict

### Step 3: Render in server.py

### Step 4: Tests

## Test Strategy

| Test | Coverage |
|------|----------|
| Fresh work item (0/9) | Only PO is in-progress, rest pending |
| After transitions (3/9) | Completed roles correct |
| Completion (9/9) | All roles completed |
