# GCP-0056 Domain Expert Role Notes

## Domain Expertise Assessment

### Work Item Analysis

GCP-0056 introduces `golazo_update`, an MCP tool that checks Azure Artifacts for newer versions of `golazo-copilot`, guides users through installation, and optionally re-bootstraps. The technical surface areas are:

| Domain Area | Complexity | Standard/Custom |
|-------------|-----------|-----------------|
| Azure Artifacts (PEP 503 Simple API) | Low | Standard — well-documented, stable spec |
| Python packaging / version parsing | Low | Standard — `packaging.version`, PEP 440 |
| Azure auth (`az login`, keyring) | Low | Standard — documented Azure SDK pattern |
| MCP server lifecycle (restart after update) | Low | Internal convention, already established |
| Subprocess management (pip install) | Low | Standard — officially recommended approach |

### Conclusion: No Domain Expertise Required

All technologies involved are well-documented, standard Python packaging and Azure DevOps patterns. No specialized domain expert consultation is needed for this work item.

**Justification:**

1. **Azure Artifacts / PEP 503 Simple API** — The Simple Repository API is a Python packaging standard (PEP 503). Azure Artifacts implements it faithfully. The design doc correctly identifies the HTML parsing approach using stdlib `html.parser`. No edge cases or Azure-specific deviations require expert input.

2. **Python version parsing** — The design correctly uses `packaging.version.Version` and its `is_prerelease` property for PEP 440 classification. This is the canonical approach and requires no domain expertise beyond what is already documented.

3. **Azure authentication** — The auth pattern (`az login` → `keyring` → `artifacts-keyring`) is the standard Azure Artifacts authentication flow for pip. The pre-flight checks (`importlib.util.find_spec` for keyring packages, `az account show` for login status) are straightforward. No custom auth flows, token management, or credential storage are involved.

4. **MCP server lifecycle** — The decision to NOT auto-restart the server and instead inform the user is consistent with existing Golazo patterns. The post-install bootstrap delegation to `golazo_bootstrap` reuses an existing, tested tool. No new lifecycle patterns are introduced.

5. **Subprocess pip invocation** — Running pip via `subprocess.run([sys.executable, "-m", "pip", ...])` is the officially recommended approach per pip documentation. Timeout handling and error capture are standard subprocess patterns.

## Domain-Specific Guidance (Precautionary Notes)

While no formal domain expert consultation is needed, the following technical notes are worth documenting for downstream roles:

### PEP 503 Parsing
- Azure Artifacts normalizes package names (e.g., `golazo-copilot` → `golazo-copilot`). The parser should normalize names per PEP 503 (lowercase, hyphens).
- Version strings are embedded in filenames (e.g., `golazo_copilot-2.109.0.tar.gz`). The regex extraction should handle both `.tar.gz` and `.whl` suffixes.
- The feed may include multiple distribution formats per version. Deduplicate by version before classification.

### `packaging.version` Behavior
- `packaging.version.Version` raises `InvalidVersion` for non-PEP-440 strings. The implementation should catch this and skip malformed entries rather than crashing.
- Pre-release ordering: `2.110.0a1 < 2.110.0b1 < 2.110.0rc1 < 2.110.0`. The `packaging` library handles this correctly.

### Azure Auth Edge Cases
- `az account show` can succeed but the token may be expired for the specific feed. The tool should surface pip's error output clearly if install fails despite passing the pre-flight check.
- On some corporate machines, `artifacts-keyring` may be blocked by group policy. The error message should be actionable (suggest contacting IT or using a PAT).

### pip Subprocess
- Use `sys.executable` (not just `pip`) to ensure the correct Python environment is targeted.
- The `--index-url` flag replaces the default PyPI index. If the user also needs PyPI packages, `--extra-index-url` would be needed — but for this tool, `--index-url` is correct since we're installing a specific package from a known feed.

## Recommendations for Downstream Roles

- **Quality Assurance**: Focus test cases on error paths — feed unreachable, auth expired, malformed version strings, pip install failure. The happy path is straightforward.
- **Architect**: No structural concerns — single new module + server registration follows the established Golazo tool pattern.
- **Developer**: Consider adding a timeout to the `urllib.request` call (the design doc mentions < 10 seconds; enforce this in code). Handle `InvalidVersion` gracefully.

## Assumptions

- The Azure Artifacts feed implements PEP 503 faithfully (confirmed by existing team usage of `pip install` from this feed).
- `packaging` is available at runtime (transitive dependency of pip/setuptools, present in any standard Python environment).
- No proxy or network configuration beyond system defaults is needed (same assumption as existing Golazo tools).
