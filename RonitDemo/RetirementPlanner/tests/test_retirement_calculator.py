"""
Test cases for RetirementCalculator service.
Based on RETIRE-001-Test-Cases.md
"""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import UserProfile, ProjectionResult
from services import RetirementCalculator


class TestRetirementCalculatorHappyPath:
    """TC-01: Calculate with valid inputs"""
    
    def test_calculate_projection_happy_path(self):
        # Given
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=50000.0,
            monthly_contribution=500.0,
            desired_monthly_income=4000.0
        )
        calculator = RetirementCalculator()
        
        # When
        result = calculator.calculate(profile)
        
        # Then
        assert result.years_to_retirement == 35
        assert result.projected_savings > 0
        assert result.required_nest_egg == 1_200_000.0  # 4000 * 12 / 0.04
        assert isinstance(result.is_on_track, bool)


class TestAgeValidation:
    """TC-02, TC-03, TC-04: Age boundary tests"""
    
    def test_age_minimum_boundary(self):
        """TC-02: Age at minimum (18)"""
        profile = UserProfile(
            current_age=18,
            retirement_age=65,
            current_savings=0.0,
            monthly_contribution=100.0,
            desired_monthly_income=3000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.years_to_retirement == 47
    
    def test_age_maximum_boundary(self):
        """TC-03: Age at maximum (100)"""
        profile = UserProfile(
            current_age=99,
            retirement_age=100,
            current_savings=1_000_000.0,
            monthly_contribution=0.0,
            desired_monthly_income=3000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.years_to_retirement == 1
    
    def test_zero_years_to_retirement(self):
        """TC-04: Edge case - current age equals retirement age"""
        profile = UserProfile(
            current_age=65,
            retirement_age=65,
            current_savings=1_000_000.0,
            monthly_contribution=0.0,
            desired_monthly_income=3000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.years_to_retirement == 0
        assert result.projected_savings == 1_000_000.0  # No growth time


class TestSavingsScenarios:
    """TC-05, TC-06: Savings tests"""
    
    def test_zero_current_savings(self):
        """TC-05: Zero current savings"""
        profile = UserProfile(
            current_age=25,
            retirement_age=65,
            current_savings=0.0,
            monthly_contribution=1000.0,
            desired_monthly_income=5000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.projected_savings > 0  # Contributions still grow
    
    def test_large_current_savings(self):
        """TC-06: Large current savings"""
        profile = UserProfile(
            current_age=50,
            retirement_age=65,
            current_savings=5_000_000.0,
            monthly_contribution=0.0,
            desired_monthly_income=10000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.is_on_track == True
        assert result.surplus_or_gap > 0


class TestContributionScenarios:
    """TC-07, TC-08: Contribution tests"""
    
    def test_zero_monthly_contribution(self):
        """TC-07: Zero monthly contribution"""
        profile = UserProfile(
            current_age=40,
            retirement_age=65,
            current_savings=100_000.0,
            monthly_contribution=0.0,
            desired_monthly_income=3000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        # Should still calculate based on savings growth only
        assert result.projected_savings > 100_000.0  # Savings grew
    
    def test_high_monthly_contribution(self):
        """TC-08: High monthly contribution"""
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=0.0,
            monthly_contribution=5000.0,
            desired_monthly_income=4000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.is_on_track == True


class TestDesiredIncomeScenarios:
    """TC-09, TC-10: Desired income tests"""
    
    def test_minimum_desired_income(self):
        """TC-09: Very small desired income"""
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=10000.0,
            monthly_contribution=100.0,
            desired_monthly_income=0.01
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.required_nest_egg == 3.0  # 0.01 * 12 / 0.04
        assert result.is_on_track == True
    
    def test_high_desired_income_not_on_track(self):
        """TC-10: High desired income (not on track)"""
        profile = UserProfile(
            current_age=50,
            retirement_age=65,
            current_savings=100_000.0,
            monthly_contribution=500.0,
            desired_monthly_income=20000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.is_on_track == False
        assert result.surplus_or_gap < 0  # Negative = gap


class TestCalculationFormulas:
    """TC-11, TC-12, TC-13: Formula verification"""
    
    def test_compound_interest_calculation(self):
        """TC-11: Verify compound interest formula
        FV = P(1+r)^n + PMT*[((1+r)^n - 1)/r]
        With P=10000, r=0.07, n=10, PMT=12000 (1000/mo * 12)
        """
        profile = UserProfile(
            current_age=55,
            retirement_age=65,
            current_savings=10000.0,
            monthly_contribution=1000.0,
            desired_monthly_income=2000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        # Manual calculation:
        # FV = 10000 * (1.07)^10 + 12000 * [((1.07)^10 - 1) / 0.07]
        # FV = 19671.51 + 165797.38 = 185468.89 (more precise calculation)
        assert abs(result.projected_savings - 185468.89) < 1.0
    
    def test_required_nest_egg_calculation(self):
        """TC-12: Required = (Monthly * 12) / 0.04"""
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=0.0,
            monthly_contribution=0.0,
            desired_monthly_income=5000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        expected_nest_egg = (5000 * 12) / 0.04  # 1,500,000
        assert result.required_nest_egg == expected_nest_egg
    
    def test_monthly_income_possible(self):
        """TC-13: Verify monthly income possible calculation"""
        profile = UserProfile(
            current_age=55,
            retirement_age=65,
            current_savings=500_000.0,
            monthly_contribution=2000.0,
            desired_monthly_income=4000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        # monthly_income_possible = (projected_savings * 0.04) / 12
        expected_monthly = (result.projected_savings * 0.04) / 12
        assert abs(result.monthly_income_possible - expected_monthly) < 0.01


class TestOnTrackStatus:
    """TC-14, TC-15, TC-16: On-track status tests"""
    
    def test_exactly_on_track(self):
        """TC-14: Close to goal boundary"""
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=100_000.0,
            monthly_contribution=750.0,
            desired_monthly_income=4000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert isinstance(result.is_on_track, bool)
    
    def test_surplus_ahead_of_goal(self):
        """TC-15: Surplus scenario (ahead of goal)"""
        profile = UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=200_000.0,
            monthly_contribution=2000.0,
            desired_monthly_income=3000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.is_on_track == True
        assert result.surplus_or_gap > 0  # Positive = surplus
    
    def test_gap_behind_goal(self):
        """TC-16: Gap scenario (behind goal)"""
        profile = UserProfile(
            current_age=55,
            retirement_age=65,
            current_savings=50_000.0,
            monthly_contribution=200.0,
            desired_monthly_income=8000.0
        )
        calculator = RetirementCalculator()
        result = calculator.calculate(profile)
        
        assert result.is_on_track == False
        assert result.surplus_or_gap < 0  # Negative = gap
