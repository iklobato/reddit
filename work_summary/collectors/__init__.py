"""
Collectors module - Data collection from various sources.
"""

from work_summary.collectors.base import BaseCollector
from work_summary.collectors.github import GitHubCollector
from work_summary.collectors.gitlab import GitLabCollector
from work_summary.collectors.jira import JiraCollector
from work_summary.collectors.shortcut import ShortcutCollector

__all__ = [
    "BaseCollector",
    "GitHubCollector",
    "GitLabCollector",
    "JiraCollector",
    "ShortcutCollector",
]
