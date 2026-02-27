# SFI-032 Builder Notes

## Branch
- Created: `SFI-032` from `SFI-031`
- Commit: `9cce5cf` — "SFI-032: Move org-tree cache from services.py into GraphEndpoint._build_subtree"

## Build Verification
- accia-s360: 76 passed, 1 warning
- S360Reporter (core tests): 21 passed, 5 errors (pre-existing Azure CLI issues in test_data.py)

## Files Changed
- 21 files changed, 787 insertions, 361 deletions
