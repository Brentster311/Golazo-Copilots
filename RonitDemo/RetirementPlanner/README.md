# Retirement Planner

MVP retirement planning application for Windows.

## Requirements
- Python 3.8+
- No external dependencies for runtime (standard library only)
- pytest for testing (dev dependency)

## Quick Start
```bash
# Run the application
python RetirementPlanner/src/main.py

# Run tests
pytest RetirementPlanner/tests/ -v
```

## Project Structure
```
RetirementPlanner/
??? src/
?   ??? main.py
?   ??? models/
?   ?   ??? user_profile.py
?   ??? repository/
?   ?   ??? base_repository.py
?   ?   ??? json_file_repository.py
?   ??? services/
?   ?   ??? retirement_calculator.py
?   ??? ui/
?       ??? main_window.py
??? tests/
?   ??? test_retirement_calculator.py
?   ??? test_json_file_repository.py
??? data/
?   ??? (user_profile.json created at runtime)
??? WorkItems/
    ??? (Golazo artifacts)
```

## Features (RETIRE-001 MVP)
- Enter current age and retirement age
- Enter current savings and monthly contribution
- Enter desired monthly retirement income
- Calculate projected retirement savings
- Display on-track status with surplus/gap
- Persist data to local JSON file
