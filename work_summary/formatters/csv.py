"""
CSV formatter for work summary.

Outputs work items in CSV format for spreadsheet analysis.
"""

import csv
import io
from typing import List, Optional

from work_summary.formatters.base import BaseFormatter
from work_summary.models import Task, WorkSummary


class CSVFormatter(BaseFormatter):
    """Format work summary as CSV."""
    
    def __init__(
        self,
        delimiter: str = ',',
        include_headers: bool = True,
        fields: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize CSV formatter.
        
        Args:
            delimiter: CSV delimiter character
            include_headers: Whether to include header row
            fields: List of field names to include (None = all)
            **kwargs: Additional arguments for BaseFormatter
        """
        super().__init__(**kwargs)
        self.delimiter = delimiter
        self.include_headers = include_headers
        self.fields = fields or [
            'company', 'source', 'type', 'id', 'title', 'status',
            'repo', 'updated', 'url', 'additional'
        ]
    
    def format(self, summary: WorkSummary) -> str:
        """
        Format work summary as CSV.
        
        Args:
            summary: Work summary to format
            
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.fields,
            delimiter=self.delimiter,
            extrasaction='ignore'
        )
        
        if self.include_headers:
            writer.writeheader()
        
        for task in summary.tasks:
            task_dict = task.model_dump()
            # Convert lists to strings
            for key, value in task_dict.items():
                if isinstance(value, list):
                    task_dict[key] = ', '.join(str(v) for v in value)
            writer.writerow(task_dict)
        
        return output.getvalue()
