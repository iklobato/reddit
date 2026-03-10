"""
Table formatter for work summary.

Uses rich library for beautiful terminal tables with colors.
"""

from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table as RichTable
from rich.text import Text

from work_summary.formatters.base import BaseFormatter
from work_summary.models import Task, WorkSummary
from work_summary.utils.colors import (
    ColorManager,
    colorize_company,
    colorize_status,
    colorize_type,
    colorize_source,
    colorize_priority,
)


class TableFormatter(BaseFormatter):
    """Format work summary as beautiful terminal tables."""
    
    def __init__(self, color_manager: Optional[ColorManager] = None, **kwargs):
        """
        Initialize table formatter.
        
        Args:
            color_manager: Color manager instance
            **kwargs: Additional arguments for BaseFormatter
        """
        super().__init__(**kwargs)
        self.color_manager = color_manager or ColorManager()
        self.console = Console()
    
    def format(self, summary: WorkSummary) -> str:
        """
        Format work summary as tables.
        
        Args:
            summary: Work summary to format
            
        Returns:
            Formatted table string
        """
        output_parts = []
        
        # Main header
        output_parts.append(self._format_main_header())
        
        # PRs/MRs table
        prs_mrs = summary.get_prs_and_mrs()
        if prs_mrs:
            output_parts.append(self._format_section_header(f"Pull Requests / Merge Requests ({len(prs_mrs)})"))
            output_parts.append(self.format_prs_mrs_table(prs_mrs))
        
        # Issues table
        issues = summary.get_issues()
        if issues:
            output_parts.append(self._format_section_header(f"Issues ({len(issues)})"))
            output_parts.append(self.format_comprehensive_table(issues))
        
        # Cards table (Jira/Shortcut)
        cards = summary.get_cards()
        if cards:
            output_parts.append(self._format_section_header(f"Cards - Shortcut / Jira ({len(cards)})"))
            output_parts.append(self.format_comprehensive_table(cards))
        
        if not prs_mrs and not issues and not cards:
            output_parts.append("No tasks found")
        
        # Footer
        output_parts.append(self._format_footer())
        
        return '\n\n'.join(output_parts)
    
    def format_prs_mrs_table(self, tasks: List[Task]) -> str:
        """
        Format PRs/MRs table.
        
        Args:
            tasks: List of PR/MR tasks
            
        Returns:
            Formatted table string
        """
        table = RichTable(show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Company", style="cyan")
        table.add_column("ID", style="bright_green")
        table.add_column("Title", style="white", no_wrap=False)
        table.add_column("Status")
        table.add_column("Updated", style="dim")
        table.add_column("Comments")
        
        # Check if we have additional fields
        has_draft = any(task.is_draft for task in tasks)
        has_review = any(task.review_decision for task in tasks)
        
        if has_draft:
            table.add_column("Draft/WIP")
        if has_review:
            table.add_column("Review")
        
        table.add_column("URL", style="bright_black", no_wrap=False)
        
        # Add rows
        for task in tasks:
            row = [
                colorize_company(task.company.title(), self.color_manager),
                task.id,
                task.title,
                colorize_status(task.status, self.color_manager),
                task.updated or "N/A",
                f"{task.total_comments or 0}/{task.resolved_review_comments or 0}",
            ]
            
            if has_draft:
                draft_text = "Draft" if task.is_draft else ""
                if draft_text:
                    draft_text = self.color_manager.yellow(draft_text)
                row.append(draft_text)
            
            if has_review:
                review_text = self._format_review_status(task.review_decision)
                row.append(review_text)
            
            row.append(task.url or "")
            
            table.add_row(*row)
        
        # Render to string
        with self.console.capture() as capture:
            self.console.print(table)
        
        return capture.get()
    
    def format_comprehensive_table(self, tasks: List[Task]) -> str:
        """
        Format comprehensive table with all fields.
        
        Args:
            tasks: List of tasks
            
        Returns:
            Formatted table string
        """
        table = RichTable(show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Company", style="cyan")
        table.add_column("Source")
        table.add_column("Type")
        table.add_column("ID")
        table.add_column("Title", style="white", no_wrap=False)
        table.add_column("Status")
        table.add_column("Repository", style="dim")
        
        # Check for optional fields
        has_created = any(task.created for task in tasks)
        has_priority = any(task.priority for task in tasks)
        has_assignee = any(task.assignee for task in tasks)
        has_watching = any(task.is_watching for task in tasks)
        
        if has_created:
            table.add_column("Created", style="dim")
        
        table.add_column("Updated", style="dim")
        
        if has_priority:
            table.add_column("Priority")
        if has_assignee:
            table.add_column("Assignee", style="cyan")
        if has_watching:
            table.add_column("Watching")
        
        table.add_column("URL", style="bright_black", no_wrap=False)
        
        # Add rows
        for task in tasks:
            # Add watching indicator to title if present
            title = task.title
            if task.is_watching:
                title = f"👁 {title}"
            
            row = [
                colorize_company(task.company.title(), self.color_manager),
                colorize_source(task.source, self.color_manager),
                colorize_type(task.type, self.color_manager),
                self._colorize_id(task.id),
                title,
                colorize_status(task.status, self.color_manager),
                task.repo or "N/A",
            ]
            
            if has_created:
                row.append(task.created or "")
            
            row.append(task.updated or "N/A")
            
            if has_priority:
                priority_text = task.priority or ""
                if priority_text:
                    priority_text = colorize_priority(priority_text, self.color_manager)
                row.append(priority_text)
            
            if has_assignee:
                assignee = task.assignee or ""
                if assignee and assignee not in ["Unassigned", "null"]:
                    assignee = self.color_manager.cyan(assignee)
                else:
                    assignee = ""
                row.append(assignee)
            
            if has_watching:
                watching_text = ""
                if task.is_watching:
                    watching_text = "👁 Watching"
                    if task.watch_count and task.watch_count > 0:
                        watching_text += f" ({task.watch_count})"
                    watching_text = self.color_manager.yellow(watching_text)
                row.append(watching_text)
            
            row.append(task.url or "")
            
            table.add_row(*row)
        
        # Render to string
        with self.console.capture() as capture:
            self.console.print(table)
        
        return capture.get()
    
    def _format_main_header(self) -> str:
        """Format main header."""
        header = self.color_manager.bold(self.color_manager.cyan(
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║              COMPREHENSIVE WORK SUMMARY                       ║\n"
            "╚═══════════════════════════════════════════════════════════════╝"
        ))
        return header
    
    def _format_section_header(self, title: str) -> str:
        """Format section header."""
        return self.color_manager.bold(self.color_manager.cyan(
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  {title}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ))
    
    def _format_footer(self) -> str:
        """Format footer."""
        return self.color_manager.bold(self.color_manager.cyan(
            "═══════════════════════════════════════════════════════════════\n"
            "  Summary Complete\n"
            "═══════════════════════════════════════════════════════════════"
        ))
    
    def _colorize_id(self, task_id: str) -> str:
        """Colorize task ID based on prefix."""
        if task_id.startswith('#'):
            return self.color_manager.bright_green(task_id)
        elif task_id.startswith('!'):
            return self.color_manager.bright_magenta(task_id)
        else:
            return self.color_manager.bright_cyan(task_id)
    
    def _format_review_status(self, review_decision: Optional[str]) -> str:
        """Format review status with colors."""
        if not review_decision:
            return ""
        
        decision_lower = review_decision.lower()
        
        if 'approved' in decision_lower:
            return self.color_manager.green(f"Review: Approved")
        elif 'changes' in decision_lower or 'requested' in decision_lower:
            return self.color_manager.red(f"Review: Changes Requested")
        elif 'required' in decision_lower:
            return self.color_manager.yellow(f"Review: Required")
        else:
            return self.color_manager.yellow(f"Review: Pending")
