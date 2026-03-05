# GCP-0065 Review Comments

## Overall Assessment
Design is feasible and scoped to a single behavior change with backward-compatible migration. It is implementation-ready with one clarification required for dual-file conflict handling.

## Strengths
- Canonical-path decision is explicit.
- Migration intent is clear and user-centric.
- Test strategy includes canonical, legacy-only, dual-file, and missing-file cases.

## Gaps / Clarifications Needed
- Conflict policy when both `WorkItems/capabilities.yaml` and legacy `capabilities.yaml` exist must be deterministic and test-asserted.
- Move failure behavior should specify error surface (exception type/message contract) to avoid brittle test expectations.

## Recommended Adjustments
- Set policy: canonical wins; legacy file remains untouched with warning.
- Include explicit message pattern for missing-file and move-failure paths with canonical target included.

## Risk Focus
- Cross-device moves may fail if rename semantics differ across platforms.
- Permission errors can regress command behavior if exceptions are not handled with actionable messages.

## Architect Notes
- Architectural alignment: change remains within capability registry tooling boundaries (`tool-capabilities`) and MCP dispatch surface (`mcp-server`) without introducing new public API shape.
- Contract stance: canonical file contract becomes `WorkItems/capabilities.yaml`; legacy path is migration input only.
- Security/privacy: no new network or auth surface introduced; ensure file operation errors do not expose sensitive filesystem details beyond required source/target diagnostics.
- Resilience: handle move failures deterministically and preserve readable fallback errors.
- Performance/cost: resolver should check canonical path first and avoid broad filesystem scans.
- Naming/structure: centralize path resolution and migration logic in one helper to reduce duplicated behavior across `list`, `show`, `impact`, and `validate`.
