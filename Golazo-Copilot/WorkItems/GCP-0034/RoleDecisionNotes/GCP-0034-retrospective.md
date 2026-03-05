# GCP-0034: Retrospective

## What Went Well
- Fix was simple — single constant change plus test update
- Bootstrap now works correctly with the workspace's `WorkItems/` directory
- GCP-0030 cleanly superseded

## What Didn't Go Well
- `.github/` files kept getting deleted by `git add .` because the git root is one level up — had to restore them 3 times
- The `.github/` tracking issue is a monorepo layout pain point — `git add .` from a subfolder stages deletions of tracked files that no longer exist at that level

## Action Items
- Consider adding `.github/` to `.gitignore` at the subfolder level, or committing only from the repo root
- The repeated `.github/` deletion suggests a structural issue with git tracking
