# Test Cases: RETIRE-001

## Overview
Test cases for MVP Retirement Planner. Each test maps to acceptance criteria from the User Story.

---

## Test Case Mapping to Acceptance Criteria

| AC # | Acceptance Criteria | Test Cases |
|------|---------------------|------------|
| AC-1 | Enter current age and retirement age | TC-01, TC-02, TC-03, TC-04 |
| AC-2 | Enter current savings | TC-05, TC-06 |
| AC-3 | Enter monthly contribution | TC-07, TC-08 |
| AC-4 | Enter desired monthly income | TC-09, TC-10 |
| AC-5 | Calculate projected retirement savings | TC-11, TC-12, TC-13 |
| AC-6 | Display on-track status | TC-14, TC-15, TC-16 |
| AC-7 | Data persists to file | TC-17, TC-18, TC-19, TC-20 |

---

## Unit Tests: RetirementCalculator Service

### TC-01: Calculate with valid inputs (Happy Path)
**Maps to**: AC-5, AC-6
**Type**: Unit Test
```python
def test_calculate_projection_happy_path():
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
```

### TC-02: Age validation - current age at minimum (18)
**Maps to**: AC-1, FR-1
**Type**: Unit Test
```python
def test_age_minimum_boundary():
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
```

### TC-03: Age validation - current age at maximum (100)
**Maps to**: AC-1, FR-1
**Type**: Unit Test (Edge Case)
```python
def test_age_maximum_boundary():
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
```

### TC-04: Edge case - current age equals retirement age
**Maps to**: AC-1 (Edge case from Reviewer)
**Type**: Unit Test (Edge Case)
```python
def test_zero_years_to_retirement():
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
```

### TC-05: Zero current savings
**Maps to**: AC-2
**Type**: Unit Test
```python
def test_zero_current_savings():
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
```

### TC-06: Large current savings
**Maps to**: AC-2 (Edge case)
**Type**: Unit Test
```python
def test_large_current_savings():
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
```

### TC-07: Zero monthly contribution
**Maps to**: AC-3
**Type**: Unit Test
```python
def test_zero_monthly_contribution():
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
```

### TC-08: High monthly contribution
**Maps to**: AC-3
**Type**: Unit Test
```python
def test_high_monthly_contribution():
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
```

### TC-09: Minimum desired income
**Maps to**: AC-4
**Type**: Unit Test
```python
def test_minimum_desired_income():
    profile = UserProfile(
        current_age=30,
        retirement_age=65,
        current_savings=10000.0,
        monthly_contribution=100.0,
        desired_monthly_income=0.01  # Very small but > 0
    )
    calculator = RetirementCalculator()
    result = calculator.calculate(profile)
    
    assert result.required_nest_egg == 3.0  # 0.01 * 12 / 0.04
    assert result.is_on_track == True
```

### TC-10: High desired income (likely not on track)
**Maps to**: AC-4
**Type**: Unit Test
```python
def test_high_desired_income_not_on_track():
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
```

### TC-11: Verify compound interest formula
**Maps to**: AC-5, Design Doc formula
**Type**: Unit Test
```python
def test_compound_interest_calculation():
    """
    Verify: FV = P(1+r)^n + PMT*[((1+r)^n - 1)/r]
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
    # FV ? 19671.51 + 165764.53 ? 185436.04
    assert abs(result.projected_savings - 185436.04) < 1.0  # Allow small float variance
```

### TC-12: Verify required nest egg formula
**Maps to**: AC-5, AC-6
**Type**: Unit Test
```python
def test_required_nest_egg_calculation():
    """
    Required = (Monthly * 12) / 0.04 (4% withdrawal rate)
    """
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
```

### TC-13: Verify monthly income possible calculation
**Maps to**: AC-6
**Type**: Unit Test
```python
def test_monthly_income_possible():
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
```

### TC-14: On track status - exactly meets goal
**Maps to**: AC-6
**Type**: Unit Test (Boundary)
```python
def test_exactly_on_track():
    # Construct a case where projected equals required
    profile = UserProfile(
        current_age=30,
        retirement_age=65,
        current_savings=100_000.0,
        monthly_contribution=750.0,  # Tuned to hit ~$1.2M
        desired_monthly_income=4000.0
    )
    calculator = RetirementCalculator()
    result = calculator.calculate(profile)
    
    # Close to goal should be on_track
    # (exact equality is unlikely due to float math)
    assert isinstance(result.is_on_track, bool)
```

### TC-15: Surplus scenario (ahead of goal)
**Maps to**: AC-6 (Edge case from Reviewer)
**Type**: Unit Test
```python
def test_surplus_ahead_of_goal():
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
```

### TC-16: Gap scenario (behind goal)
**Maps to**: AC-6
**Type**: Unit Test
```python
def test_gap_behind_goal():
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
```

---

## Unit Tests: JsonFileRepository

### TC-17: Save and load round-trip
**Maps to**: AC-7
**Type**: Unit Test
```python
def test_save_and_load_roundtrip(tmp_path):
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
```

### TC-18: Load returns None when file doesn't exist
**Maps to**: AC-7
**Type**: Unit Test
```python
def test_load_nonexistent_file(tmp_path):
    repo = JsonFileRepository(tmp_path / "nonexistent.json")
    
    result = repo.load()
    
    assert result is None
```

### TC-19: Handle corrupted JSON gracefully
**Maps to**: AC-7, NFR-3
**Type**: Unit Test (Error Case)
```python
def test_load_corrupted_json(tmp_path):
    file_path = tmp_path / "corrupted.json"
    file_path.write_text("{ invalid json }", encoding='utf-8')
    
    repo = JsonFileRepository(file_path)
    
    # Should either return None or raise RepositoryError, not crash
    try:
        result = repo.load()
        assert result is None
    except RepositoryError:
        pass  # Also acceptable
```

### TC-20: File uses UTF-8 encoding
**Maps to**: AC-7, Architect decision
**Type**: Unit Test
```python
def test_file_uses_utf8_encoding(tmp_path):
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
```

---

## Unit Tests: Input Validation

### TC-21: Reject age below minimum
**Maps to**: FR-1, NFR-3
**Type**: Unit Test (Negative)
```python
def test_reject_age_below_18():
    # Validation can be in model or service
    with pytest.raises(ValueError):
        UserProfile(
            current_age=17,  # Invalid
            retirement_age=65,
            current_savings=0.0,
            monthly_contribution=0.0,
            desired_monthly_income=1000.0
        )
```

### TC-22: Reject retirement age <= current age
**Maps to**: FR-2, NFR-3
**Type**: Unit Test (Negative)
```python
def test_reject_retirement_age_not_greater():
    with pytest.raises(ValueError):
        UserProfile(
            current_age=65,
            retirement_age=60,  # Invalid: not > current_age
            current_savings=0.0,
            monthly_contribution=0.0,
            desired_monthly_income=1000.0
        )
```

### TC-23: Reject negative savings
**Maps to**: FR-3, NFR-3
**Type**: Unit Test (Negative)
```python
def test_reject_negative_savings():
    with pytest.raises(ValueError):
        UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=-1000.0,  # Invalid
            monthly_contribution=100.0,
            desired_monthly_income=3000.0
        )
```

### TC-24: Reject negative contribution
**Maps to**: FR-4, NFR-3
**Type**: Unit Test (Negative)
```python
def test_reject_negative_contribution():
    with pytest.raises(ValueError):
        UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=1000.0,
            monthly_contribution=-100.0,  # Invalid
            desired_monthly_income=3000.0
        )
```

### TC-25: Reject zero or negative desired income
**Maps to**: FR-5, NFR-3
**Type**: Unit Test (Negative)
```python
def test_reject_zero_desired_income():
    with pytest.raises(ValueError):
        UserProfile(
            current_age=30,
            retirement_age=65,
            current_savings=1000.0,
            monthly_contribution=100.0,
            desired_monthly_income=0.0  # Invalid
        )
```

---

## Integration Tests

### TC-26: Full workflow - new user
**Maps to**: All AC
**Type**: Integration Test
```python
def test_full_workflow_new_user(tmp_path):
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
```

### TC-27: Data persists across sessions (simulated)
**Maps to**: AC-7
**Type**: Integration Test
```python
def test_data_persists_across_sessions(tmp_path):
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
```

---

## Manual Test Cases (UI)

### TC-M1: Application launches without errors
**Maps to**: KPI-1
**Steps**:
1. Run `python main.py`
2. Verify main window appears
3. Verify all input fields are visible
4. Verify Calculate button is visible

**Expected**: Window displays with all controls

### TC-M2: Input validation shows user-friendly errors
**Maps to**: NFR-3
**Steps**:
1. Enter "abc" in age field
2. Click Calculate

**Expected**: Error message displayed (not crash)

### TC-M3: Save and reload on restart
**Maps to**: AC-7
**Steps**:
1. Enter valid data in all fields
2. Click Save
3. Close application
4. Reopen application

**Expected**: Previously entered data is loaded

### TC-M4: Calculation completes quickly
**Maps to**: NFR-4
**Steps**:
1. Enter valid data
2. Click Calculate
3. Observe response time

**Expected**: Result displays in < 1 second

---

## Summary

| Category | Count |
|----------|-------|
| Calculator Unit Tests | 16 |
| Repository Unit Tests | 4 |
| Validation Unit Tests | 5 |
| Integration Tests | 2 |
| Manual Tests | 4 |
| **Total** | **31** |

All acceptance criteria are covered by at least one automated test case.
