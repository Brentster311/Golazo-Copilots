# Architect Decision Notes: RETIRE-001

## Work Item
RETIRE-001 - MVP Retirement Planner

## Decisions Made

### 1. Data Contracts Defined
**Decision**: Explicitly define `UserProfile` and `ProjectionResult` dataclass structures.

**Rationale**: 
- Clear contracts enable parallel development
- Type hints improve code quality
- Dataclasses are built-in (Python 3.7+), no dependencies

### 2. Repository Interface Contract
**Decision**: Define `IDataRepository` abstract base class with `save()` and `load()` methods.

**Rationale**:
- User explicitly requested abstraction for future flexibility
- Interface enables mocking for unit tests
- Clear contract: load returns `None` if no data, raises on corruption

### 3. Error Handling Pattern
**Decision**: Repository raises `RepositoryError`, Service catches or re-raises, UI displays friendly message.

**Rationale**:
- Consistent error handling across layers
- Failures don't crash the application
- User sees helpful messages, not stack traces

### 4. Explicit UTF-8 Encoding
**Decision**: Always use `encoding='utf-8'` when reading/writing JSON files.

**Rationale**:
- Python default encoding varies by platform
- UTF-8 is safe cross-platform
- Explicit is better than implicit

### 5. File Location
**Decision**: Store user data in `data/` subfolder relative to application.

**Rationale**:
- Keeps data organized
- Easy to find for backup/debugging
- Doesn't clutter application root

### 6. Security Posture
**Decision**: Plaintext JSON is acceptable for MVP.

**Rationale**:
- Local file on user's own machine
- No network transmission
- User can inspect/edit if desired
- Encryption can be future enhancement

## Alternatives Considered

### Alternative: Use TypedDict instead of dataclass
**Rejected**: Dataclasses provide better ergonomics, validation hooks, and are equally built-in.

### Alternative: Add encryption now
**Rejected**: Adds complexity, dependencies, and key management. Overkill for local MVP.

### Alternative: Use SQLite for type safety
**Rejected**: Single record doesn't warrant database. JSON is simpler.

## Tradeoffs Accepted
1. **Plaintext over encryption**: Simplicity wins for MVP
2. **Dataclass over Pydantic**: No external dependency, less validation magic
3. **Custom error class over generic Exception**: Clearer error handling

## Known Limitations
1. No data migration strategy if model changes (MVP assumption: schema won't change)
2. No concurrent access handling (single user assumption)
3. No backup/versioning of data file

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Model changes break existing data | Low (MVP) | Document schema, can add migration in future story |
| File permission errors | Low | Catch and display friendly error |

## Contracts Defined

### UserProfile
```python
@dataclass
class UserProfile:
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    desired_monthly_income: float
```

### ProjectionResult
```python
@dataclass
class ProjectionResult:
    years_to_retirement: int
    projected_savings: float
    required_nest_egg: float
    monthly_income_possible: float
    is_on_track: bool
    surplus_or_gap: float
```

### IDataRepository
```python
class IDataRepository(ABC):
    @abstractmethod
    def save(self, profile: UserProfile) -> None: ...
    
    @abstractmethod
    def load(self) -> UserProfile | None: ...
```

## Open Items for Tester
- Test cases should cover all edge cases identified by Reviewer
- Repository tests should verify error handling
- Calculator tests should verify formula correctness
