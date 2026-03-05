"""GCP-0048: Test that role files are self-contained for subagent isolation.

Validates:
- AC1: YAML front-matter with inputs, outputs, tools
- AC2: No implicit cross-role references
- AC3: Explicit WorkItems/{id}/ artifact paths
- AC4: output_validator backward compatibility
- AC6: Front-matter outputs consistent with Required Outputs
"""

import re
from importlib import resources

import pytest
import yaml

from golazo_copilot.core.output_validator import parse_required_outputs

# All 10 role file names (excludes TechBestPractices.md)
ROLE_FILES = [
    "project-owner-assistant",
    "program-manager",
    "domain-expert",
    "quality-assurance",
    "architect",
    "developer",
    "refactor-expert",
    "documenter",
    "builder",
    "retrospective",
]

# Roles that reference TechBestPractices.md
TECH_BP_ROLES = [
    "project-owner-assistant",
    "architect",
    "developer",
    "refactor-expert",
]

# Implicit cross-role reference patterns (AC2)
IMPLICIT_PATTERNS = re.compile(
    r"previous role|from the last|earlier phase|already created"
    r"|(?<!Developer )role complete|implementation complete|DoR complete",
    re.IGNORECASE,
)


def _load_role_content(role: str) -> str:
    """Load role file content from package defaults."""
    files = resources.files("golazo_copilot.roles.defaults")
    role_file = files.joinpath(f"{role}.md")
    return role_file.read_text(encoding="utf-8")


def _extract_front_matter(content: str) -> tuple[dict | None, str]:
    """Extract YAML front-matter and remaining body from role file.

    Returns (parsed_yaml_dict_or_None, body_after_front_matter).
    """
    if not content.startswith("---"):
        return None, content
    # Find closing ---
    end = content.find("\n---", 3)
    if end == -1:
        return None, content
    yaml_text = content[3:end].strip()
    body = content[end + 4:]  # skip \n---
    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError:
        return None, content
    return parsed, body


# ---------------------------------------------------------------------------
# TC-1 & TC-6: Every role file has valid YAML front-matter (AC1)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role", ROLE_FILES)
def test_role_has_valid_yaml_front_matter(role: str):
    """TC-1/TC-6: Role file has YAML front-matter with inputs, outputs, tools."""
    content = _load_role_content(role)

    assert content.startswith("---"), (
        f"{role}.md does not start with YAML front-matter delimiter '---'"
    )

    fm, _ = _extract_front_matter(content)
    assert fm is not None, f"{role}.md has invalid YAML front-matter"
    assert isinstance(fm, dict), f"{role}.md front-matter is not a dict: {type(fm)}"

    assert "inputs" in fm, f"{role}.md front-matter missing 'inputs' key"
    assert "outputs" in fm, f"{role}.md front-matter missing 'outputs' key"
    assert "tools" in fm, f"{role}.md front-matter missing 'tools' key"

    # inputs may be empty list for first role (POA), but must be a list
    assert isinstance(fm["inputs"], list), (
        f"{role}.md front-matter 'inputs' is not a list"
    )
    # outputs must have at least 1 entry
    assert isinstance(fm["outputs"], list) and len(fm["outputs"]) >= 1, (
        f"{role}.md front-matter 'outputs' must be a non-empty list"
    )
    # tools must have at least 1 entry
    assert isinstance(fm["tools"], list) and len(fm["tools"]) >= 1, (
        f"{role}.md front-matter 'tools' must be a non-empty list"
    )


# ---------------------------------------------------------------------------
# TC-2: No implicit cross-role references (AC2)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role", ROLE_FILES)
def test_no_implicit_cross_role_references(role: str):
    """TC-2: No implicit cross-role references in role file body."""
    content = _load_role_content(role)
    _, body = _extract_front_matter(content)

    matches = []
    for i, line in enumerate(body.splitlines(), start=1):
        # Skip HTML comments
        if line.strip().startswith("<!--"):
            continue
        found = IMPLICIT_PATTERNS.search(line)
        if found:
            matches.append(f"  line {i}: '{found.group()}' in: {line.strip()}")

    assert not matches, (
        f"{role}.md contains implicit cross-role references:\n"
        + "\n".join(matches)
    )


# ---------------------------------------------------------------------------
# TC-3: All artifact references use explicit WorkItems paths (AC3)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role", ROLE_FILES)
def test_artifact_references_use_explicit_paths(role: str):
    """TC-3: Artifact references to work item files use WorkItems/{id}/ paths."""
    content = _load_role_content(role)
    _, body = _extract_front_matter(content)

    # Pattern: references like {id}-Something.md or <workitem-id>-Something.md
    # that should be prefixed with WorkItems/{id}/ or WorkItems/<workitem-id>/
    artifact_ref = re.compile(
        r'(?<!/)`?(?:\{id\}|<workitem-id>)-[A-Za-z][A-Za-z0-9-]*\.md`?'
    )
    path_prefix = re.compile(
        r'WorkItems/(?:\{id\}|<workitem-id>)/'
    )

    issues = []
    in_code_block = False
    for i, line in enumerate(body.splitlines(), start=1):
        # Skip fenced code blocks
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        # Skip HTML comments
        if line.strip().startswith("<!--"):
            continue

        for m in artifact_ref.finditer(line):
            # Check if there's a WorkItems/ prefix before this match
            start = max(0, m.start() - 60)
            context = line[start:m.end()]
            if not path_prefix.search(context):
                issues.append(f"  line {i}: bare artifact ref '{m.group()}' in: {line.strip()}")

    assert not issues, (
        f"{role}.md has artifact references without WorkItems/ path prefix:\n"
        + "\n".join(issues)
    )


# ---------------------------------------------------------------------------
# TC-4: output_validator backward compatibility (AC4)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role", ROLE_FILES)
def test_output_validator_backward_compatible(role: str):
    """TC-4: output_validator.parse_required_outputs works with front-matter."""
    content = _load_role_content(role)
    outputs = parse_required_outputs(content, "TEST-001")

    # Every role file has at least 1 required output (the decision notes)
    assert len(outputs) >= 1, (
        f"{role}.md: output_validator found {len(outputs)} outputs, expected >= 1"
    )

    # Check that decision notes output is present
    notes_found = any("RoleDecisionNotes" in o.path_or_pattern for o in outputs)
    assert notes_found, (
        f"{role}.md: output_validator did not find RoleDecisionNotes output"
    )


# ---------------------------------------------------------------------------
# TC-5: Front-matter outputs consistent with Required Outputs (AC6)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role", ROLE_FILES)
def test_front_matter_outputs_match_required_outputs(role: str):
    """TC-5: Front-matter outputs: list matches ## Required Outputs section."""
    content = _load_role_content(role)

    fm, _ = _extract_front_matter(content)
    assert fm is not None, f"{role}.md has no front-matter"

    fm_outputs = set()
    for path in fm.get("outputs", []):
        # Normalize: strip WorkItems/{id}/ prefix and replace {id} with placeholder
        normalized = path.replace("WorkItems/{id}/", "").replace("{id}", "ID")
        fm_outputs.add(normalized)

    # Parse Required Outputs section
    parsed = parse_required_outputs(content, "ID")
    ro_outputs = set()
    for spec in parsed:
        # Normalize: strip WorkItems/ID/ prefix
        normalized = spec.path_or_pattern.replace("WorkItems/ID/", "")
        ro_outputs.add(normalized)

    fm_only = fm_outputs - ro_outputs
    ro_only = ro_outputs - fm_outputs

    assert fm_outputs == ro_outputs, (
        f"{role}.md front-matter/Required Outputs drift:\n"
        f"  In front-matter only: {fm_only or 'none'}\n"
        f"  In Required Outputs only: {ro_only or 'none'}"
    )


# ---------------------------------------------------------------------------
# TC-7: Universal tools present in every role
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role", ROLE_FILES)
def test_universal_tools_in_front_matter(role: str):
    """TC-7: Every role has golazo_status and golazo_transition in tools list."""
    content = _load_role_content(role)
    fm, _ = _extract_front_matter(content)
    assert fm is not None, f"{role}.md has no front-matter"

    tools = fm.get("tools", [])
    assert "golazo_status" in tools, f"{role}.md missing golazo_status in tools"
    assert "golazo_transition" in tools, f"{role}.md missing golazo_transition in tools"


# ---------------------------------------------------------------------------
# TC-8: TechBestPractices path is correct
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("role", TECH_BP_ROLES)
def test_tech_best_practices_path(role: str):
    """TC-8: Roles referencing TechBestPractices use correct deployed path."""
    content = _load_role_content(role)
    _, body = _extract_front_matter(content)

    # Find TechBestPractices references
    refs = re.findall(r'[`\s/]([^\s`]*TechBestPractices[^\s`]*)', body)
    for ref in refs:
        assert ".github/agents/golazo-copilot/roles/TechBestPractices.md" in ref or "TechBestPractices.md" == ref, (
            f"{role}.md references TechBestPractices with unexpected path: '{ref}'"
        )
