# SFI-014 Builder Notes

## Work Item
- **ID**: SFI-014
- **Title**: Fix Unknown Owner Item and Drill-Down "No Items Found" Bugs
- **Date**: 2024

## Git Operations

### Branch Creation
```bash
git checkout -b SFI-014
# Switched to a new branch 'SFI-014'
```

### Build Verification
```bash
python -m py_compile GUI/src/sfi_reporter/tk_app.py
# Build status: True (success)
```

### Test Verification
```bash
python -m pytest GUI/tests/ -v
# 88 passed in 1.07s
```

### Commit
```bash
git add .
git commit -m "SFI-014: Fix Unknown Owner and Drill-Down Bugs in Manager View"
# [SFI-014 8de6ff9] SFI-014: Fix Unknown Owner and Drill-Down Bugs in Manager View
# 10 files changed, 388 insertions(+), 9 deletions(-)
```

## Files Changed

- `GUI/src/sfi_reporter/tk_app.py` - Bug fixes
- `WorkItems/SFI-014/SFI-014-User-Story.md` - Updated status
- `WorkItems/SFI-014/Design/SFI-014-design-doc.md` - Created
- `WorkItems/SFI-014/Design/SFI-014-Review-Comments.md` - Created
- `WorkItems/SFI-014/RoleDecisionNotes/*` - All role notes created

## DoD Status

All items complete:
- [x] branchCreated
- [x] testsWrittenFirst
- [x] testsPass
- [x] buildPasses
- [x] docsUpdated
- [x] refactorComplete
- [x] committed
