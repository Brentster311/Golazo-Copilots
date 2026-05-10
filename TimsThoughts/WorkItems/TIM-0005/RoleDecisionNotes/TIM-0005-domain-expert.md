# TIM-0005 — Domain Expert Decision Notes

## Assessment

**Domain expertise required: VS Code Agent Customization**

This work item creates `.agent.md` files — VS Code Custom Agent primitives. The relevant domain expertise is the VS Code agent customization format and YAML frontmatter rules. This expertise is already embedded in this session via the agent-customization SKILL.md, which was consulted during the POA decision to use `.agent.md` over `.prompt.md`.

### Key Guidance from Agent Customization Domain

1. **YAML frontmatter `description` must be quoted** if it contains colons — unescaped colons cause silent failures
2. **`name` field** is optional but strongly recommended for agent picker display (defaults to filename stem otherwise)
3. **`tools: [read, search]`** is the appropriate minimal set for read-only reviewer agents
4. **`user-invocable: true`** is the default — can be omitted, but should be explicit for clarity
5. **Description is the discovery surface**: the `description` field is how the agent decides whether this persona is relevant. Trigger phrases like "review from [Author]'s perspective" and "what would [Author] say" must appear in the description.
6. **Body length**: Keep agent bodies focused. Long bodies waste context on every invocation. 200–400 words per agent is appropriate.

## Conclusion

Proceed with the design as specified. No structural changes needed.
