# Program Manager Decision Notes: RETIRE-001

## Work Item
RETIRE-001 - MVP Retirement Planner

## Decisions Made

### 1. GUI Framework Selection: Tkinter
**Decision**: Use Tkinter for the GUI layer.

**Rationale**:
- Built into Python standard library (no dependencies)
- Sufficient for MVP form-based input
- Windows-native appearance
- Fast development cycle
- Can be replaced in future story if richer UI needed

**Alternatives Rejected**:
- PyQt/PySide: Too heavy for MVP, licensing considerations
- Dear PyGui: Extra dependency, learning curve

### 2. Calculation Assumptions
**Decision**: Hard-code financial assumptions for MVP.

| Assumption | Value | Rationale |
|------------|-------|-----------|
| Annual Return Rate | 7% | Historical stock market average (inflation-adjusted) |
| Safe Withdrawal Rate | 4% | Standard retirement planning rule of thumb |

**Future Enhancement**: Make these configurable (separate user story).

### 3. Data Format: JSON
**Decision**: Use JSON for local file storage.

**Rationale**:
- Human-readable (user can inspect/edit if needed)
- No dependencies (json module is built-in)
- Easy to debug during development
- Simple to migrate to other formats later via repository abstraction

### 4. Architecture: Three-Layer with Repository Pattern
**Decision**: Implement clean separation of concerns.

```
UI ? Service ? Repository
```

**Rationale**:
- User explicitly requested abstraction for data persistence
- Makes unit testing straightforward (mock repository)
- Follows SOLID principles
- Enables future storage backends without touching business logic

### 5. Input Validation Strategy
**Decision**: Validate at UI layer with clear error messages.

**Bounds**:
- Age: 18-100 (integer)
- Retirement age: > current age, ? 100
- Money values: ? 0 (decimal)
- Desired income: > 0 (must have a goal)

### 6. No External Dependencies for Core
**Decision**: MVP uses only Python standard library.

**Rationale**:
- Simplifies installation
- No version conflicts
- pytest only as dev dependency for testing

## Alternatives Considered

### Electron/Web-based GUI
**Rejected**: Overkill for single-user local app. Would require Node.js, more complexity.

### Database Storage (SQLite)
**Deferred**: Single user with one profile doesn't need a database. Repository abstraction allows adding this later.

### Configuration File for Assumptions
**Deferred**: Hard-coded values for MVP reduce complexity. Can be a separate user story.

## Tradeoffs Accepted

1. **Tkinter appearance vs. modern UI**: Accepted dated look for zero dependencies
2. **Hard-coded rates vs. flexibility**: Accepted less flexibility for simpler MVP
3. **No encryption vs. security**: Accepted plaintext JSON (local file, single user, no sensitive auth data)

## Known Limitations

1. Projection accuracy limited by simplified formula (no inflation, taxes, varying returns)
2. Single user profile only
3. No data export/backup feature
4. Windows-only (Tkinter works cross-platform but not tested)

## Risks

| Risk | Mitigation |
|------|------------|
| User trusts projection too literally | Add disclaimer in UI |
| Future framework change expensive | Repository pattern isolates data layer; UI is separate module |

## Open Items for Architect
1. Confirm repository interface design
2. Validate calculation formula
3. Review proposed file structure
