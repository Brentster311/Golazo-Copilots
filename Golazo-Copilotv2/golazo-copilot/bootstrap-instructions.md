# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## REQUIRED: Before EVERY Response
1. Call `gcp_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the role instructions returned
4. If no active work item, ask user which to start

---

## Starting a New Work Item
```
gcp_init(work_item_id="<id>", profile="complete")
```
Then create User Story at `WorkItems/<id>/<id>-User-Story.md`

---

## Marking Progress (IMPORTANT: use `complete` not `value`)

After creating **User Story**:
```
gcp_mark_dor(work_item_id="<id>", item="userStory", complete=true)
```

After creating **Design Doc**:
```
gcp_mark_dor(work_item_id="<id>", item="designDoc", complete=true)
```

After creating **Review Comments**:
```
gcp_mark_dor(work_item_id="<id>", item="reviewComments", complete=true)
```

After creating **Test Cases**:
```
gcp_mark_dor(work_item_id="<id>", item="testCases", complete=true)
```

---

## Role Transitions

To move to next role:
```
gcp_transition(work_item_id="<id>", role="program-manager")
```

**Valid roles in order:**
1. project-owner
2. program-manager
3. quality-assurance
4. architect
5. developer (requires DoR complete!)
6. refactor-expert
7. documentor
8. builder
9. retrospective

---

## DoD Items (after development)

```
gcp_mark_dod(work_item_id="<id>", item="branchCreated", complete=true)
gcp_mark_dod(work_item_id="<id>", item="testsWrittenFirst", complete=true)
gcp_mark_dod(work_item_id="<id>", item="testsPass", complete=true)
gcp_mark_dod(work_item_id="<id>", item="refactorComplete", complete=true)
gcp_mark_dod(work_item_id="<id>", item="docsUpdated", complete=true)
gcp_mark_dod(work_item_id="<id>", item="buildPasses", complete=true)
gcp_mark_dod(work_item_id="<id>", item="committed", complete=true)
gcp_mark_dod(work_item_id="<id>", item="retroComplete", complete=true)
```

---

## File Naming Convention (ENFORCE)

| Artifact | Path |
|----------|------|
| User Story | `WorkItems/<id>/<id>-User-Story.md` |
| Design Doc | `WorkItems/<id>/Design/<id>-design-doc.md` |
| Review Comments | `WorkItems/<id>/Design/<id>-Review-Comments.md` |
| Test Cases | `WorkItems/<id>/Design/<id>-Test-Cases.md` |
| Refactoring Plan | `WorkItems/<id>/Design/<id>-Refactoring-Plan.md` |
| Retro Plan | `WorkItems/<id>/Design/<id>-Retro-Plan.md` |
| Role Notes | `WorkItems/<id>/RoleDecisionNotes/<id>-<role>.md` |

---

## Gate Enforcement
- **DoR Gate**: Cannot transition to `developer` until ALL DoR items are complete
- If `gcp_transition` fails, call `gcp_status` to see what's missing
