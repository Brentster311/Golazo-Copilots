# Test Cases: WIP-001 - Organize Photos by Date/Time

## Acceptance Criteria Mapping

| AC | Description | Test Cases |
|----|-------------|------------|
| AC-1 | User can specify source folder | TC-01, TC-02, TC-03 |
| AC-2 | User can specify destination folder | TC-04, TC-05 |
| AC-3 | Photos copied to YYYY/MM/ structure | TC-06, TC-07, TC-08 |
| AC-4 | EXIF fallback to file date | TC-09, TC-10 |
| AC-5 | Unsupported files skipped with warning | TC-11, TC-12 |
| AC-6 | Summary displayed | TC-13 |

---

## Test Cases

### TC-01: Valid source folder with photos
**Type**: Happy Path  
**Maps to**: AC-1, AC-3

**Given**: A source folder containing 3 JPG photos with EXIF dates  
**When**: User runs `python photo_organizer.py <source> <dest>`  
**Then**: 
- Exit code is 0
- All 3 photos are copied to destination
- Photos are in correct YYYY/MM/ folders based on EXIF date

---

### TC-02: Source folder does not exist
**Type**: Error Case  
**Maps to**: AC-1

**Given**: A source path that does not exist  
**When**: User runs `python photo_organizer.py /nonexistent <dest>`  
**Then**:
- Exit code is non-zero
- Error message: "Source folder does not exist: /nonexistent"
- No files are copied

---

### TC-03: Source folder is empty
**Type**: Edge Case  
**Maps to**: AC-1

**Given**: An empty source folder  
**When**: User runs `python photo_organizer.py <empty_source> <dest>`  
**Then**:
- Exit code is 0
- Summary shows: "Photos organized: 0"
- No error messages

---

### TC-04: Destination folder created if not exists
**Type**: Happy Path  
**Maps to**: AC-2

**Given**: A destination path that does not exist  
**When**: User runs `python photo_organizer.py <source> <new_dest>`  
**Then**:
- Destination folder is created
- Photos are copied successfully
- Exit code is 0

---

### TC-05: Destination folder not writable
**Type**: Error Case  
**Maps to**: AC-2

**Given**: A destination path that is not writable (permission denied)  
**When**: User runs `python photo_organizer.py <source> <readonly_dest>`  
**Then**:
- Exit code is non-zero
- Error message indicates permission issue
- No partial results

---

### TC-06: Photos organized by EXIF date
**Type**: Happy Path  
**Maps to**: AC-3

**Given**: 
- Photo A with EXIF date 2024-01-15
- Photo B with EXIF date 2024-03-20
- Photo C with EXIF date 2023-12-25

**When**: User runs organizer  
**Then**:
- Photo A is in `<dest>/2024/01/`
- Photo B is in `<dest>/2024/03/`
- Photo C is in `<dest>/2023/12/`

---

### TC-07: Nested source folders scanned recursively
**Type**: Happy Path  
**Maps to**: AC-3

**Given**: Source folder with structure:
```
source/
  photo1.jpg
  subfolder/
    photo2.jpg
    deeper/
      photo3.jpg
```

**When**: User runs organizer  
**Then**: All 3 photos are found and organized

---

### TC-08: Filename collision handled
**Type**: Edge Case  
**Maps to**: AC-3

**Given**: 
- Two different photos both named `IMG_001.jpg` with same EXIF month

**When**: User runs organizer  
**Then**:
- First photo: `<dest>/2024/01/IMG_001.jpg`
- Second photo: `<dest>/2024/01/IMG_001_2.jpg`
- Both files preserved, no overwrite

---

### TC-09: Photo without EXIF uses file date
**Type**: Happy Path  
**Maps to**: AC-4

**Given**: A PNG file without EXIF data, file modified on 2024-02-10  
**When**: User runs organizer  
**Then**: Photo is copied to `<dest>/2024/02/`

---

### TC-10: Photo with corrupted EXIF uses file date
**Type**: Edge Case  
**Maps to**: AC-4

**Given**: A JPG file with corrupted/unreadable EXIF data  
**When**: User runs organizer  
**Then**: 
- Photo is still processed using file modification date
- Warning message logged
- Photo copied to correct folder

---

### TC-11: Non-image files skipped
**Type**: Happy Path  
**Maps to**: AC-5

**Given**: Source folder containing:
- photo.jpg
- document.pdf
- readme.txt

**When**: User runs organizer  
**Then**:
- Only photo.jpg is copied
- Warning: "Skipped: document.pdf (unsupported format)"
- Warning: "Skipped: readme.txt (unsupported format)"

---

### TC-12: All supported formats processed
**Type**: Happy Path  
**Maps to**: AC-5

**Given**: Source folder with: test.jpg, test.jpeg, test.png, test.gif, test.bmp  
**When**: User runs organizer  
**Then**: All 5 files are copied (0 skipped)

---

### TC-13: Summary statistics displayed
**Type**: Happy Path  
**Maps to**: AC-6

**Given**: Source with 5 photos and 2 non-photos  
**When**: User runs organizer  
**Then**: Output includes:
- "Photos organized: 5"
- "Files skipped: 2"
- "Elapsed time: X.Xs"

---

## Performance Tests

### TC-14: 1000+ photos handled
**Type**: Performance  
**Maps to**: NFR-1, NFR-2

**Given**: Source folder with 1000 small JPG files  
**When**: User runs organizer  
**Then**:
- Completes without crash
- Completes in < 60 seconds
- All photos organized correctly

---

## Security Tests

### TC-15: Path traversal prevented
**Type**: Security

**Given**: Malicious input attempting path traversal  
**When**: User runs `python photo_organizer.py ../../../etc <dest>`  
**Then**: 
- Path is validated/normalized
- No access outside intended directories

---

## Test Data Requirements

| Item | Description |
|------|-------------|
| test_photos/ | Folder with sample photos (various formats) |
| test_photos_exif/ | Photos with known EXIF dates |
| test_photos_no_exif/ | Photos without EXIF data |
| test_photos_mixed/ | Mix of photos and non-photos |
