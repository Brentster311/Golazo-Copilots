# SFI-016 — Program Manager Notes

## Design Decisions
1. **Singleton over connection pool**: Desktop app with one user — singleton is the simplest correct solution.
2. **Tuple return over exception raising**: Partial success is the common case (some KPIs work, some don't). Exceptions would abort the entire result set. A tuple lets callers handle both outcomes.
3. **User-initiated retry over auto-retry**: Gives users agency. They can inspect failures before retrying, or proceed with partial data.
4. **Merge-into-cache over full refresh**: Retry should be fast — only fetches the missing KPIs and splices results into the existing dataset.

## Sequencing
All four components ship together — they are interdependent. The singleton is a prerequisite for reducing noise during retry. The tuple return is required for the UI to know what failed.

## Open Questions
- None. Scope is tight and implementation is already done.
