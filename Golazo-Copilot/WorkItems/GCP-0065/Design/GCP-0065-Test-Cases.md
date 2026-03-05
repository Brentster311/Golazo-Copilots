# GCP-0065 Test Cases

## Acceptance Criteria Mapping
- AC1: `list` resolves canonical path.
- AC2: `impact` resolves canonical path.
- AC3: Legacy location auto-migrates to canonical when canonical missing.
- AC4: Missing-file errors include canonical expected location.

## Test Matrix

### TC1 Canonical Path Used by List
- Type: Integration
- Setup: Create `WorkItems/capabilities.yaml` with valid content.
- Steps: Run `golazo_capabilities(action="list")`.
- Expected: Command succeeds and returns parsed capabilities.
- Failure message: "Expected list to resolve WorkItems/capabilities.yaml."

### TC2 Canonical Path Used by Impact
- Type: Integration
- Setup: Create `WorkItems/capabilities.yaml` and sample impacted files.
- Steps: Run `golazo_capabilities(action="impact", files=[...])`.
- Expected: Impact output references capabilities defined in canonical file.
- Failure message: "Expected impact to use canonical capability registry."

### TC3 Legacy File Is Moved When Canonical Missing
- Type: Integration
- Setup: Create legacy `capabilities.yaml` at repo root; ensure `WorkItems/capabilities.yaml` absent.
- Steps: Run `golazo_capabilities(action="list")`.
- Expected: `WorkItems/capabilities.yaml` exists after command and legacy file no longer at old location.
- Failure message: "Expected legacy capabilities.yaml to be migrated to WorkItems/capabilities.yaml."

### TC4 Dual-File Conflict Canonical Wins
- Type: Integration
- Setup: Create both canonical and legacy files with different markers.
- Steps: Run `golazo_capabilities(action="list")`.
- Expected: Canonical content is used; legacy file remains untouched; warning emitted if supported.
- Failure message: "Expected canonical capabilities file to take precedence in dual-file scenario."

### TC5 Missing File Error Is Actionable
- Type: Integration
- Setup: Ensure no capability file exists in canonical or legacy paths.
- Steps: Run `golazo_capabilities(action="list")`.
- Expected: Error includes `WorkItems/capabilities.yaml` as expected location.
- Failure message: "Expected missing-file error to mention canonical path."

### TC6 Move Failure Surfaces Actionable Error
- Type: Unit/Integration (mock or controlled FS permission failure)
- Setup: Legacy file exists; canonical missing; force move operation to fail.
- Steps: Invoke resolver command path.
- Expected: Error message includes source and target paths with move failure reason.
- Failure message: "Expected actionable migration failure details with source and target paths."

## Non-Functional Checks
- Run tests on Windows path semantics at minimum.
- Verify no additional file scans beyond expected resolver paths.
