# Test Cases: Python Code Sandbox App

## Test Case 1: Basic Code Execution
**Maps to:** AC - User can click a "Run" button to execute the code
- **Input:** `print("Hello, World!")`
- **Expected:** Output area shows `Hello, World!`
- **Type:** Happy path

## Test Case 2: Multi-line Code Execution
**Maps to:** AC - User can enter Python code in a multi-line text input
- **Input:**
  ```python
  x = 5
  y = 10
  print(x + y)
  ```
- **Expected:** Output area shows `15`
- **Type:** Happy path

## Test Case 3: Syntax Error Handling
**Maps to:** AC - Errors are caught and displayed gracefully
- **Input:** `print("unclosed`
- **Expected:** Output shows syntax error message
- **Type:** Error case

## Test Case 4: Runtime Error Handling
**Maps to:** AC - Errors are caught and displayed gracefully
- **Input:** `print(1/0)`
- **Expected:** Output shows `ZeroDivisionError` message
- **Type:** Error case

## Test Case 5: Blocked Builtin - open()
**Maps to:** AC - Execution is sandboxed
- **Input:** `open("test.txt", "w")`
- **Expected:** Error indicating `open` is not allowed
- **Type:** Security/Negative

## Test Case 6: Blocked Builtin - __import__()
**Maps to:** AC - Execution is sandboxed
- **Input:** `__import__("os")`
- **Expected:** Error indicating `__import__` is not allowed
- **Type:** Security/Negative

## Test Case 7: Blocked Builtin - eval()
**Maps to:** AC - Execution is sandboxed
- **Input:** `eval("1+1")`
- **Expected:** Error indicating `eval` is not allowed
- **Type:** Security/Negative

## Test Case 8: Allowed Builtins Work
**Maps to:** AC - Output is displayed
- **Input:**
  ```python
  nums = [1, 2, 3, 4, 5]
  print(sum(nums))
  print(len(nums))
  print(max(nums))
  ```
- **Expected:** Output shows `15`, `5`, `5` on separate lines
- **Type:** Happy path

## Test Case 9: Timeout on Infinite Loop
**Maps to:** AC - Execution has a timeout
- **Input:** `while True: pass`
- **Expected:** Execution stops after ~5 seconds with timeout message
- **Type:** Edge case

## Test Case 10: Empty Input
**Maps to:** AC - Errors are caught and displayed gracefully
- **Input:** (empty)
- **Expected:** No error, output area remains empty or shows nothing
- **Type:** Edge case

## Test Case 11: GUI Launches
**Maps to:** AC - Application launches with a GUI window
- **Action:** Run the application
- **Expected:** Window appears with input area, output area, and Run button
- **Type:** Happy path (manual)

## Test Case 12: Clear Functionality
**Maps to:** Functional requirement - Clear button
- **Action:** Enter code, run it, then click Clear
- **Expected:** Both input and output areas are cleared
- **Type:** Happy path (manual)
