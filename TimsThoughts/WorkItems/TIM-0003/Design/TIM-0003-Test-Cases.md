# TIM-0003 — Test Cases

## TC-001: File Existence

**Acceptance Criterion**: `Tims-Delivery-Vision.pptx` exists in `WorkItems/TIM-0003/`

**Test**: 
```powershell
Test-Path "q:\src\Golazo-Copilots\TimsThoughts\WorkItems\TIM-0003\Tims-Delivery-Vision.pptx"
```
**Expected**: `True`  
**Result**: PASS (file exists, 89,098 bytes)

---

## TC-002: Slide Count

**Acceptance Criterion**: File contains 34 slides covering all 5 documents

**Test**:
```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$z = [System.IO.Compression.ZipFile]::OpenRead("...\Tims-Delivery-Vision.pptx")
($z.Entries | Where-Object { $_.FullName -match '^ppt/slides/slide\d+\.xml$' }).Count
$z.Dispose()
```
**Expected**: 34  
**Result**: PASS (34 slide XML parts verified)

---

## TC-003: All 5 Documents Covered

**Acceptance Criterion**: Each document has exactly 1 section divider + 4 content slides

**Test**: Manual review of `Build-SlideDeck.ps1` — 5 section dividers (using ppLayoutTitle) + 20 content slides (4 per doc) confirmed in source.  
**Result**: PASS

---

## TC-004: Corpus Abstract Present

**Acceptance Criterion**: Corpus abstract slide summarizes the entire 5-document model

**Test**: Slide 2 content verified in script — covers urgency argument, four model elements, diagnosis/prescription framing.  
**Result**: PASS

---

## TC-005: File Opens Without Error

**Acceptance Criterion**: File opens in PowerPoint without errors

**Test**: Open `Tims-Delivery-Vision.pptx` in Microsoft PowerPoint.  
**Expected**: No repair dialogs, no missing reference errors, all 34 slides visible  
**Status**: Pending PO validation (requires manual open in PowerPoint)
