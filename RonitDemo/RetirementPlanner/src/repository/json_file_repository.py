"""
JSON file-based implementation of IDataRepository.
"""
import json
from pathlib import Path
from typing import Optional

from models.user_profile import UserProfile
from repository.base_repository import IDataRepository, RepositoryError


class JsonFileRepository(IDataRepository):
    """
    Repository implementation using JSON file storage.
    
    Stores user profile as a JSON file with explicit UTF-8 encoding.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize repository with file path.
        
        Args:
            file_path: Path to the JSON file for storage
        """
        self._file_path = Path(file_path)
    
    def save(self, profile: UserProfile) -> None:
        """
        Save user profile to JSON file.
        
        Creates parent directories if they don't exist.
        Uses explicit UTF-8 encoding for cross-platform safety.
        
        Args:
            profile: The user profile to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        try:
            # Ensure parent directory exists
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert dataclass to dict
            data = {
                'current_age': profile.current_age,
                'retirement_age': profile.retirement_age,
                'current_savings': profile.current_savings,
                'monthly_contribution': profile.monthly_contribution,
                'desired_monthly_income': profile.desired_monthly_income
            }
            
            # Write with explicit UTF-8 encoding
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except (IOError, OSError) as e:
            raise RepositoryError(f"Failed to save profile: {e}") from e
    
    def load(self) -> Optional[UserProfile]:
        """
        Load user profile from JSON file.
        
        Returns:
            UserProfile if file exists and is valid, None if file doesn't exist
            
        Raises:
            RepositoryError: If file exists but contains invalid JSON
        """
        if not self._file_path.exists():
            return None
        
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return UserProfile(
                current_age=data['current_age'],
                retirement_age=data['retirement_age'],
                current_savings=data['current_savings'],
                monthly_contribution=data['monthly_contribution'],
                desired_monthly_income=data['desired_monthly_income']
            )
            
        except json.JSONDecodeError as e:
            # Return None for corrupted files (graceful handling)
            return None
        except (KeyError, TypeError) as e:
            # Missing or invalid fields
            return None
        except (IOError, OSError) as e:
            raise RepositoryError(f"Failed to load profile: {e}") from e
