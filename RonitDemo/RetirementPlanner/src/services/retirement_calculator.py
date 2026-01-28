"""
Retirement calculation service.
"""
from models.user_profile import UserProfile, ProjectionResult


class RetirementCalculator:
    """
    Service for calculating retirement projections.
    
    Uses compound interest formula for projections and
    4% safe withdrawal rate for income calculations.
    """
    
    # Default assumptions (hard-coded for MVP)
    ANNUAL_RETURN_RATE = 0.07  # 7% average return
    SAFE_WITHDRAWAL_RATE = 0.04  # 4% rule
    
    def calculate(self, profile: UserProfile) -> ProjectionResult:
        """
        Calculate retirement projection based on user profile.
        
        Formula:
        Future Value = P * (1 + r)^n + PMT * [((1 + r)^n - 1) / r]
        
        Where:
        - P = Current savings (principal)
        - r = Annual return rate (7%)
        - n = Years until retirement
        - PMT = Annual contribution (monthly * 12)
        
        Args:
            profile: User's financial profile
            
        Returns:
            ProjectionResult with all calculated values
        """
        years_to_retirement = profile.retirement_age - profile.current_age
        
        # Calculate projected savings at retirement
        projected_savings = self._calculate_future_value(
            principal=profile.current_savings,
            annual_contribution=profile.monthly_contribution * 12,
            years=years_to_retirement,
            rate=self.ANNUAL_RETURN_RATE
        )
        
        # Calculate required nest egg using 4% rule
        # Required = (Annual Income) / Withdrawal Rate
        annual_income_needed = profile.desired_monthly_income * 12
        required_nest_egg = annual_income_needed / self.SAFE_WITHDRAWAL_RATE
        
        # Calculate what monthly income the projected savings could support
        monthly_income_possible = (projected_savings * self.SAFE_WITHDRAWAL_RATE) / 12
        
        # Determine if on track
        is_on_track = projected_savings >= required_nest_egg
        surplus_or_gap = projected_savings - required_nest_egg
        
        return ProjectionResult(
            years_to_retirement=years_to_retirement,
            projected_savings=projected_savings,
            required_nest_egg=required_nest_egg,
            monthly_income_possible=monthly_income_possible,
            is_on_track=is_on_track,
            surplus_or_gap=surplus_or_gap
        )
    
    def _calculate_future_value(
        self,
        principal: float,
        annual_contribution: float,
        years: int,
        rate: float
    ) -> float:
        """
        Calculate future value using compound interest formula.
        
        FV = P(1+r)^n + PMT * [((1+r)^n - 1) / r]
        
        Handles edge case where years = 0 (already at retirement).
        """
        if years == 0:
            return principal
        
        if rate == 0:
            # No growth, just sum of principal and contributions
            return principal + (annual_contribution * years)
        
        # Growth factor: (1 + r)^n
        growth_factor = (1 + rate) ** years
        
        # Future value of principal
        fv_principal = principal * growth_factor
        
        # Future value of annuity (contributions)
        # PMT * [((1+r)^n - 1) / r]
        fv_contributions = annual_contribution * ((growth_factor - 1) / rate)
        
        return fv_principal + fv_contributions
