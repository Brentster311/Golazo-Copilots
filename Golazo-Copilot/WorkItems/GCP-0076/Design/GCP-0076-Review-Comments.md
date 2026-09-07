# GCP-0076 Review Comments

## Quality Assurance Review

Approved for architecture review with these invariants:

- `WorkItems/capabilities.yaml` is the only active registry under a supplied workspace root.
- Canonical data wins whenever both canonical and root legacy files exist.
- Mutating setup operations migrate a legacy-only file rather than replacing its data.
- Status may inspect a legacy-only file for compatibility but must not move it.
- Cleanup is repository-specific: preserve AgentLoop's independent registry and the test-workspace fixture.
- A zero-impact result must not be interpreted as proof that no new capability card is needed.

## Risks

- Importing private path helpers across tools would create coupling; expose small shared helpers with explicit mutating/read-only semantics.
- Repository-layout assertions can be brittle if they ban all nested registries; scope them to known obsolete top-level/package files.
- Capability cards must use repository-root-relative key files because validation joins paths to the supplied workspace root.

## Architect Notes

Approved. Implement two explicit shared operations in the capability module:

- A read-only lookup that returns canonical when present, otherwise legacy, and never mutates the workspace.
- An ensure/migration operation that returns canonical, moving legacy data only when canonical is absent and creating the packaged template only when neither exists.

Bootstrap and work-item creation use ensure/migration; status uses read-only lookup; capability actions retain ensure/migration for backward compatibility. Canonical always wins when both files exist. No new dependency or security boundary is introduced.
