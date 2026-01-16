# Test Cases: CALJACK-001

**Work Item**: CALJACK-001 - Main Menu and Game Window Foundation  
**Tester**: Golazo Tester Role  
**Date**: 2025-01-XX

---

## Test Coverage Summary

| Acceptance Criteria | Test Cases | Coverage |
|---------------------|------------|----------|
| AC #1: Window launches (1024x768) | TC-001, TC-002 | ? |
| AC #2: "New Game" button displayed | TC-003 | ? |
| AC #3: "Help" button displayed | TC-004 | ? |
| AC #4: "New Game" transitions to game screen | TC-005, TC-006 | ? |
| AC #5: "Help" transitions to help screen | TC-007, TC-008 | ? |
| NFR-001: Window responds to close button | TC-009 | ? |
| NFR-002: Buttons respond within 100ms | TC-010 | ? |

---

## Test Cases

### TC-001: Window launches successfully

**Maps to**: AC #1  
**Type**: Integration  
**Priority**: High

**Preconditions**:
- pygame installed
- Display available

**Steps**:
1. Run `python main.py`
2. Observe window creation

**Expected Result**:
- Pygame window opens without error
- Window title is "California Jack" (or similar)

**Failure Message**: "Window failed to launch - pygame initialization error"

---

### TC-002: Window has correct dimensions

**Maps to**: AC #1  
**Type**: Unit  
**Priority**: High

**Preconditions**:
- Game window created

**Test Code** (pytest):
```python
def test_window_dimensions():
    """Window should be 1024x768 pixels."""
    from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT
    
    assert WINDOW_WIDTH == 1024, f"Expected width 1024, got {WINDOW_WIDTH}"
    assert WINDOW_HEIGHT == 768, f"Expected height 768, got {WINDOW_HEIGHT}"
```

**Expected Result**: Constants define 1024x768

**Failure Message**: "Window dimensions incorrect - expected 1024x768"

---

### TC-003: New Game button is displayed

**Maps to**: AC #2  
**Type**: Integration (Manual)  
**Priority**: High

**Preconditions**:
- Game launched
- Main menu state active

**Steps**:
1. Launch game
2. Observe main menu

**Expected Result**:
- Button labeled "New Game" is visible
- Button is positioned in center area of screen
- Button text is readable

**Failure Message**: "New Game button not visible or not readable"

---

### TC-004: Help button is displayed

**Maps to**: AC #3  
**Type**: Integration (Manual)  
**Priority**: High

**Preconditions**:
- Game launched
- Main menu state active

**Steps**:
1. Launch game
2. Observe main menu

**Expected Result**:
- Button labeled "Help" is visible
- Button is positioned below "New Game" button
- Button text is readable

**Failure Message**: "Help button not visible or not readable"

---

### TC-005: New Game button click transitions to game state

**Maps to**: AC #4  
**Type**: Unit  
**Priority**: High

**Test Code** (pytest):
```python
def test_new_game_button_transitions_to_game_state():
    """Clicking New Game should return 'game' state name."""
    from game.states.menu_state import MenuState
    from unittest.mock import MagicMock
    import pygame
    
    menu = MenuState()
    
    # Create mock click event at New Game button location
    click_event = MagicMock()
    click_event.type = pygame.MOUSEBUTTONDOWN
    click_event.button = 1  # Left click
    click_event.pos = menu.new_game_button.rect.center
    
    result = menu.handle_event(click_event)
    
    assert result == "game", f"Expected 'game' state, got '{result}'"
```

**Expected Result**: Returns "game" state name

**Failure Message**: "New Game button click did not transition to game state"

---

### TC-006: New Game button click outside bounds does nothing

**Maps to**: AC #4 (edge case)  
**Type**: Unit  
**Priority**: Medium

**Test Code** (pytest):
```python
def test_click_outside_new_game_button_does_nothing():
    """Clicking outside button should not trigger transition."""
    from game.states.menu_state import MenuState
    from unittest.mock import MagicMock
    import pygame
    
    menu = MenuState()
    
    # Create mock click event outside button
    click_event = MagicMock()
    click_event.type = pygame.MOUSEBUTTONDOWN
    click_event.button = 1
    click_event.pos = (0, 0)  # Top-left corner, outside buttons
    
    result = menu.handle_event(click_event)
    
    assert result is None, f"Expected None (no transition), got '{result}'"
```

**Expected Result**: Returns None (no state change)

**Failure Message**: "Click outside button incorrectly triggered transition"

---

### TC-007: Help button click transitions to help state

**Maps to**: AC #5  
**Type**: Unit  
**Priority**: High

**Test Code** (pytest):
```python
def test_help_button_transitions_to_help_state():
    """Clicking Help should return 'help' state name."""
    from game.states.menu_state import MenuState
    from unittest.mock import MagicMock
    import pygame
    
    menu = MenuState()
    
    # Create mock click event at Help button location
    click_event = MagicMock()
    click_event.type = pygame.MOUSEBUTTONDOWN
    click_event.button = 1
    click_event.pos = menu.help_button.rect.center
    
    result = menu.handle_event(click_event)
    
    assert result == "help", f"Expected 'help' state, got '{result}'"
```

**Expected Result**: Returns "help" state name

**Failure Message**: "Help button click did not transition to help state"

---

### TC-008: Game state placeholder displays content

**Maps to**: AC #4 (placeholder verification)  
**Type**: Integration (Manual)  
**Priority**: Medium

**Preconditions**:
- Game launched
- Clicked "New Game"

**Steps**:
1. Launch game
2. Click "New Game" button
3. Observe game screen

**Expected Result**:
- Screen changes from menu
- Placeholder text visible (e.g., "Game Screen - Coming Soon")

**Failure Message**: "Game state placeholder not displayed or blank screen"

---

### TC-009: Window close button terminates application

**Maps to**: NFR-001  
**Type**: Integration (Manual)  
**Priority**: High

**Preconditions**:
- Game window open

**Steps**:
1. Launch game
2. Click window close button (X)

**Expected Result**:
- Window closes
- Application terminates cleanly (no error)
- Process exits

**Failure Message**: "Window did not close or application hung"

---

### TC-010: Button response time under 100ms

**Maps to**: NFR-002  
**Type**: Performance  
**Priority**: Medium

**Test Code** (pytest):
```python
import time

def test_button_response_time():
    """Button click should respond in under 100ms."""
    from game.states.menu_state import MenuState
    from unittest.mock import MagicMock
    import pygame
    
    menu = MenuState()
    
    click_event = MagicMock()
    click_event.type = pygame.MOUSEBUTTONDOWN
    click_event.button = 1
    click_event.pos = menu.new_game_button.rect.center
    
    start = time.perf_counter()
    menu.handle_event(click_event)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    assert elapsed_ms < 100, f"Response took {elapsed_ms:.2f}ms, expected <100ms"
```

**Expected Result**: Response in under 100ms

**Failure Message**: "Button response exceeded 100ms threshold"

---

## Edge Cases

### TC-011: Right-click on button does nothing

**Maps to**: AC #4, AC #5 (edge case)  
**Type**: Unit  
**Priority**: Low

**Test Code** (pytest):
```python
def test_right_click_does_nothing():
    """Right-click should not trigger button action."""
    from game.states.menu_state import MenuState
    from unittest.mock import MagicMock
    import pygame
    
    menu = MenuState()
    
    click_event = MagicMock()
    click_event.type = pygame.MOUSEBUTTONDOWN
    click_event.button = 3  # Right click
    click_event.pos = menu.new_game_button.rect.center
    
    result = menu.handle_event(click_event)
    
    assert result is None, "Right-click should not trigger transition"
```

**Expected Result**: Returns None

**Failure Message**: "Right-click incorrectly triggered button action"

---

### TC-012: Keyboard events do not trigger buttons

**Maps to**: AC #2, AC #3 (edge case)  
**Type**: Unit  
**Priority**: Low

**Test Code** (pytest):
```python
def test_keyboard_does_not_trigger_buttons():
    """Keyboard events should not trigger button actions."""
    from game.states.menu_state import MenuState
    from unittest.mock import MagicMock
    import pygame
    
    menu = MenuState()
    
    key_event = MagicMock()
    key_event.type = pygame.KEYDOWN
    key_event.key = pygame.K_RETURN
    
    result = menu.handle_event(key_event)
    
    assert result is None, "Keyboard should not trigger button transition"
```

**Expected Result**: Returns None

**Failure Message**: "Keyboard incorrectly triggered button action"

---

## Error Cases

### TC-013: State manager handles invalid state name gracefully

**Maps to**: Architect observation (failure isolation)  
**Type**: Unit  
**Priority**: Medium

**Test Code** (pytest):
```python
def test_invalid_state_name_handled():
    """Invalid state name should not crash application."""
    from game.state_manager import StateManager
    
    manager = StateManager()
    
    # Attempt transition to non-existent state
    try:
        manager.change_state("nonexistent")
        # Should either log warning or raise controlled exception
    except KeyError:
        pass  # Acceptable if raises KeyError
    except Exception as e:
        pytest.fail(f"Unexpected exception type: {type(e)}")
```

**Expected Result**: Graceful handling (warning or controlled exception)

**Failure Message**: "Invalid state name caused uncontrolled crash"

---

## Test Execution Plan

### Automated Tests (pytest)
```
tests/
??? test_constants.py       # TC-002
??? test_menu_state.py      # TC-005, TC-006, TC-007, TC-010, TC-011, TC-012
??? test_state_manager.py   # TC-013
```

### Manual Tests
- TC-001: Window launch (smoke test)
- TC-003: New Game button visible
- TC-004: Help button visible
- TC-008: Game state placeholder
- TC-009: Window close

### Test Commands
```bash
# Run all automated tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=game --cov-report=term-missing
```

---

## Justification for Manual Tests

Some tests require manual execution because:
1. **Visual verification** (TC-003, TC-004, TC-008): Cannot programmatically verify button is "readable"
2. **System interaction** (TC-001, TC-009): Window creation and close require display
3. **Pygame display dependency**: Automated tests can use mock, but true integration requires display

**Follow-up plan**: Consider pygame headless mode or screenshot comparison for CI in future iteration.
