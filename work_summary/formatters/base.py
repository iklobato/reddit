"""
Base formatter class for output formatting.

Provides common functionality for different output formats.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from work_summary.models import Task, WorkSummary


class BaseFormatter(ABC):
    """
    Base class for all formatters.
    
    Formatters convert WorkSummary data into various output formats.
    """
    
    def __init__(self, color_enabled: bool = True):
        """
        Initialize formatter.
        
        Args:
            color_enabled: Whether to use colors in output
        """
        self.color_enabled = color_enabled
    
    @abstractmethod
    def format(self, summary: WorkSummary) -> str:
        """
        Format work summary.
        
        Args:
            summary: Work summary to format
            
        Returns:
            Formatted output string
        """
        pass
    
    def format_tasks(self, tasks: List[Task]) -> str:
        """
        Format a list of tasks.
        
        Args:
            tasks: List of tasks to format
            
        Returns:
            Formatted output string
        """
        # Create a temporary WorkSummary
        summary = WorkSummary(tasks=tasks)
        return self.format(summary)
    
    @property
    def name(self) -> str:
        """Get formatter name."""
        return self.__class__.__name__.replace('Formatter', '')
