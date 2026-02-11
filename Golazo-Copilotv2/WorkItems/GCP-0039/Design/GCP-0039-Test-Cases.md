# Test Cases — GCP-0039

## TC1: QA role mentions capability registry
- Verify `quality-assurance.md` source contains "Capability Registry" section
- Verify conditional phrasing includes "capabilities.yaml"

## TC2: Architect role mentions capability registry
- Verify `architect.md` source contains "Capability Registry" section

## TC3: Developer role mentions capability registry
- Verify `developer.md` source contains "Capability Registry" section

## TC4: Refactor Expert role mentions capability registry
- Verify `refactor-expert.md` source contains "Capability Registry" section

## TC5: Retrospective role mentions capability registry
- Verify `retrospective.md` source contains "Capability Registry" section

## TC6: All 5 roles use conditional phrasing
- Each file contains "If a `capabilities.yaml` exists"

## TC7: Existing tests still pass
- All 160 existing tests remain green
