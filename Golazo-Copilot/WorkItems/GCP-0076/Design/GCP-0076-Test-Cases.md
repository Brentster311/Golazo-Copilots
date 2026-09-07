# GCP-0076 Test Cases

## AC1: Shared Canonical Path

1. Bootstrap on an empty workspace creates `WorkItems/capabilities.yaml` and no root registry.
2. Work-item creation on an empty workspace creates the canonical registry and no root registry.
3. Status counts capabilities from the canonical registry.
4. Capability list reads the same canonical data.

## AC2: Migration And Precedence

1. Mutating setup with only a legacy root registry moves its exact data to the canonical path.
2. When both files exist, capability list and status report canonical data.
3. Status on a legacy-only workspace reports its count without moving the file.
4. Malformed canonical YAML produces an explicit warning/error rather than silently falling back.

## AC3: Meaningful Registry

1. The top-level canonical registry contains cards for workflow orchestration, capability-registry management, bootstrap installation, project finalization, and release-policy guidance.
2. Every card has a description, at least one key file, at least one contract, and a dependency list.
3. Registry validation reports every card valid.
4. Impact analysis maps representative changed files to their cards.

## AC4: Repository Cleanup

1. Top-level `capabilities.yaml` is absent.
2. Obsolete `golazo-copilot/capabilities.yaml` is absent.
3. `WorkItems/capabilities.yaml`, `AgentLoop/WorkItems/capabilities.yaml`, and `golazo-copilot/tests/capabilities.yaml` remain.

## AC5: Regression Protection

1. Existing capability migration, dependency, malformed-data, and validation tests remain green.
2. Bootstrap, create-work-item, and status suites remain green.
3. Full tests and Ruff pass.

## Failure Signals

Any duplicate active top-level registry, divergent status/list count, lost legacy content, missing key file, or unrecognized representative impact path fails the focused policy suite.
