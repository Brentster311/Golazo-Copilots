"""
Test cases for JsonFileRepository.
Based on RETIRE-001-Test-Cases.md
"""
import pytest
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import UserProfile
from repository import JsonFileRepository, RepositoryError


class TestJsonFileRepositoryRoundTrip:
    """TC-17: Save and load round-trip"""
    
    def test_save_and_load_roundtrip(self, tmp_path):
        repo = JsonFileRepository(tmp_path / "test_profile.json")
        profile = UserProfile(
            current_age=35,
            retirement_age=60,
            current_savings=75000.0,
            monthly_contribution=1200.0,
            desired_monthly_income=5000.0
        )
        
        repo.save(profile)
        loaded = repo.load()
        
        assert loaded == profile


class TestJsonFileRepositoryLoad:
    """TC-18, TC-19: Load scenarios"""
    
    def test_load_nonexistent_file(self, tmp_path):
        """TC-18: Load returns None when file doesn't exist"""
        repo = JsonFileRepository(tmp_path / "nonexistent.json")
        
        result = repo.load()
        
        assert result is None
    
    def test_load_corrupted_json(self, tmp_path):
        """TC-19: Handle corrupted JSON gracefully"""
        file_path = tmp_path / "corrupted.json"
        file_path.write_text("{ invalid json }", encoding='utf-8')
        
        repo = JsonFileRepository(file_path)
        
        # Should either return None or raise RepositoryError, not crash
        try:
            result = repo.load()
            assert result is None
        except RepositoryError:
            pass  # Also acceptable


class TestJsonFileRepositoryEncoding:
    """TC-20: UTF-8 encoding"""
    
    def test_file_uses_utf8_encoding(self, tmp_path):
        file_path = tmp_path / "profile.json"
        repo = JsonFileRepository(file_path)
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=1000.0,
            monthly_contribution=100.0,
            desired_monthly_income=3000.0
        )
        
        repo.save(profile)
        
        # Verify file is UTF-8
        content = file_path.read_text(encoding='utf-8')
        assert 'current_age' in content


class TestIntegration:
    """TC-26, TC-27: Integration tests"""
    
    def test_full_workflow_new_user(self, tmp_path):
        """TC-26: Full workflow - new user"""
        from services import RetirementCalculator
        
        # Setup
        repo = JsonFileRepository(tmp_path / "profile.json")
        calculator = RetirementCalculator()
        
        # Initially no data
        assert repo.load() is None
        
        # User enters data
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=50000.0,
            monthly_contribution=500.0,
            desired_monthly_income=4000.0
        )
        
        # Save
        repo.save(profile)
        
        # Calculate
        result = calculator.calculate(profile)
        
        # Verify
        assert result.years_to_retirement == 35
        assert result.required_nest_egg == 1_200_000.0
        assert isinstance(result.is_on_track, bool)
        
        # Reload
        loaded = repo.load()
        assert loaded == profile
    
    def test_data_persists_across_sessions(self, tmp_path):
        """TC-27: Data persists across sessions (simulated)"""
        file_path = tmp_path / "profile.json"
        
        # Session 1: Create and save
        repo1 = JsonFileRepository(file_path)
        profile = UserProfile(
            current_age=40,
            retirement_age=65,
            current_savings=100000.0,
            monthly_contribution=1000.0,
            desired_monthly_income=5000.0
        )
        repo1.save(profile)
        
        # Session 2: New instance loads existing data
        repo2 = JsonFileRepository(file_path)
        loaded = repo2.load()
        
        assert loaded == profile
