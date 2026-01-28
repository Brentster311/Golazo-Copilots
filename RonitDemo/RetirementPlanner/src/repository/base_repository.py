"""
Abstract base class for data repository.
Provides abstraction layer for data persistence.
"""
from abc import ABC, abstractmethod
from typing import Optional

from models.user_profile import UserProfile


class RepositoryError(Exception):
    """Exception raised when repository operations fail."""
    pass


class IDataRepository(ABC):
    """
    Abstract interface for user profile data storage.
    
    Implementations can use different storage backends
    (JSON file, database, cloud, etc.) while maintaining
    the same interface.
    """
    
    @abstractmethod
    def save(self, profile: UserProfile) -> None:
        """
        Save user profile to storage.
        
        Args:
            profile: The user profile to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    def load(self) -> Optional[UserProfile]:
        """
        Load user profile from storage.
        
        Returns:
            UserProfile if found, None if not found
            
        Raises:
            RepositoryError: If load operation fails due to corruption
        """
        pass
