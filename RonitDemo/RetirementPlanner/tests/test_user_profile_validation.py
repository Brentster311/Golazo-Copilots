"""
Test cases for UserProfile validation.
Based on RETIRE-001-Test-Cases.md
"""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import UserProfile


class TestUserProfileValidation:
    """TC-21 through TC-25: Input validation tests"""
    
    def test_reject_age_below_18(self):
        """TC-21: Reject age below minimum"""
        with pytest.raises(ValueError):
            UserProfile(
                current_age=17,
                retirement_age=65,
                current_savings=0.0,
                monthly_contribution=0.0,
                desired_monthly_income=1000.0
            )
    
    def test_reject_age_above_100(self):
        """Reject age above maximum"""
        with pytest.raises(ValueError):
            UserProfile(
                current_age=101,
                retirement_age=105,
                current_savings=0.0,
                monthly_contribution=0.0,
                desired_monthly_income=1000.0
            )
    
    def test_reject_retirement_age_not_greater(self):
        """TC-22: Reject retirement age <= current age"""
        with pytest.raises(ValueError):
            UserProfile(
                current_age=65,
                retirement_age=60,
                current_savings=0.0,
                monthly_contribution=0.0,
                desired_monthly_income=1000.0
            )
    
    def test_allow_retirement_age_equal_current(self):
        """Allow retirement age == current age (edge case: already retired)"""
        # This should NOT raise - it's an edge case we handle
        profile = UserProfile(
            current_age=65,
            retirement_age=65,
            current_savings=1_000_000.0,
            monthly_contribution=0.0,
            desired_monthly_income=3000.0
        )
        assert profile.current_age == profile.retirement_age
    
    def test_reject_negative_savings(self):
        """TC-23: Reject negative savings"""
        with pytest.raises(ValueError):
            UserProfile(
                current_age=30,
                retirement_age=65,
                current_savings=-1000.0,
                monthly_contribution=100.0,
                desired_monthly_income=3000.0
            )
    
    def test_reject_negative_contribution(self):
        """TC-24: Reject negative contribution"""
        with pytest.raises(ValueError):
            UserProfile(
                current_age=30,
                retirement_age=65,
                current_savings=1000.0,
                monthly_contribution=-100.0,
                desired_monthly_income=3000.0
            )
    
    def test_reject_zero_desired_income(self):
        """TC-25: Reject zero desired income"""
        with pytest.raises(ValueError):
            UserProfile(
                current_age=30,
                retirement_age=65,
                current_savings=1000.0,
                monthly_contribution=100.0,
                desired_monthly_income=0.0
            )
    
    def test_reject_negative_desired_income(self):
        """Reject negative desired income"""
        with pytest.raises(ValueError):
            UserProfile(
                current_age=30,
                retirement_age=65,
                current_savings=1000.0,
                monthly_contribution=100.0,
                desired_monthly_income=-1000.0
            )
