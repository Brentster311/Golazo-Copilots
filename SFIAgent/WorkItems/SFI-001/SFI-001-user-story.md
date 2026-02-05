# SFI-001: S360 API Direct Access Library

**Status**: IN PROGRESS

---

## User Story

- **Title**: S360 API Direct Access Library for Python
- **As a**: Developer working with Microsoft S360 service management platform
- **I want**: A Python library that authenticates with Azure and directly calls S360 APIs
- **So that**: I can programmatically interact with S360 to manage action items, ETAs, and discover available API endpoints without manual browser access

---

## Out of Scope

- Web UI or dashboard
- Real-time notifications or webhooks
- Integration with other non-S360 services (except Azure Identity for auth)
- Automated scheduling or background jobs
- Multi-user session management

---

## Assumptions

- **Assumption (explicit)**: User has Azure CLI installed and authenticated (`az login` completed)
- **Assumption (explicit)**: User has appropriate permissions to access S360 APIs with their Microsoft corporate account
- **Assumption (explicit)**: S360 API base URL remains `https://api.vnext.s360.msftcloudes.com/v1`
- **Assumption (explicit)**: The S360 scope `https://microsoft.onmicrosoft.com/Service360/.default` is valid for API access

---

## Acceptance Criteria

- [ ] **AC1**: Library authenticates using `AzureCliCredential` and successfully retrieves a bearer token for S360 scope
- [ ] **AC2**: Library can call existing known S360 endpoints (GetEtaHistoryById, SaveETAsByIds) and return parsed responses
- [ ] **AC3**: Library includes an API discovery mechanism that can probe/document available S360 endpoints
- [ ] **AC4**: All API responses are cached locally with configurable expiry
- [ ] **AC5**: Library provides clear error handling with meaningful error messages for auth failures, API errors, and network issues
- [ ] **AC6**: Project includes comprehensive unit tests with mocked API responses
- [ ] **AC7**: README documents installation, configuration, and usage examples

---

## Non-Functional Requirements

- Response time: API calls should timeout after 30 seconds (configurable)
- Local cache storage using JSON files in user's app data directory
- Support Python 3.10+
- Type hints throughout codebase
- Logging using Python's standard logging module

---

## Telemetry / Metrics Expected

- None for initial release (local tool)
- Future: Optional telemetry for API call success/failure rates

---

## Rollout / Rollback Notes

- Standalone library, no deployment pipeline required
- Install via `pip install -e .` for local development
- No rollback concerns for v1.0

---

## Technical Context (from Reference Project)

### Known S360 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ActionItems/GetEtaHistoryById` | Get ETA history for action item |
| POST | `/ActionItems/SaveETAsByIds` | Save ETA updates |

### Authentication
- Uses `azure-identity` package with `AzureCliCredential`
- S360 Scope: `https://microsoft.onmicrosoft.com/Service360/.default`
- Graph Scope: `https://graph.microsoft.com/.default` (for user info)

### Configuration
- S360 Base URL: `https://api.vnext.s360.msftcloudes.com/v1`
- Dashboard URL: `https://vnext.s360.msftcloudes.com`

---

## Decomposition Rationale

This story covers the foundational library. Future stories may include:
- CLI wrapper for command-line usage
- Extended API coverage as endpoints are discovered
- Integration with Kusto for data retrieval
