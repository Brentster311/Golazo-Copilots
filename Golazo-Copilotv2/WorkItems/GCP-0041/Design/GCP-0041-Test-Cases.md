# Test Cases — GCP-0041

## TC1: Spine contains gcp_capabilities mention
- **Action**: Read `bootstrap-instructions.md` source
- **Assert**: Contains `gcp_capabilities`

## TC2: Mention uses conditional phrasing
- **Action**: Read `bootstrap-instructions.md` source
- **Assert**: Contains "capabilities.yaml" with conditional framing

## TC3: Section is brief
- **Action**: Extract the "Capability Registry" section from source
- **Assert**: Section is <= 10 lines
