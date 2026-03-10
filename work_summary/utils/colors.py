"""
ANSI color utilities for terminal output.

Provides centralized color management with support for themes and
automatic detection of terminal capabilities.
"""

import os
import sys
from enum import Enum
from typing import Optional


class ColorTheme(str, Enum):
    """Available color themes."""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    NONE = "none"


class Colors:
    """ANSI color codes and formatting."""
    
    # Reset
    RESET = '\033[0m'
    
    # Text formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class ColorManager:
    """Manages color output based on terminal capabilities and user preferences."""
    
    def __init__(self, theme: ColorTheme = ColorTheme.DEFAULT, enabled: Optional[bool] = None):
        """
        Initialize color manager.
        
        Args:
            theme: Color theme to use
            enabled: Force enable/disable colors. If None, auto-detect.
        """
        self.theme = theme
        self._enabled = enabled if enabled is not None else self._detect_color_support()
    
    @staticmethod
    def _detect_color_support() -> bool:
        """
        Detect if terminal supports colors.
        
        Returns:
            True if colors are supported
        """
        # Check if output is a TTY
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check environment variables
        if os.environ.get('NO_COLOR'):
            return False
        
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # Check TERM variable
        term = os.environ.get('TERM', '')
        if term in ('dumb', 'unknown'):
            return False
        
        return True
    
    def colorize(self, text: str, color: str) -> str:
        """
        Apply color to text.
        
        Args:
            text: Text to colorize
            color: ANSI color code
            
        Returns:
            Colorized text or plain text if colors disabled
        """
        if not self._enabled or self.theme == ColorTheme.NONE:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    def bold(self, text: str) -> str:
        """Make text bold."""
        return self.colorize(text, Colors.BOLD)
    
    def dim(self, text: str) -> str:
        """Make text dim."""
        return self.colorize(text, Colors.DIM)
    
    def red(self, text: str) -> str:
        """Make text red."""
        return self.colorize(text, Colors.RED)
    
    def green(self, text: str) -> str:
        """Make text green."""
        return self.colorize(text, Colors.GREEN)
    
    def yellow(self, text: str) -> str:
        """Make text yellow."""
        return self.colorize(text, Colors.YELLOW)
    
    def blue(self, text: str) -> str:
        """Make text blue."""
        return self.colorize(text, Colors.BLUE)
    
    def magenta(self, text: str) -> str:
        """Make text magenta."""
        return self.colorize(text, Colors.MAGENTA)
    
    def cyan(self, text: str) -> str:
        """Make text cyan."""
        return self.colorize(text, Colors.CYAN)
    
    def white(self, text: str) -> str:
        """Make text white."""
        return self.colorize(text, Colors.WHITE)
    
    def bright_green(self, text: str) -> str:
        """Make text bright green."""
        return self.colorize(text, Colors.BRIGHT_GREEN)
    
    def bright_cyan(self, text: str) -> str:
        """Make text bright cyan."""
        return self.colorize(text, Colors.BRIGHT_CYAN)
    
    def bright_magenta(self, text: str) -> str:
        """Make text bright magenta."""
        return self.colorize(text, Colors.BRIGHT_MAGENTA)
    
    def bright_black(self, text: str) -> str:
        """Make text bright black (gray)."""
        return self.colorize(text, Colors.BRIGHT_BLACK)


# Semantic colorizers
def colorize_company(company: str, color_manager: Optional[ColorManager] = None) -> str:
    """
    Colorize company names.
    
    Args:
        company: Company name
        color_manager: Color manager instance
        
    Returns:
        Colorized company name
    """
    if color_manager is None:
        color_manager = ColorManager()
    
    company_lower = company.lower()
    if 'precisetarget' in company_lower:
        return color_manager.cyan(company)
    elif 'rivian' in company_lower:
        return color_manager.magenta(company)
    elif 'sanctum' in company_lower:
        return color_manager.yellow(company)
    elif 'orlo' in company_lower:
        return color_manager.blue(company)
    return company


def colorize_status(status: str, color_manager: Optional[ColorManager] = None) -> str:
    """
    Colorize status values.
    
    Args:
        status: Status string
        color_manager: Color manager instance
        
    Returns:
        Colorized status
    """
    if color_manager is None:
        color_manager = ColorManager()
    
    status_lower = status.lower()
    if any(word in status_lower for word in ['open', 'opened', 'todo', 'to do']):
        return color_manager.green(status)
    elif any(word in status_lower for word in ['closed', 'done', 'resolved', 'completed', 'merged', 'cancelled']):
        return color_manager.red(status)
    elif any(word in status_lower for word in ['in progress', 'wip', 'inprogress']):
        return color_manager.yellow(status)
    elif any(word in status_lower for word in ['review', 'testing', 'qa', 'pending']):
        return color_manager.blue(status)
    return status


def colorize_type(task_type: str, color_manager: Optional[ColorManager] = None) -> str:
    """
    Colorize task types.
    
    Args:
        task_type: Task type string
        color_manager: Color manager instance
        
    Returns:
        Colorized task type
    """
    if color_manager is None:
        color_manager = ColorManager()
    
    type_lower = task_type.lower()
    if 'pr' in type_lower or 'pull' in type_lower:
        return color_manager.green(task_type)
    elif 'mr' in type_lower or 'merge' in type_lower:
        return color_manager.magenta(task_type)
    elif 'issue' in type_lower:
        return color_manager.blue(task_type)
    elif 'task' in type_lower or 'story' in type_lower:
        return color_manager.cyan(task_type)
    elif 'bug' in type_lower:
        return color_manager.red(task_type)
    elif 'epic' in type_lower:
        return color_manager.bright_magenta(task_type)
    return task_type


def colorize_source(source: str, color_manager: Optional[ColorManager] = None) -> str:
    """
    Colorize source names.
    
    Args:
        source: Source platform name
        color_manager: Color manager instance
        
    Returns:
        Colorized source name
    """
    if color_manager is None:
        color_manager = ColorManager()
    
    source_lower = source.lower()
    if 'github' in source_lower:
        return color_manager.bright_black(source)
    elif 'gitlab' in source_lower:
        return color_manager.magenta(source)
    elif 'jira' in source_lower:
        return color_manager.blue(source)
    elif 'shortcut' in source_lower:
        return color_manager.yellow(source)
    return source


def colorize_priority(priority: str, color_manager: Optional[ColorManager] = None) -> str:
    """
    Colorize priority values.
    
    Args:
        priority: Priority string
        color_manager: Color manager instance
        
    Returns:
        Colorized priority
    """
    if color_manager is None:
        color_manager = ColorManager()
    
    priority_lower = priority.lower()
    if any(word in priority_lower for word in ['high', 'critical', 'blocker', 'urgent']):
        return color_manager.red(priority)
    elif 'medium' in priority_lower:
        return color_manager.yellow(priority)
    elif 'low' in priority_lower:
        return color_manager.green(priority)
    return priority


# Global color manager instance
_global_color_manager: Optional[ColorManager] = None


def get_color_manager() -> ColorManager:
    """Get the global color manager instance."""
    global _global_color_manager
    if _global_color_manager is None:
        _global_color_manager = ColorManager()
    return _global_color_manager


def set_color_manager(color_manager: ColorManager) -> None:
    """Set the global color manager instance."""
    global _global_color_manager
    _global_color_manager = color_manager
