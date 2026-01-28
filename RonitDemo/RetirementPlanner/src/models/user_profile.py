"""
Data models for the Retirement Planner application.
"""
from dataclasses import dataclass


@dataclass
class UserProfile:
    """
    User's financial profile for retirement planning.
    
    Attributes:
        current_age: User's current age (18-100)
        retirement_age: Target retirement age (>= current_age, <= 100)
        current_savings: Current total savings/investments (>= 0)
        monthly_contribution: Monthly contribution amount (>= 0)
        desired_monthly_income: Desired monthly income in retirement (> 0)
    """
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    desired_monthly_income: float
    
    def __post_init__(self):
        """Validate all fields after initialization."""
        # Age validation
        if self.current_age < 18:
            raise ValueError(f"Current age must be at least 18, got {self.current_age}")
        if self.current_age > 100:
            raise ValueError(f"Current age must be at most 100, got {self.current_age}")
        
        # Retirement age validation (allow equal for "already retired" edge case)
        if self.retirement_age < self.current_age:
            raise ValueError(
                f"Retirement age ({self.retirement_age}) must be >= current age ({self.current_age})"
            )
        if self.retirement_age > 100:
            raise ValueError(f"Retirement age must be at most 100, got {self.retirement_age}")
        
        # Financial validation
        if self.current_savings < 0:
            raise ValueError(f"Current savings cannot be negative, got {self.current_savings}")
        if self.monthly_contribution < 0:
            raise ValueError(f"Monthly contribution cannot be negative, got {self.monthly_contribution}")
        if self.desired_monthly_income <= 0:
            raise ValueError(f"Desired monthly income must be positive, got {self.desired_monthly_income}")


@dataclass
class ProjectionResult:
    """
    Results of a retirement projection calculation.
    
    Attributes:
        years_to_retirement: Years remaining until retirement
        projected_savings: Estimated savings at retirement
        required_nest_egg: Amount needed to support desired income (using 4% rule)
        monthly_income_possible: Monthly income supported by projected savings
        is_on_track: Whether projected savings meets or exceeds required nest egg
        surplus_or_gap: Positive = surplus, Negative = gap
    """
    years_to_retirement: int
    projected_savings: float
    required_nest_egg: float
    monthly_income_possible: float
    is_on_track: bool
    surplus_or_gap: float
