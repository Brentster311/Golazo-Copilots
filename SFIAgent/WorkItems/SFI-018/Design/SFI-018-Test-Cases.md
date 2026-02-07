# SFI-018 — Test Cases

## Mapping to Acceptance Criteria

| AC# | Acceptance Criterion | Test Cases |
|-----|---------------------|------------|
| 1 | Valid `az login` → no browser popup | TC-01 |
| 2 | No `az login` → browser opens → app loads | TC-02 |
| 3 | Cancelled/failed login → clear error | TC-03, TC-04 |
| 4 | LAUNCHME.ps1 removed, BUILD_MANIFEST updated | TC-05 |
| 5 | Existing tests pass | TC-06 |
| 6 | Exe builds and runs | TC-07 |

---

## Unit Tests (automated)

### TC-01: CLI credential succeeds — no fallback

```
Given: AzureCliCredential.get_token() returns a valid token
When:  AuthManager acquires a token
Then:  InteractiveBrowserCredential.get_token() is never called
And:   Log contains "AzureCliCredential succeeded"
```

### TC-02: CLI fails — falls back to interactive browser

```
Given: AzureCliCredential.get_token() raises CredentialUnavailableError
And:   InteractiveBrowserCredential.get_token() returns a valid token
When:  AuthManager acquires a token  
Then:  A valid token is returned
And:   Log contains "falling back to InteractiveBrowserCredential"
```

### TC-03: Both credentials fail — error surfaces

```
Given: AzureCliCredential.get_token() raises CredentialUnavailableError
And:   InteractiveBrowserCredential.get_token() raises AuthenticationError
When:  AuthManager acquires a token
Then:  AuthenticationError is raised (not swallowed)
And:   Log contains "Auth failed"
```

### TC-04: Browser login cancelled/timed out

```
Given: AzureCliCredential.get_token() raises CredentialUnavailableError
And:   InteractiveBrowserCredential.get_token() raises ClientAuthenticationError("user cancelled")
When:  The app attempts to load data
Then:  Status bar shows "Authentication failed — please try again"
And:   Tables remain empty (not populated with zeros)
```

### TC-05: LAUNCHME.ps1 removed from repo

```
Given: The current branch
When:  Checking for LAUNCHME.ps1
Then:  File does not exist at SFIReporter/LAUNCHME.ps1
And:   BUILD_MANIFEST.md does not reference LAUNCHME.ps1
And:   Zip contents table lists only SFIReporter.exe + README.md
```

### TC-06: Existing tests pass

```
Given: All code changes applied
When:  Running pytest tests/ -v
Then:  All tests pass (0 failures)
```

### TC-07: Exe builds successfully (manual)

```
Given: PyInstaller build with hidden-imports
When:  Running the exe without az login
Then:  Browser opens for login
And:   After login, data loads normally
```

## Edge Cases

### TC-08: Token expired mid-session

```
Given: App loaded data successfully
And:   Token expires (>1 hour)
When:  User clicks Refresh Data
Then:  azure-identity silently re-authenticates (or prompts browser)
And:   Data loads without error
```

### TC-09: Credential chain used for both scopes

```
Given: ChainedTokenCredential is configured
When:  get_s360_token() and get_graph_token() are called
Then:  Both use the same credential chain
And:   Both return valid tokens
```
