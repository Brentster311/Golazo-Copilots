# GCP-0056 Developer Decision Notes

## Implementation Summary

Implemented the `golazo_update` MCP tool that checks Azure Artifacts for newer versions of `golazo-copilot` and guides users through installation and bootstrap.

## Files Created / Modified

### New Files
- **`src/golazo_copilot/tools/golazo_update.py`** — Core tool module (~250 lines)
- **`tests/test_golazo_update.py`** — 30 test cases covering check, install, preflight, edge cases, security, and formatter

### Modified Files
- **`src/golazo_copilot/server.py`** — Added import, tool registration (list_tools), dispatch block (call_tool), and `format_update_result()` formatter
- **`src/golazo_copilot/tools/__init__.py`** — Added golazo_update import and __all__ entry

## Key Design Decisions

### 1. PEP 503 HTML Parsing
Used `html.parser.HTMLParser` (stdlib) to parse the Azure Artifacts Simple API response. No external HTML parsing dependency needed. The `_AnchorParser` class extracts `href` attributes from `<a>` tags.

### 2. Version Extraction Regex
`VERSION_RE = re.compile(r"golazo[_-]copilot-(\d+\.\d+\.\d+(?:[a-zA-Z0-9.]*[a-zA-Z0-9])?)(?:\.tar|\.whl|\.zip|-py)")`

Key design choice: The regex uses a lookahead for file extensions (`.tar`, `.whl`, `.zip`, `-py`) to prevent capturing file extensions as part of the version string. Initial version was too greedy and captured `.tar.gz` as part of the version, causing `InvalidVersion` exceptions.

### 3. Version Classification
Used `packaging.version.Version.is_prerelease` to classify versions as stable vs pre-release. Invalid version strings are silently skipped (logged but not propagated as errors).

### 4. Input Validation
`_SAFE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+([a-zA-Z0-9.]*)?$")` validates user-supplied version strings before passing to pip. Prevents shell injection via version parameter.

### 5. Test Module Loading Workaround
The normal import chain (`golazo_copilot.tools.golazo_update`) is broken because `golazo_transition.py` imports `get_role_order_for_profile` which doesn't exist in `core/transitions.py`. Tests use `importlib.util.spec_from_file_location` to load the module directly as `golazo_update_mod`, bypassing the broken import chain. All patches use `golazo_update_mod.` prefix.

### 6. Structured Return Values
Both `_action_check` and `_action_install` return structured dicts rather than formatted strings. The formatter (`format_update_result` in server.py) handles presentation. This keeps the tool testable and separates concerns.

### 7. Post-Install Flow
After successful install, the tool returns:
- `restart_required: true` with a message that the MCP server must be refreshed
- `bootstrap_options`: list of 3 options (no bootstrap, standard bootstrap, full clean bootstrap)
- The tool does NOT auto-bootstrap; it presents options for the user/copilot to act on

### 8. Authentication
The tool checks for `keyring` and `artifacts-keyring` packages, and verifies `az login` status. These are preflight checks only — actual auth is handled by pip + keyring during install.

## Test Results
- **30/30 tests pass** for `test_golazo_update.py`
- **178/178 non-broken tests pass** across the full test suite (15 pre-existing collection errors due to `get_role_order_for_profile` import issue are unrelated)
- No regressions introduced

## Assumptions
- Azure Artifacts feed URL is stable: `https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/golazo-copilot/`
- `keyring` and `artifacts-keyring` are the required auth packages
- pip subprocess is acceptable for installation (no programmatic pip API usage)
- Current version is read from `golazo_copilot.__version__`
