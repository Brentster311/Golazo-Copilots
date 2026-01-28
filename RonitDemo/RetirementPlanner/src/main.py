"""
Retirement Planner Application

MVP retirement planning tool that helps users understand
their retirement savings trajectory.

Usage:
    python main.py
"""
import sys
from pathlib import Path

# Add src to path for imports when running as script
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from models import UserProfile, ProjectionResult
from repository import JsonFileRepository
from services import RetirementCalculator
from ui import MainWindow


def get_data_path() -> Path:
    """
    Get the path for user data storage.
    
    Uses a 'data' subdirectory relative to the application.
    """
    app_dir = Path(__file__).parent.parent
    data_dir = app_dir / "data"
    return data_dir / "user_profile.json"


def main():
    """Application entry point."""
    # Initialize components with dependency injection
    data_path = get_data_path()
    repository = JsonFileRepository(data_path)
    calculator = RetirementCalculator()
    
    # Create and run the main window
    app = MainWindow(
        repository=repository,
        calculator=calculator
    )
    
    print(f"Retirement Planner started. Data stored at: {data_path}")
    app.run()


if __name__ == "__main__":
    main()
