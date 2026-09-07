---
name: golazo-ado-sync
description: 'Synchronize Golazo Copilot local work items with Azure DevOps. Use automatically when creating, starting, advancing, closing, approving, or checking a Golazo work item; creates or updates the matching ADO PBI, keeps it on the EngOps Supportability DS Planned swimlane, moves active work to In Progress, moves locally completed work to Ready to Review, and moves it to Done only after explicit user approval.'
user-invocable: true
disable-model-invocation: false
---

# Golazo Azure DevOps Sync

Keep each local Golazo work item synchronized with one Azure DevOps Product Backlog Item (PBI).

## Fixed Configuration

- Organization: `https://dev.azure.com/msazure`
- Project: `One`
- Team: `EngOps Supportability DS`
- Board: `Backlog items`
- Work item type: `Product Backlog Item`
- Area: `One\Azure CXP\Product and Platform\Data\Data Science\SupportabilityDS`
- Iteration: `One\FY27`
- Assignee: `brentj@microsoft.com`
- Planned swimlane field: `WEF_3685ECC254584507922BD78681CF0942_Kanban.Lane`
- Board column field: `WEF_3685ECC254584507922BD78681CF0942_Kanban.Column`
- Board done field: `WEF_3685ECC254584507922BD78681CF0942_Kanban.Column.Done`

Before any update, fetch the board configuration through the Azure DevOps Work Boards API and verify that these labels still exist: `Planned`, `Backlog`, `In Progress`, `Ready to Review`, and `Done`. Fail closed if the configuration changed.

## Authentication

Acquire an Azure DevOps bearer token without printing it:

```powershell
$token = az account get-access-token `
  --resource 499b84ac-1321-427f-aa17-267ca6975798 `
  --query accessToken -o tsv
$headers = @{ Authorization = "Bearer $token" }
```

Never store credentials in the repository, skill, work-item files, or output.

## Identity And Source

1. The local source is `WorkItems/<id>/<id>-User-Story.md` plus read-only `WorkItems/<id>/state.json` timestamps.
2. Never edit `state.json`; only Golazo MCP tools may mutate local workflow state.
3. Read `- Title:` from the user story and form the exact ADO title `[<id>] <Title>`.
4. Put the entire user-story Markdown, including Closure, in ADO Description as encoded `<pre>` content.
5. Do not store the ADO ID in `state.json`. Find the PBI by exact title when needed.

## Create Or Reconcile

Run immediately after `golazo_create_workitem` and user-story creation.

1. Query PBIs by exact title and project. Escape WIQL values correctly.
2. If more than one exact match exists, stop and report the duplicates.
3. If none exists, create one PBI.
4. If one exists, reconcile it instead of creating another.
5. Patch Description, Area, Iteration, Assigned To, board lane `Planned`, and initial board column `Backlog` in one JSON Patch request where practical.
6. Use a revision `test` operation for updates to existing items.
7. Fetch the PBI and verify exact title, decoded Description equality, Area, Iteration, assignee, lane, and column.

Do not use `az boards work-item create --description` for multiline Markdown. Use the Work Item REST API and JSON Patch because shell argument handling can truncate multiline content.

## Lifecycle Mapping

| Local lifecycle event | ADO board lane | ADO board column | ADO workflow state | Date behavior |
|---|---|---|---|---|
| Local work item and story created, work not started | `Planned` | `Backlog` | Board-mapped value | No dates required |
| First substantive role work begins | `Planned` | `In Progress` | Board-mapped value | Set Start Date from `state.json.created_at` |
| Roles transition while work remains active | `Planned` | `In Progress` | Board-mapped value | Preserve Start Date |
| Local workflow reaches closure and story is `IMPLEMENTED` | `Planned` | `Ready to Review` | Board-mapped value | Set Finish Date from final `state.json.updated_at` |
| User explicitly approves moving this item to Done | `Planned` | `Done` | `Done` | Preserve Start/Finish dates |

Use the board configuration's `stateMappings` for the selected column. Do not infer workflow state from the column name. Patch the board-specific column and lane fields, then verify `System.BoardColumn` and `System.BoardLane` resolve to the intended values.

## Approval Gate

- Never move a PBI to `Done` merely because local closure completed.
- Local completion always means `Ready to Review` until the user explicitly approves that specific item for Done.
- Requests such as “move it to Done,” “approve SIFT-nnn,” or an unambiguous equivalent count as approval.
- Approval is item-specific; do not apply it to other PBIs.
- If approval is ambiguous, ask before changing `Done` state.

## Date Rules

- Start Date: `Microsoft.VSTS.Scheduling.StartDate` from `state.json.created_at`.
- Finish Date: `Microsoft.VSTS.Scheduling.FinishDate` from the final closure `state.json.updated_at`.
- Preserve UTC. Azure DevOps may round microseconds to milliseconds.
- Do not overwrite an existing date unless correcting it from the same local source.

## Update Safety

1. Fetch the current PBI and revision immediately before patching.
2. Include `test /rev` in every update.
3. Apply all related field changes atomically when possible.
4. Fetch again after patching and verify every intended field.
5. Report the PBI ID, URL, revision, lane, column, state, Start Date, and Finish Date.
6. If authentication, board validation, exact-title lookup, patching, or verification fails, stop and report the blocker. Never claim synchronization succeeded without read-back verification.

## Role Integration

- After each successful `golazo_transition`, keep the card in `Planned / In Progress` unless the local workflow has reached closure.
- Upon local closure, synchronize the full final user-story document and move the card to `Planned / Ready to Review`.
- A Golazo status check should compare the local phase/status with the ADO card and repair drift when safe; never repair drift by bypassing the Done approval gate.
