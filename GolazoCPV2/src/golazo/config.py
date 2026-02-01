"""
GCP2-008: Configuration System

Provides per-repo configuration for Golazo V2 workflow.
"""

import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


logger = logging.getLogger(__name__)


# Default values matching current hardcoded constants
DEFAULT_ROLES = [
    "project-owner",
    "program-manager",
    "tester",
    "architect",
    "developer",
    "refactor-expert",
    "builder",
    "documentor",
]

DEFAULT_TRANSITIONS = {
    "project-owner": ["program-manager"],
    "program-manager": ["tester"],
    "tester": ["architect"],
    "architect": ["developer"],
    "developer": ["refactor-expert"],
    "refactor-expert": ["builder"],
    "builder": ["documentor"],
    "documentor": [],
}

DEFAULT_ROLE_TO_PHASE = {
    "project-owner": "design",
    "program-manager": "design",
    "tester": "design",
    "architect": "design",
    "developer": "development",
    "refactor-expert": "development",
    "builder": "development",
    "documentor": "development",
}

DEFAULT_DOR_ITEMS = ["userStory", "designDoc", "reviewComments", "testCases"]

DEFAULT_DOD_ITEMS = [
    "branchCreated",
    "testsWrittenFirst",
    "testsPass",
    "buildPasses",
    "docsUpdated",
    "refactorComplete",
    "committed",
]

DEFAULT_QUALITY_GATES = ["tester", "architect"]

SUPPORTED_VERSIONS = {"1.0"}

KNOWN_KEYS = {
    "version", "roles", "transitions", "dor", "dod",
    "quality_gates", "phases", "role_to_phase"
}


@dataclass(frozen=True)
class GolazoConfig:
    """
    Immutable configuration for Golazo V2 workflow.
    
    Loaded from golazo.yaml or .golazo/config.yaml, with sensible defaults.
    """
    version: str
    roles: tuple
    transitions: dict  # Can't be frozen, but we don't expose setters
    dor_items: tuple
    dod_items: tuple
    quality_gates: tuple
    role_to_phase: dict
    
    @classmethod
    def load(cls, base_path: Optional[Path] = None) -> "GolazoConfig":
        """
        Load configuration from file or use defaults.
        
        Args:
            base_path: Base path to search for config files
            
        Returns:
            GolazoConfig instance
            
        Raises:
            ValueError: If config version is unsupported
            TypeError: If config values have invalid types
            yaml.YAMLError: If YAML is malformed
        """
        base_path = Path(base_path) if base_path else Path.cwd()
        
        # Find config file
        config_file = cls._find_config_file(base_path)
        
        if config_file:
            data = cls._load_yaml(config_file)
        else:
            data = {}
        
        # Apply defaults and validate
        data = cls._apply_defaults(data)
        cls._validate(data)
        cls._check_version(data)
        cls._warn_unknown_keys(data)
        
        return cls(
            version=data["version"],
            roles=tuple(data["roles"]),
            transitions={k: tuple(v) for k, v in data["transitions"].items()},
            dor_items=tuple(data["dor"]["items"]),
            dod_items=tuple(data["dod"]["items"]),
            quality_gates=tuple(data["quality_gates"]),
            role_to_phase=dict(data["role_to_phase"]),
        )
    
    @staticmethod
    def _find_config_file(base_path: Path) -> Optional[Path]:
        """Find config file in priority order."""
        candidates = [
            base_path / "golazo.yaml",
            base_path / ".golazo" / "config.yaml",
        ]
        for path in candidates:
            if path.exists():
                return path
        return None
    
    @staticmethod
    def _load_yaml(path: Path) -> dict:
        """Load YAML file, returning empty dict for empty files."""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return {}
        return yaml.safe_load(content) or {}
    
    @staticmethod
    def _apply_defaults(data: dict) -> dict:
        """Apply default values for missing keys."""
        result = {
            "version": data.get("version", "1.0"),
            "roles": data.get("roles", DEFAULT_ROLES.copy()),
            "transitions": data.get("transitions", DEFAULT_TRANSITIONS.copy()),
            "dor": data.get("dor", {"items": DEFAULT_DOR_ITEMS.copy()}),
            "dod": data.get("dod", {"items": DEFAULT_DOD_ITEMS.copy()}),
            "quality_gates": data.get("quality_gates", DEFAULT_QUALITY_GATES.copy()),
            "role_to_phase": data.get("role_to_phase", DEFAULT_ROLE_TO_PHASE.copy()),
        }
        
        # Ensure nested defaults
        if "items" not in result["dor"]:
            result["dor"]["items"] = DEFAULT_DOR_ITEMS.copy()
        if "items" not in result["dod"]:
            result["dod"]["items"] = DEFAULT_DOD_ITEMS.copy()
        
        return result
    
    @staticmethod
    def _validate(data: dict) -> None:
        """Validate configuration types."""
        if not isinstance(data.get("roles"), list):
            raise TypeError("Config 'roles' must be a list")
        if not isinstance(data.get("transitions"), dict):
            raise TypeError("Config 'transitions' must be a dict")
        if not isinstance(data.get("quality_gates"), list):
            raise TypeError("Config 'quality_gates' must be a list")
    
    @staticmethod
    def _check_version(data: dict) -> None:
        """Check config version is supported."""
        version = data.get("version", "1.0")
        if version not in SUPPORTED_VERSIONS:
            raise ValueError(f"Unknown config version: {version}. Supported: {SUPPORTED_VERSIONS}")
    
    @staticmethod
    def _warn_unknown_keys(data: dict) -> None:
        """Warn about unknown configuration keys."""
        unknown = set(data.keys()) - KNOWN_KEYS
        for key in unknown:
            warnings.warn(f"Unknown configuration key: {key}", UserWarning)
            logger.warning(f"Unknown configuration key: {key}")
