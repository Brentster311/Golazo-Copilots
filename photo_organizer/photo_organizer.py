#!/usr/bin/env python3
"""
Photo Organizer - WIP-001
Organizes photos by date into YYYY/MM folder structure.
"""

import argparse
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Supported photo extensions (case-insensitive)
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}


def get_exif_date(file_path: Path) -> Optional[datetime]:
    """
    Extract date from EXIF metadata.
    Returns None if EXIF data is unavailable or corrupted.
    """
    if not PILLOW_AVAILABLE:
        return None
    
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data is None:
                return None
            
            # Look for DateTimeOriginal (tag 36867) or DateTime (tag 306)
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == 'DateTimeOriginal':
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                elif tag_name == 'DateTime' and tag_id == 306:
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        # Corrupted EXIF or other error - return None to trigger fallback
        return None
    
    return None


def get_file_date(file_path: Path) -> datetime:
    """
    Get file modification date as fallback.
    """
    mtime = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mtime)


def get_photo_date(file_path: Path) -> Tuple[datetime, str]:
    """
    Get the date for a photo, preferring EXIF, falling back to file date.
    Returns (date, source) where source is 'exif' or 'file'.
    """
    exif_date = get_exif_date(file_path)
    if exif_date:
        return exif_date, 'exif'
    return get_file_date(file_path), 'file'


def is_supported_photo(file_path: Path) -> bool:
    """
    Check if the file is a supported photo format.
    """
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def get_unique_destination_path(dest_path: Path) -> Path:
    """
    Get a unique destination path, handling filename collisions.
    If file exists, appends _2, _3, etc.
    """
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    
    counter = 2
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def scan_photos(source_folder: Path) -> list:
    """
    Recursively scan source folder for photo files.
    Returns list of Path objects.
    """
    return [
        file_path
        for file_path in source_folder.rglob('*')
        if file_path.is_file() and is_supported_photo(file_path)
    ]


def organize_photos(source_folder: str, dest_folder: str) -> Tuple[int, int, list]:
    """
    Main function to organize photos from source to destination.
    Returns (organized_count, skipped_count, errors_list).
    """
    source_path = Path(source_folder).resolve()
    dest_path = Path(dest_folder).resolve()
    
    # Validate source folder
    if not source_path.exists():
        raise FileNotFoundError(f"Source folder does not exist: {source_path}")
    if not source_path.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source_path}")
    
    # Create destination folder if needed
    dest_path.mkdir(parents=True, exist_ok=True)
    
    organized_count = 0
    skipped_count = 0
    errors = []
    
    # Scan all files in source
    for file_path in source_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        if not is_supported_photo(file_path):
            print(f"  Skipped: {file_path.name} (unsupported format)")
            skipped_count += 1
            continue
        
        try:
            # Get photo date
            photo_date, date_source = get_photo_date(file_path)
            
            # Build destination path: dest/YYYY/MM/filename
            year_month_folder = dest_path / f"{photo_date.year}" / f"{photo_date.month:02d}"
            year_month_folder.mkdir(parents=True, exist_ok=True)
            
            dest_file_path = year_month_folder / file_path.name
            dest_file_path = get_unique_destination_path(dest_file_path)
            
            # Copy file (preserving metadata)
            shutil.copy2(file_path, dest_file_path)
            
            relative_dest = dest_file_path.relative_to(dest_path)
            print(f"  Copied: {file_path.name} -> {relative_dest}")
            organized_count += 1
            
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {e}"
            print(f"  {error_msg}")
            errors.append(error_msg)
    
    return organized_count, skipped_count, errors


def main() -> int:
    """
    Main entry point for CLI.
    Returns exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description='Organize photos by date into YYYY/MM folder structure.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python photo_organizer.py /photos/unsorted /photos/organized
  python photo_organizer.py "C:\\Users\\Photos" "D:\\Organized"
        '''
    )
    parser.add_argument(
        'source_folder',
        help='Source folder containing photos to organize'
    )
    parser.add_argument(
        'destination_folder',
        help='Destination folder for organized photos (YYYY/MM structure)'
    )
    
    args = parser.parse_args()
    
    # Check Pillow availability
    if not PILLOW_AVAILABLE:
        print("Warning: Pillow not installed. EXIF dates unavailable.")
        print("Install with: pip install Pillow")
        print("Using file modification dates as fallback.\n")
    
    print(f"Scanning: {args.source_folder}")
    print(f"Organizing to: {args.destination_folder}\n")
    print("Processing...")
    
    start_time = time.time()
    
    try:
        organized, skipped, errors = organize_photos(
            args.source_folder,
            args.destination_folder
        )
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        return 1
    except NotADirectoryError as e:
        print(f"\nError: {e}")
        return 1
    except PermissionError as e:
        print(f"\nError: Permission denied - {e}")
        return 1
    
    elapsed = time.time() - start_time
    
    print(f"\nSummary:")
    print(f"  Photos organized: {organized}")
    print(f"  Files skipped: {skipped}")
    print(f"  Elapsed time: {elapsed:.1f}s")
    
    if errors:
        print(f"  Errors: {len(errors)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
