# GCP-0072 Capability Impact

## Registry Result

`golazo_capabilities(action="impact")` was run against the proposed bootstrap tool, path resolver, MCP registry, dispatch, formatter, orchestrator guidance, and packaged skill files.

Result: **0 registered capabilities affected**.

## Registry Limitation

The capability registry contains only `example-capability`, whose key file is an unrelated placeholder. Therefore, the automated result does not mean the product has no affected behavior; it means bootstrap and packaged-skill behavior are not represented in the current registry.

## Directly Affected Product Behavior

- Bootstrap scaffolding and its MCP input/result contract.
- Workspace and user scope path resolution.
- Packaged resource installation.
- Bootstrap result formatting and orchestrator guidance.

## Transitively Affected Behavior

- Existing callers of `golazo_bootstrap` and tests of its schema and output.
- GitHub Copilot discovery of the installed `golazo-ado-sync` skill.
- Legacy server compatibility wrappers that duplicate modular registration and dispatch surfaces.

## Contract Implications

- New optional bootstrap inputs are additive and default to no skill installation.
- Existing inputs and result fields retain their meanings.
- A new additive `skills` result collection reports installation outcomes.
- No capability contract is removed or made mandatory for existing callers.

## Recommendation

Add a real bootstrap/skill-installation capability card to the registry in a separate maintenance work item. Replacing the project-wide placeholder is broader than this user story.