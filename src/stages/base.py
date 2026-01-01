"""BaseStage interface for all pipeline stages"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path


class BaseStage(ABC):
    """Abstract base class for all pipeline stages
    
    All stages must implement this interface to ensure consistent
    behavior across CLI and API execution.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize stage with optional project root path
        
        Args:
            project_root: Root path for project workspace
        """
        self.project_root = project_root

    @abstractmethod
    def run(self, project_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute stage logic
        
        Args:
            project_id: Project identifier (e.g., IMDb ID)
            config: Optional stage-specific configuration
            
        Returns:
            Dictionary containing stage output data
            
        Raises:
            StageExecutionError: If stage execution fails
        """
        pass

    @abstractmethod
    def load_input(self, project_id: str) -> Dict[str, Any]:
        """Load input from previous stage or project files
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dictionary containing input data
            
        Raises:
            FileNotFoundError: If required input files are missing
        """
        pass

    @abstractmethod
    def save_output(self, project_id: str, data: Dict[str, Any]) -> Path:
        """Save stage output to project workspace
        
        Args:
            project_id: Project identifier
            data: Output data to save
            
        Returns:
            Path to saved output file
        """
        pass

    @abstractmethod
    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate stage configuration
        
        Args:
            config: Stage configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass

    def get_project_path(self, project_id: str) -> Path:
        """Get project workspace path
        
        Args:
            project_id: Project identifier
            
        Returns:
            Path to project workspace
        """
        if self.project_root:
            return self.project_root / "projects" / project_id
        return Path("projects") / project_id

    def get_data_path(self, project_id: str) -> Path:
        """Get project data directory path"""
        return self.get_project_path(project_id) / "data"

    def get_outputs_path(self, project_id: str) -> Path:
        """Get project outputs directory path"""
        return self.get_project_path(project_id) / "outputs"

    def get_configs_path(self, project_id: str) -> Path:
        """Get project configs directory path"""
        return self.get_project_path(project_id) / "configs"

    def get_logs_path(self, project_id: str) -> Path:
        """Get project logs directory path"""
        return self.get_project_path(project_id) / "logs"

    def ensure_project_structure(self, project_id: str) -> None:
        """Ensure project workspace structure exists"""
        paths = [
            self.get_data_path(project_id),
            self.get_outputs_path(project_id),
            self.get_configs_path(project_id),
            self.get_logs_path(project_id),
            self.get_project_path(project_id) / "index" / "chroma"
        ]
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)


class StageExecutionError(Exception):
    """Exception raised when stage execution fails"""
    pass

