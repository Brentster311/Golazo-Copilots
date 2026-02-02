"""Checklist validation logic."""

# Valid DoR items
VALID_DOR_ITEMS = {"userStory", "designDoc", "reviewComments", "testCases"}

# Valid DoD items
VALID_DOD_ITEMS = {
    "branchCreated", "testsWrittenFirst", "testsPass",
    "buildPasses", "docsUpdated", "refactorComplete", "committed"
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


def get_missing_items(checklist: dict[str, bool]) -> list[str]:
    """Get list of items that are not complete."""
    return [item for item, complete in checklist.items() if not complete]


def is_checklist_complete(checklist: dict[str, bool]) -> bool:
    """Check if all items in checklist are complete."""
    return all(checklist.values())
