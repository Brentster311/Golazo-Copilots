"""gcp_mark_dor and gcp_mark_dod tools - Mark checklist items."""

from datetime import datetime, timezone
from pathlib import Path

from ..core.persistence import load_state, save_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..core.checklists import (
    validate_dor_item,
    validate_dod_item,
    get_missing_items,
    is_checklist_complete,
    VALID_DOR_ITEMS,
    VALID_DOD_ITEMS,
)
from ..core.types import ChecklistItem
from ..core.evidence import validate_evidence, get_evidence_hint


async def gcp_mark_dor(
    work_item_id: str,
    item: str | None = None,
    items: dict[str, bool] | None = None,
    complete: bool = True,
    evidence: str | None = None,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
) -> dict:
    """
    Mark DoR item(s) as complete or incomplete.
    
    Args:
        work_item_id: Work item identifier
        item: Single item to mark (use with complete)
        items: Dict of items to mark (bulk update)
        complete: Value for single item
        evidence: Evidence supporting the claim (file path, etc.)
        work_items_dir: Work items directory
    
    Returns:
        Dict with success, current checklist state, and missing items
    """
    return await _mark_checklist(
        work_item_id=work_item_id,
        checklist_type="dor",
        item=item,
        items=items,
        complete=complete,
        evidence=evidence,
        work_items_dir=work_items_dir,
        valid_items=VALID_DOR_ITEMS,
        validate_fn=validate_dor_item,
    )


async def gcp_mark_dod(
    work_item_id: str,
    item: str | None = None,
    items: dict[str, bool] | None = None,
    complete: bool = True,
    evidence: str | None = None,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
) -> dict:
    """
    Mark DoD item(s) as complete or incomplete.
    
    Args:
        work_item_id: Work item identifier
        item: Single item to mark (use with complete)
        items: Dict of items to mark (bulk update)
        complete: Value for single item
        evidence: Evidence supporting the claim (file path, etc.)
        work_items_dir: Work items directory
    
    Returns:
        Dict with success, current checklist state, and missing items
    """
    return await _mark_checklist(
        work_item_id=work_item_id,
        checklist_type="dod",
        item=item,
        items=items,
        complete=complete,
        evidence=evidence,
        work_items_dir=work_items_dir,
        valid_items=VALID_DOD_ITEMS,
        validate_fn=validate_dod_item,
    )


async def _mark_checklist(
    work_item_id: str,
    checklist_type: str,
    item: str | None,
    items: dict[str, bool] | None,
    complete: bool,
    evidence: str | None,
    work_items_dir: Path,
    valid_items: set[str],
    validate_fn,
) -> dict:
    """Internal implementation for marking checklist items."""
    
    # Check work item exists
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error": f"Work item '{work_item_id}' does not exist.",
        }
    
    # Build updates dict
    updates: dict[str, bool] = {}
    
    if item is not None:
        # Single item update
        valid, error = validate_fn(item)
        if not valid:
            return {"success": False, "error": error}
        updates[item] = complete
    
    if items is not None:
        # Bulk update - validate all items first
        for item_name in items:
            valid, error = validate_fn(item_name)
            if not valid:
                return {"success": False, "error": error}
        updates.update(items)
    
    if not updates:
        return {
            "success": False,
            "error": "No items specified. Provide 'item' or 'items' parameter.",
        }
    
    # Evidence validation: required when marking complete (but not when unmarking)
    marking_complete = any(v for v in updates.values())
    if marking_complete:
        if evidence is None:
            # Get hint for the first item being marked complete
            first_item = next((k for k, v in updates.items() if v), list(updates.keys())[0])
            hint = get_evidence_hint(first_item, work_item_id)
            return {
                "success": False,
                "error": f"Missing evidence for '{first_item}'. Expected: {hint}",
            }
        
        # Validate the evidence
        # Only validate for the single item case (bulk updates require more complex evidence handling)
        if item is not None and complete:
            result = validate_evidence(item, evidence, work_items_dir)
            if not result.valid:
                return {
                    "success": False,
                    "error": result.message,
                }
            # Use normalized path if available
            validated_evidence = result.normalized_path or evidence
        else:
            validated_evidence = evidence
    else:
        validated_evidence = None
    
    # Load current state
    state = load_state(work_item_id, work_items_dir)
    
    # Get checklist
    checklist = state.dor if checklist_type == "dor" else state.dod
    
    # Check for unmarking (complete=False)
    warning = None
    for item_name, value in updates.items():
        if not value and checklist.get(item_name) and checklist[item_name].complete:
            warning = f"Unmarking {item_name}. This may affect workflow gates."
    
    # Apply updates
    now = datetime.now(timezone.utc)
    for item_name, value in updates.items():
        if item_name not in checklist:
            checklist[item_name] = ChecklistItem()
        checklist[item_name].complete = value
        if value and validated_evidence:
            checklist[item_name].evidence = validated_evidence
            checklist[item_name].validated_at = now
        elif not value:
            # Clear evidence when unmarking
            checklist[item_name].evidence = None
            checklist[item_name].validated_at = None
    
    # Update state
    state.updated_at = now
    if checklist_type == "dor":
        state.dor = checklist
    else:
        state.dod = checklist
    
    # Save state
    save_state(work_item_id, state, work_items_dir)
    
    # Build response with simplified checklist view
    items_summary = {k: v.complete for k, v in checklist.items()}
    
    result = {
        "success": True,
        "checklist": checklist_type,
        "items": items_summary,
        "complete": is_checklist_complete(checklist),
        "missing": get_missing_items(checklist),
    }
    
    if validated_evidence:
        result["evidence"] = validated_evidence
    
    if warning:
        result["warning"] = warning
    
    return result
