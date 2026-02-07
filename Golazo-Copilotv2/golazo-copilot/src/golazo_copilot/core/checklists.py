"""Checklist validation logic."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ChecklistItem

# Valid DoR items
VALID_DOR_ITEMS = {"userStory", "designDoc", "reviewComments", "testCases"}

# Valid DoD items
VALID_DOD_ITEMS = {
    "branchCreated", "testsWrittenFirst", "testsPass",
    "buildPasses", "docsUpdated", "refactorComplete", "committed",
    "retroComplete"
}


def validate_dor_item(item: str) -> tuple[bool, str | None]:
    """
    Validate DoR item name.
    
    Returns:
        Tuple of (is_valid, error_message).
    """
    if item not in VALID_DOR_ITEMS:
        return False, f"Unknown DoR item '{item}'. Valid items: {', '.join(sorted(VALID_DOR_ITEMS))}"
    return True, None


def validate_dod_item(item: str) -> tuple[bool, str | None]:
    """
    Validate DoD item name.
    
    Returns:
        Tuple of (is_valid, error_message).
    """
    if item not in VALID_DOD_ITEMS:
        return False, f"Unknown DoD item '{item}'. Valid items: {', '.join(sorted(VALID_DOD_ITEMS))}"
    return True, None


def _is_item_complete(item: "ChecklistItem | bool") -> bool:
    """Check if a checklist item is complete, supporting both old and new formats."""
    if isinstance(item, bool):
        return item
    return item.complete


def get_missing_items(checklist: "dict[str, ChecklistItem | bool]") -> list[str]:
    """Get list of items that are not complete."""
    return [item for item, value in checklist.items() if not _is_item_complete(value)]


def is_checklist_complete(checklist: "dict[str, ChecklistItem | bool]") -> bool:
    """Check if all items in checklist are complete."""
    return all(_is_item_complete(v) for v in checklist.values())
