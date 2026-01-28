<!-- Golazo Version: 1.1.0 -->
# PowerShell Terminal Guide

## When to Use

Consult this guide when:
- Writing files via terminal commands in PowerShell
- Encountering `SyntaxError: source code string cannot contain null bytes`
- Files appear to have content but Python can't import them
- Tests fail on import but source files look correct

---

## Problem

**CRITICAL**: PowerShell has encoding behaviors that corrupt Python files.

PowerShell's default file output uses UTF-16 LE encoding with BOM, which Python interprets as null bytes causing `SyntaxError: source code string cannot contain null bytes`.

---

## Mandatory Patterns

### 1. NEVER use PowerShell native file operations for Python files

? **Do NOT use:**
```powershell
echo "content" > file.py
"content" | Out-File file.py
Set-Content file.py -Value "content"
```

### 2. ALWAYS use this pattern for writing files

? **Use this pattern:**
```powershell
cmd /c "python -c ""import base64; c=base64.b64decode('BASE64_CONTENT').decode('utf-8'); open(r'PATH', 'w', encoding='utf-8').write(c); print('OK')"""
```

### 3. ALWAYS verify file encoding after writing

```powershell
cmd /c "python -c ""print('NULL' if b'\x00' in open(r'PATH','rb').read() else 'CLEAN')"""
```

### 4. If `create_file` tool reports success, verify on disk

```powershell
cmd /c "dir PATH"
```

The IDE buffer and filesystem may be out of sync.

### 5. Clear Python cache after fixing encoding issues

```powershell
cmd /c "python -c ""import shutil,os; [shutil.rmtree(os.path.join(r,d)) for r,dirs,_ in os.walk(r'PROJECT_PATH') for d in dirs if d=='__pycache__']"""
```

---

## Why `cmd /c`?

- Bypasses PowerShell's quote parsing entirely
- Uses CMD's simpler escaping rules (double quotes = `""`)
- Avoids UTF-16 BOM encoding issues

---

## Symptoms of Encoding Problems

| Symptom | Likely Cause |
|---------|--------------|
| `SyntaxError: source code string cannot contain null bytes` | UTF-16 BOM in Python file |
| Files appear to have content but Python can't import them | Encoding mismatch |
| Tests fail on import but source files look correct | Null bytes in file |

---

## Quick Reference

```powershell
# Write file safely (replace BASE64_CONTENT and PATH)
cmd /c "python -c ""import base64; c=base64.b64decode('BASE64_CONTENT').decode('utf-8'); open(r'PATH', 'w', encoding='utf-8').write(c); print('OK')"""

# Check file for null bytes
cmd /c "python -c ""print('NULL' if b'\x00' in open(r'PATH','rb').read() else 'CLEAN')"""

# Clear __pycache__ directories
cmd /c "python -c ""import shutil,os; [shutil.rmtree(os.path.join(r,d)) for r,dirs,_ in os.walk(r'PROJECT_PATH') for d in dirs if d=='__pycache__']"""
```
