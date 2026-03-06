"""Formatting helpers for MCP tool results."""

# Status icons (using ASCII to avoid encoding issues)
ICON_OK = "[OK]"
ICON_FAIL = "[FAIL]"
ICON_WARN = "[WARN]"
ICON_PENDING = "[...]"
ICON_CHECK = "[x]"
ICON_EMPTY = "[ ]"


def format_create_workitem_result(result: dict) -> str:
    """Format golazo_create_workitem result dict into display text."""
    if result["success"]:
        return f"""{ICON_OK} Work item '{result['work_item_id']}' created!

**Current Role:** {result['current_role']}

---
{result['role_instructions']}
"""
    return f"{ICON_FAIL} Failed to create work item: {result['error']}"


def format_transition_result(result: dict) -> str:
    """Format golazo_transition result dict into display text."""
    if result["success"]:
        warning = f"\n{ICON_WARN} {result['warning']}" if result.get("warning") else ""
        closure_label = f" {ICON_WARN} **CLOSURE MODE**" if result.get("closure_pending") else ""
        return f"""{ICON_OK} Transitioned to '{result['current_role']}'!{warning}

**Current Phase:** {result['current_phase']}{closure_label}

---
{result['role_instructions']}
"""
    return f"{ICON_FAIL} Transition failed: {result['error']}"


def format_status_result(result: dict) -> str:
    """Format golazo_status result dict into display text."""
    if result.get("active", False):
        version_warning = ""
        if result.get("version_warning"):
            version_warning = f"\n{ICON_WARN} {result['version_warning']}"

        progress_section = ""
        role_progress = result.get("role_progress", {})
        if role_progress:
            completed = role_progress.get("roles_completed", 0)
            total = role_progress.get("roles_total", 9)
            progress_section = f"\n- Role Progress: {completed}/{total} complete"

        outputs_section = ""
        req_outputs = result.get("required_outputs", {})
        output_list = req_outputs.get("outputs", [])
        if output_list:
            out_valid = sum(1 for output in output_list if output["valid"])
            out_total = len(output_list)
            out_status = f"{ICON_OK} Complete" if req_outputs.get("complete") else f"{ICON_PENDING} {out_valid}/{out_total}"
            out_lines = []
            for output in output_list:
                icon = ICON_CHECK if output["valid"] else ICON_EMPTY
                out_lines.append(f"  {icon} {output['path']}")
            outputs_section = f"\n- Required Outputs: {out_status}\n" + "\n".join(out_lines)

        registry_section = ""
        if result.get("registry_hint"):
            registry_section = f"\n- {result['registry_hint']}"

        tooling_warning_section = ""
        tooling_warnings = result.get("tooling_warnings", [])
        if tooling_warnings:
            tooling_warning_section = "\n- Tooling self-check warnings: " + " | ".join(tooling_warnings)

        next_steps = "\n".join(f"- {step}" for step in result["next_steps"])

        closure_label = ""
        if result.get("closure_pending"):
            closure_label = f" {ICON_WARN} **CLOSURE MODE**"

        deviations_section = ""
        if result.get("deviations"):
            deviations_lines = []
            for deviation in result["deviations"]:
                consumed = " (consumed)" if deviation["consumed"] else ""
                deviations_lines.append(f"- {deviation['id']}: {deviation['action']} - \"{deviation['reason']}\"{consumed}")
            deviations_section = "\n\n**Deviations:**\n" + "\n".join(deviations_lines)

        return f"""**Golazo Status** (v{result['version']}){version_warning}
- Work Item: {result['work_item_id']}
- Current Role: **{result['current_role']}**{closure_label}
    - Phase: {result['current_phase']}{progress_section}{outputs_section}{registry_section}{tooling_warning_section}{deviations_section}

**Next Steps:**
{next_steps}

---
{result['role_instructions']}
"""
    version_info = f" (v{result.get('version', 'unknown')})" if 'version' in result else ""
    tooling_warnings = result.get("tooling_warnings", [])
    tooling_suffix = ""
    if tooling_warnings:
        tooling_suffix = "\n" + "\n".join(f"{ICON_WARN} Tooling self-check: {warning}" for warning in tooling_warnings)
    return f"{ICON_WARN}{version_info} {result.get('message', 'No active work item')}{tooling_suffix}"


def format_bootstrap_result(result: dict) -> str:
    """Format golazo_bootstrap result dict into display text."""
    if result["success"]:
        created = "\n".join(f"  {ICON_CHECK} {item}" for item in result["files_created"]) or "  (none)"
        skipped = "\n".join(f"  {ICON_EMPTY} {item}" for item in result["files_skipped"]) or "  (none)"
        return f"""{ICON_OK} Golazo Copilot bootstrapped!

**Files Created:**
{created}

**Files Skipped (already exist):**
{skipped}

{result['message']}
"""
    error_msg = result['error']
    if "No workspace markers found" in error_msg:
        error_msg += (
            "\n\n**Next step:** Confirm with the user that the workspace_path is correct. "
            "If it is, create a `WorkItems` folder at that path (e.g. `mkdir <workspace_path>/WorkItems`) "
            "and then re-run `golazo_bootstrap`."
        )
    return f"{ICON_FAIL} Bootstrap failed: {error_msg}"


def format_consent_result(result: dict) -> str:
    """Format golazo_consent result dict into display text."""
    if result["success"]:
        return f"""{ICON_OK} Consent recorded!

**Deviation ID:** {result['deviation_id']}
**Action:** {result['action']}

{result['message']}
"""
    return f"{ICON_FAIL} Consent failed: {result['error']}"


def format_capabilities_result(result: dict, action: str, files: list | None = None) -> str:
    """Format golazo_capabilities result dict into display text."""
    if not result["success"]:
        return f"{ICON_FAIL} {result['error']}"
    if result.get("message"):
        return result["message"]
    if action == "list":
        caps = result["capabilities"]
        if not caps:
            return "**Capability Registry** (empty)"
        lines = [f"**Capability Registry** ({len(caps)} capabilities)"]
        for cap in caps:
            lines.append(f"- **{cap['name']}**: {cap['description']}")
        return "\n".join(lines)
    if action == "show":
        cap = result["capability"]
        key_files = ", ".join(cap["key_files"]) or "(none)"
        contracts = "\n  ".join(f"- {contract}" for contract in cap["contracts"]) or "  (none)"
        depends = ", ".join(cap["depends_on"]) or "(none)"
        depended = ", ".join(cap["depended_on_by"]) or "(none)"
        return f"""**Capability: {cap['name']}**
- **Description**: {cap['description']}
- **Key Files**: {key_files}
- **Contracts**:
  {contracts}
- **Depends On**: {depends}
- **Depended On By**: {depended}"""
    if action == "impact":
        direct = result["directly_affected"]
        transitive = result["transitively_affected"]
        total = len(direct) + len(transitive)
        lines = [f"**Impact Analysis** ({len(files or [])} files -> {total} capabilities affected)"]
        if direct:
            lines.append("\n**Directly Affected:**")
            for cap in direct:
                lines.append(f"- **{cap['name']}**: {cap['description']}")
        if transitive:
            lines.append("\n**Transitively Affected (dependents):**")
            for cap in transitive:
                lines.append(f"- **{cap['name']}**: {cap['description']}")
        if not direct and not transitive:
            lines.append("\nNo capabilities affected by the given files.")
        return "\n".join(lines)
    if action == "validate":
        lines = ["**Registry Validation**"]
        for item in result["results"]:
            if item["valid"]:
                lines.append(f"{ICON_OK} **{item['name']}**: all key_files exist")
            else:
                missing = ", ".join(item["missing_files"])
                lines.append(f"{ICON_FAIL} **{item['name']}**: missing {missing}")
        return "\n".join(lines)
    return str(result)


def format_role_context_result(result: dict) -> str:
    """Format golazo_role_context result dict into display text."""
    if result["status"] != "ok":
        return f"{ICON_FAIL} {result['error']}"
    meta = []
    meta.append(f"Role: {result.get('role', 'unknown')}")
    meta.append(f"Artifacts: {result.get('artifact_count', 0)}")
    meta.append(f"Size: {result.get('total_size', 0)} bytes")
    if result.get("truncated"):
        meta.append(f"{ICON_WARN} Some artifacts were truncated")
    header = " | ".join(meta)
    return f"""{ICON_OK} Role context bundled ({header})

{result['bundle']}"""


def format_git_propose_result(result: dict) -> str:
    """Format golazo_git_propose result dict into display text."""
    if not result.get("success"):
        code = result.get("error_code")
        suffix = f" ({code})" if code else ""
        return f"{ICON_FAIL} Git proposal failed{suffix}: {result['error']}"

    proposal = result["proposal"]
    payload = []
    if "files" in proposal:
        payload.append(f"files={proposal['files']}")
    if "message" in proposal:
        payload.append("message=<provided>")
    if "branch" in proposal:
        payload.append(f"branch={proposal['branch']}")
    payload_text = f"\nPayload: {', '.join(payload)}" if payload else ""

    return (
        f"{ICON_OK} Git proposal recorded for '{result['work_item_id']}'.\n\n"
        f"Action: {proposal['action']}\n"
        f"Status: {proposal['status']}\n"
        f"Timestamp: {proposal['timestamp']}\n"
        f"Proposal count: {result['proposal_count']}"
        f"{payload_text}"
    )


def format_transition_workitem_result(result: dict) -> str:
    """Format golazo_transition_workitem result dict into display text."""
    if not result.get("success"):
        code = result.get("error_code")
        suffix = f" ({code})" if code else ""
        return f"{ICON_FAIL} Work-item transition failed{suffix}: {result['error']}"

    guidance = ""
    if not result.get("next_work_item_exists", False):
        guidance = (
            f"\n{ICON_WARN} Next work item does not exist yet. "
            f"Create '{result['next_work_item']}' with golazo_create_workitem."
        )

    created = "yes" if result.get("global_state_created") else "no"
    return (
        f"{ICON_OK} Project-level transition recorded for '{result['work_item_id']}'.\n\n"
        f"Completed work item: {result['completed_work_item']}\n"
        f"Next work item: {result['next_work_item']}\n"
        f"Next work item exists: {'yes' if result.get('next_work_item_exists') else 'no'}\n"
        f"global_state.json created: {created}\n"
        f"global_state.json path: {result['global_state_path']}"
        f"{guidance}"
    )


def format_update_result(result: dict) -> str:
    """Format golazo_update result dict into display text."""
    if result.get("status") == "error":
        msg = f"{ICON_FAIL} {result['error']}"
        if result.get("stderr"):
            msg += f"\n\n```\n{result['stderr']}\n```"
        return msg

    action = result.get("action")

    if action == "check":
        lines = [
            f"{ICON_OK} **Golazo Copilot Version Check**",
            "",
            "Read-only report: this action does not install or modify your environment.",
            "",
            "| Field | Value |",
            "|-------|-------|",
            f"| Current version | {result['current_version']} |",
            f"| Latest stable | {result.get('latest_stable', 'N/A')} |",
        ]
        if result.get("latest_prerelease"):
            lines.append(f"| Latest pre-release | {result['latest_prerelease']} |")
        if result["update_available"]:
            lines.append(f"\n{ICON_WARN} **Update available!** Use `golazo_update(action=\"install\", version=\"<version>\", target=\"active\")` to install.")
        else:
            lines.append(f"\n{ICON_OK} Already up to date.")
        return "\n".join(lines)

    if action == "install":
        target = result.get("target", "active")
        install_cmd = result.get("install_command")
        lines = [
            f"{ICON_OK} **Installed golazo-copilot {result['installed_version']}**",
            "",
            f"Target: `{target}`",
        ]
        if install_cmd:
            lines.extend([
                f"Install command: `{ ' '.join(str(p) for p in install_cmd) }`",
                "",
            ])
        lines.extend([
            f"{ICON_WARN} {result['restart_message']}",
            "",
            "**Post-restart bootstrap options:**",
        ])
        for option in result.get("bootstrap_options", []):
            lines.append(f"- {option}")
        return "\n".join(lines)

    return str(result)
