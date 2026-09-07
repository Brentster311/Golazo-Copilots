# GCP-0072 Test Cases

## Acceptance Criteria Traceability

| Acceptance criterion | Test cases |
|---|---|
| AC1: Display and confirm every packaged default | TC-01, TC-02, TC-03 |
| AC2: Install configured workspace skill | TC-04, TC-05, TC-06 |
| AC3: Install configured user skill cross-platform | TC-07, TC-08 |
| AC4: Report outcomes and avoid partial installs | TC-09 through TC-14 |

## Canonical Defaults

Tests must assert exact coverage for organization, project, team, board, work item type, area, iteration, assignee, planned swimlane field, board column field, and board done field as currently declared in the packaged `golazo-ado-sync/SKILL.md`.

## Test Cases

### TC-01: Tool contract exposes all defaults

- **Action:** Inspect the `golazo_bootstrap` tool definition and bootstrap guidance.
- **Expected:** Every canonical key and packaged value is available for user review before installation.
- **Failure message:** `Bootstrap confirmation contract does not match packaged golazo-ado-sync defaults.`

### TC-02: Explicit acceptance installs defaults

- **Action:** Invoke full bootstrap with skill installation enabled and explicit confirmation of unchanged defaults.
- **Expected:** The installed configuration exactly matches all canonical defaults and the result marks the source as `defaults`.
- **Failure message:** `Confirmed defaults were not persisted exactly.`

### TC-03: Missing confirmation fails closed

- **Action:** Enable skill installation without explicit confirmation/configuration.
- **Expected:** Bootstrap fails with an actionable confirmation error and creates no skill destination.
- **Failure message:** `Skill installation proceeded without explicit configuration confirmation.`

### TC-04: Workspace installation uses supported path

- **Action:** Bootstrap a temporary workspace with Workspace scope.
- **Expected:** The complete resource tree exists at `.github/skills/golazo-ado-sync/`, including valid `SKILL.md`; no user-scope skill is created.
- **Failure message:** `Workspace skill was not installed exclusively at the supported path.`

### TC-05: Customized workspace configuration persists

- **Action:** Confirm a configuration with representative replacements, including an area containing backslashes.
- **Expected:** Installed values match replacements exactly; package-source `SKILL.md` remains unchanged; result marks the source as `customized`.
- **Failure message:** `Customized configuration was altered or mutated packaged defaults.`

### TC-06: Generated skill remains discoverable

- **Action:** Parse generated YAML frontmatter and inspect the folder name.
- **Expected:** Frontmatter is valid; `name` equals `golazo-ado-sync`; description and invocation flags are preserved.
- **Failure message:** `Installed skill violates Copilot discovery metadata requirements.`

### TC-07: User installation resolves mocked home

- **Action:** Monkeypatch the active home to a temporary path and bootstrap with User scope.
- **Expected:** Installation occurs only at `<home>/.copilot/skills/golazo-ado-sync/`.
- **Failure message:** `User skill destination was not resolved from the active home directory.`

### TC-08: Path construction is platform independent

- **Action:** Exercise path resolvers with Windows-style and POSIX-style workspace/home fixtures without string concatenation assumptions.
- **Expected:** Each produces the standard path components for its platform representation.
- **Failure message:** `Skill destination contains platform-specific path construction errors.`

### TC-09: Existing destination skips without force

- **Action:** Seed an installed skill with sentinel content and invoke bootstrap with `force=False`.
- **Expected:** Sentinel content remains unchanged and the skill destination appears in structured skipped results.
- **Failure message:** `Existing skill was overwritten without force permission.`

### TC-10: Existing destination is replaced with force

- **Action:** Seed an installed skill and invoke bootstrap with `force=True` and confirmed configuration.
- **Expected:** The complete destination is replaced and structured results report creation/replacement.
- **Failure message:** `Force installation did not replace the existing skill consistently.`

### TC-11: Invalid configuration creates no destination

- **Action:** Omit each required value in parameterized cases and include malformed value types.
- **Expected:** Bootstrap returns a field-specific error and no destination exists.
- **Failure message:** `Invalid configuration produced a partial skill installation.`

### TC-12: Write failure preserves previous installation

- **Action:** Simulate a staged write/copy failure during forced replacement.
- **Expected:** Bootstrap fails, the previous destination remains intact, and temporary artifacts are cleaned up.
- **Failure message:** `Failed replacement damaged the existing installed skill.`

### TC-13: Result reports structured installation details

- **Action:** Exercise default install, customized install, and skip paths.
- **Expected:** Results expose scope, resolved skill destination, created/skipped outcomes, and configuration source without credentials or tokens.
- **Failure message:** `Bootstrap result lacks deterministic skill installation details or exposes sensitive data.`

### TC-14: Orchestrator-only rejects skill installation

- **Action:** Request `mode="orchestrator-only"` with skill installation enabled.
- **Expected:** Bootstrap returns an actionable incompatibility error before writing either artifact.
- **Failure message:** `Orchestrator-only mode accepted contradictory skill installation input.`

## Regression And Coverage

- Existing bootstrap tests must remain green, including omitted/empty scope defaults, role copying, capabilities behavior, force semantics, and orchestrator-only behavior.
- Server registry/schema and dispatch tests must cover new optional inputs and result formatting.
- Run focused pytest with coverage for every changed Python module and require more than 70% module coverage.
- No live home directory, package installation, Azure authentication, or Azure DevOps network call is permitted in automated tests.