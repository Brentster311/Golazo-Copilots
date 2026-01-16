# Photo Organizer

A simple Python tool to organize photos by date into a `YYYY/MM/` folder structure.

## Features

- Scans source folder recursively for photos
- Organizes photos into `YYYY/MM/` subfolders based on date
- Extracts date from EXIF metadata (with Pillow) or falls back to file modification date
- Preserves original files (copies, not moves)
- Handles filename collisions automatically
- Supports JPG, JPEG, PNG, GIF, BMP formats

## Requirements

- Python 3.8+
- Pillow (optional, for EXIF date extraction)

## Installation

```bash
# Clone the repository
git clone https://github.com/Brentster311/Golazo-Copilots
cd Golazo-Copilots/photo_organizer

# (Optional) Install Pillow for EXIF support
pip install Pillow
```

## Usage

```bash
python photo_organizer.py <source_folder> <destination_folder>
```

### Examples

```bash
# Organize photos from Downloads to Pictures
python photo_organizer.py ~/Downloads/photos ~/Pictures/organized

# Windows example
python photo_organizer.py "C:\Users\Me\Photos" "D:\Organized"
```

### Output

```
Scanning: /photos/unsorted
Organizing to: /photos/organized

Processing...
  Copied: IMG_001.jpg -> 2024/01/IMG_001.jpg
  Copied: IMG_002.jpg -> 2024/01/IMG_002.jpg
  Skipped: document.pdf (unsupported format)
  Copied: IMG_003.png -> 2023/12/IMG_003.png

Summary:
  Photos organized: 3
  Files skipped: 1
  Elapsed time: 0.5s
```

## How It Works

1. **Scan**: Recursively finds all photo files in the source folder
2. **Extract Date**: Reads EXIF `DateTimeOriginal` if available; otherwise uses file modification date
3. **Organize**: Copies each photo to `destination/YYYY/MM/filename`
4. **Handle Collisions**: If a file already exists, appends `_2`, `_3`, etc.

## Supported Formats

| Format | Extension |
|--------|-----------|
| JPEG | `.jpg`, `.jpeg` |
| PNG | `.png` |
| GIF | `.gif` |
| BMP | `.bmp` |

## Running Tests

```bash
python -m unittest test_photo_organizer -v
```

## Notes

- Original photos are **not modified or deleted** (copy operation)
- Without Pillow, the tool still works using file modification dates
- Photos without EXIF data use file modification date as fallback

## License

MIT
