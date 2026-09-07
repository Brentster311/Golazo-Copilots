# GCP-0075 Capability Impact

## Directly Affected

- `bootstrap-skill-installation`: bootstrap role-copy output changes because corrected packaged Documenter and Builder instructions are copied during full bootstrap.

## Transitively Affected

None identified.

## Contract Implications

- Documenter reviews non-release implementation documentation without requiring future Builder artifacts.
- Builder owns release classification, canonical version update, PEP 440 monotonicity validation, changelog maintenance, build, commit, and push across Complete and Express.
- Bootstrap API and overwrite behavior are unchanged; forced bootstrap produces corrected role text while non-force preserves existing custom copies.
- No runtime MCP tool or state contract changes.

## Compatibility

The change is instruction-only. Existing workflows, profile sequences, and state files need no migration. Customized role installations opt into replacement through existing force behavior.
