<!-- Last Updated in Golazo Copilot Version: 2.105.3 -->
# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## REQUIRED: Before EVERY Response
1. Call `golazo_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the role instructions returned

## Starting a New Work Item
```
golazo_create_workitem(work_item_id="<id>", profile="complete")
```

## Role Transitions
```
golazo_transition(work_item_id="<id>", role="program-manager")
```

For full documentation, see the Golazo Copilot README.
