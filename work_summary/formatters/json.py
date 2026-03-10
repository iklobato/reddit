"""
JSON formatter for work summary.

Outputs work items in JSON format for machine processing.
"""

import json
from typing import Dict, Any

from work_summary.formatters.base import BaseFormatter
from work_summary.models import WorkSummary


class JSONFormatter(BaseFormatter):
    """Format work summary as JSON."""
    
    def __init__(self, pretty: bool = True, **kwargs):
        """
        Initialize JSON formatter.
        
        Args:
            pretty: Whether to pretty-print JSON
            **kwargs: Additional arguments for BaseFormatter
        """
        super().__init__(**kwargs)
        self.pretty = pretty
    
    def format(self, summary: WorkSummary) -> str:
        """
        Format work summary as JSON.
        
        Args:
            summary: Work summary to format
            
        Returns:
            JSON string
        """
        data = summary.to_dict()
        
        if self.pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)


class JSONLinesFormatter(BaseFormatter):
    """Format work summary as JSON Lines (one JSON object per line)."""
    
    def format(self, summary: WorkSummary) -> str:
        """
        Format work summary as JSON Lines.
        
        Args:
            summary: Work summary to format
            
        Returns:
            JSON Lines string
        """
        lines = []
        for task in summary.tasks:
            lines.append(json.dumps(task.model_dump(), ensure_ascii=False))
        
        return '\n'.join(lines)
