#!/usr/bin/env python3
"""
Test Suite for Photo Organizer - WIP-001
Maps to test cases in docs/tests/WIP-001-test-cases.md
"""

import os
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module under test
import photo_organizer
from photo_organizer import (
    is_supported_photo,
    get_file_date,
    get_unique_destination_path,
    organize_photos,
    main,
    SUPPORTED_EXTENSIONS,
)


class TestSupportedFormats(unittest.TestCase):
    """TC-12: All supported formats processed"""
    
    def test_jpg_supported(self):
        self.assertTrue(is_supported_photo(Path("test.jpg")))
    
    def test_jpeg_supported(self):
        self.assertTrue(is_supported_photo(Path("test.jpeg")))
    
    def test_png_supported(self):
        self.assertTrue(is_supported_photo(Path("test.png")))
    
    def test_gif_supported(self):
        self.assertTrue(is_supported_photo(Path("test.gif")))
    
    def test_bmp_supported(self):
        self.assertTrue(is_supported_photo(Path("test.bmp")))
    
    def test_uppercase_extension_supported(self):
        self.assertTrue(is_supported_photo(Path("test.JPG")))
        self.assertTrue(is_supported_photo(Path("test.PNG")))
    
    def test_pdf_not_supported(self):
        self.assertFalse(is_supported_photo(Path("document.pdf")))
    
    def test_txt_not_supported(self):
        self.assertFalse(is_supported_photo(Path("readme.txt")))


class TestFilenameCollision(unittest.TestCase):
    """TC-08: Filename collision handled"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_no_collision_returns_original(self):
        dest_path = Path(self.temp_dir) / "IMG_001.jpg"
        result = get_unique_destination_path(dest_path)
        self.assertEqual(result, dest_path)
    
    def test_collision_adds_counter(self):
        # Create existing file
        existing = Path(self.temp_dir) / "IMG_001.jpg"
        existing.touch()
        
        result = get_unique_destination_path(existing)
        expected = Path(self.temp_dir) / "IMG_001_2.jpg"
        self.assertEqual(result, expected)
    
    def test_multiple_collisions(self):
        # Create existing files
        (Path(self.temp_dir) / "IMG_001.jpg").touch()
        (Path(self.temp_dir) / "IMG_001_2.jpg").touch()
        (Path(self.temp_dir) / "IMG_001_3.jpg").touch()
        
        result = get_unique_destination_path(Path(self.temp_dir) / "IMG_001.jpg")
        expected = Path(self.temp_dir) / "IMG_001_4.jpg"
        self.assertEqual(result, expected)


class TestOrganizePhotosIntegration(unittest.TestCase):
    """Integration tests for organize_photos function"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.dest_dir = Path(self.temp_dir) / "dest"
        self.source_dir.mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def _create_test_photo(self, folder: Path, name: str, mtime: datetime = None):
        """Helper to create a test photo file"""
        photo_path = folder / name
        photo_path.parent.mkdir(parents=True, exist_ok=True)
        # Create a minimal valid image (1x1 pixel PNG)
        # PNG header + minimal IHDR + IDAT + IEND
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        photo_path.write_bytes(png_data)
        
        if mtime:
            timestamp = mtime.timestamp()
            os.utime(photo_path, (timestamp, timestamp))
        
        return photo_path
    
    def test_tc01_valid_source_with_photos(self):
        """TC-01: Valid source folder with photos"""
        # Create test photos with specific file dates
        self._create_test_photo(
            self.source_dir, "photo1.png",
            datetime(2024, 1, 15, 10, 30)
        )
        self._create_test_photo(
            self.source_dir, "photo2.png",
            datetime(2024, 1, 20, 14, 0)
        )
        
        organized, skipped, errors = organize_photos(
            str(self.source_dir), str(self.dest_dir)
        )
        
        self.assertEqual(organized, 2)
        self.assertEqual(skipped, 0)
        self.assertEqual(len(errors), 0)
        
        # Check destination structure
        self.assertTrue((self.dest_dir / "2024" / "01" / "photo1.png").exists())
        self.assertTrue((self.dest_dir / "2024" / "01" / "photo2.png").exists())
    
    def test_tc02_source_not_exists(self):
        """TC-02: Source folder does not exist"""
        with self.assertRaises(FileNotFoundError) as context:
            organize_photos("/nonexistent/path", str(self.dest_dir))
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_tc03_empty_source(self):
        """TC-03: Source folder is empty"""
        organized, skipped, errors = organize_photos(
            str(self.source_dir), str(self.dest_dir)
        )
        
        self.assertEqual(organized, 0)
        self.assertEqual(skipped, 0)
        self.assertEqual(len(errors), 0)
    
    def test_tc04_destination_created(self):
        """TC-04: Destination folder created if not exists"""
        new_dest = Path(self.temp_dir) / "new" / "nested" / "dest"
        self._create_test_photo(self.source_dir, "photo.png")
        
        self.assertFalse(new_dest.exists())
        
        organize_photos(str(self.source_dir), str(new_dest))
        
        self.assertTrue(new_dest.exists())
    
    def test_tc06_photos_organized_by_date(self):
        """TC-06: Photos organized by file date into YYYY/MM structure"""
        # Create photos with different dates
        self._create_test_photo(
            self.source_dir, "jan.png",
            datetime(2024, 1, 15)
        )
        self._create_test_photo(
            self.source_dir, "mar.png",
            datetime(2024, 3, 20)
        )
        self._create_test_photo(
            self.source_dir, "dec.png",
            datetime(2023, 12, 25)
        )
        
        organize_photos(str(self.source_dir), str(self.dest_dir))
        
        self.assertTrue((self.dest_dir / "2024" / "01" / "jan.png").exists())
        self.assertTrue((self.dest_dir / "2024" / "03" / "mar.png").exists())
        self.assertTrue((self.dest_dir / "2023" / "12" / "dec.png").exists())
    
    def test_tc07_nested_folders_scanned(self):
        """TC-07: Nested source folders scanned recursively"""
        self._create_test_photo(self.source_dir, "photo1.png")
        self._create_test_photo(self.source_dir / "subfolder", "photo2.png")
        self._create_test_photo(
            self.source_dir / "subfolder" / "deeper", "photo3.png"
        )
        
        organized, _, _ = organize_photos(
            str(self.source_dir), str(self.dest_dir)
        )
        
        self.assertEqual(organized, 3)
    
    def test_tc08_filename_collision_in_organize(self):
        """TC-08: Filename collision handled during organization"""
        # Create two photos with same name but in different source subfolders
        self._create_test_photo(
            self.source_dir / "folder1", "IMG_001.png",
            datetime(2024, 1, 15)
        )
        self._create_test_photo(
            self.source_dir / "folder2", "IMG_001.png",
            datetime(2024, 1, 20)
        )
        
        organize_photos(str(self.source_dir), str(self.dest_dir))
        
        # Both should exist in 2024/01
        jan_folder = self.dest_dir / "2024" / "01"
        self.assertTrue((jan_folder / "IMG_001.png").exists())
        self.assertTrue((jan_folder / "IMG_001_2.png").exists())
    
    def test_tc11_non_image_files_skipped(self):
        """TC-11: Non-image files skipped with warning"""
        self._create_test_photo(self.source_dir, "photo.png")
        
        # Create non-image files
        (self.source_dir / "document.pdf").write_text("PDF content")
        (self.source_dir / "readme.txt").write_text("README")
        
        organized, skipped, _ = organize_photos(
            str(self.source_dir), str(self.dest_dir)
        )
        
        self.assertEqual(organized, 1)
        self.assertEqual(skipped, 2)
    
    def test_tc12_all_supported_formats(self):
        """TC-12: All supported formats are processed"""
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # For non-PNG formats, just create empty files (will skip EXIF)
            photo_path = self.source_dir / f"test{ext}"
            if ext == '.png':
                self._create_test_photo(self.source_dir, f"test{ext}")
            else:
                photo_path.write_bytes(b'\x00' * 100)
        
        organized, skipped, errors = organize_photos(
            str(self.source_dir), str(self.dest_dir)
        )
        
        # PNG will succeed, others may error due to invalid format
        # but they should be attempted (not skipped as unsupported)
        self.assertEqual(skipped, 0)  # None should be skipped as unsupported


class TestCLI(unittest.TestCase):
    """Tests for CLI interface"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.dest_dir = Path(self.temp_dir) / "dest"
        self.source_dir.mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_tc02_cli_source_not_exists(self):
        """TC-02: CLI returns error for non-existent source"""
        with patch('sys.argv', ['photo_organizer.py', '/nonexistent', str(self.dest_dir)]):
            exit_code = main()
        
        self.assertEqual(exit_code, 1)
    
    def test_tc13_summary_displayed(self):
        """TC-13: Summary statistics displayed"""
        # Create a test photo
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        (self.source_dir / "photo.png").write_bytes(png_data)
        (self.source_dir / "doc.txt").write_text("text")
        
        with patch('sys.argv', ['photo_organizer.py', str(self.source_dir), str(self.dest_dir)]):
            exit_code = main()
        
        self.assertEqual(exit_code, 0)


class TestGetFileDate(unittest.TestCase):
    """Tests for file date extraction"""
    
    def test_returns_datetime(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            temp_path = Path(f.name)
        
        try:
            result = get_file_date(temp_path)
            self.assertIsInstance(result, datetime)
        finally:
            temp_path.unlink()


if __name__ == '__main__':
    unittest.main()
