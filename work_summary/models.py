"""
Data models for work items.

Uses Pydantic for type-safe, validated data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class TaskType(str, Enum):
    """Type of work item."""
    PR = "PR"
    PULL_REQUEST = "Pull Request"
    MR = "MR"
    MERGE_REQUEST = "Merge Request"
    ISSUE = "Issue"
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"
    EPIC = "Epic"
    CARD = "Card"


class TaskStatus(str, Enum):
    """Status of work item."""
    OPEN = "open"
    OPENED = "opened"
    CLOSED = "closed"
    MERGED = "merged"
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    TODO = "todo"
    DONE = "done"
    CANCELLED = "cancelled"
    REVIEW = "review"
    PENDING = "pending"


class TaskSource(str, Enum):
    """Source platform for work item."""
    GITHUB = "GitHub"
    GITLAB = "GitLab"
    JIRA = "Jira"
    SHORTCUT = "Shortcut"


class Company(str, Enum):
    """Company/organization."""
    PRECISETARGETLABS = "precisetargetlabs"
    SANCTUM = "sanctum"
    RIVIAN = "rivian"
    ORLO = "orlo"


class Task(BaseModel):
    """Base model for all work items."""
    
    company: str
    source: TaskSource
    type: str
    id: str
    title: str
    status: str
    repo: Optional[str] = None
    updated: Optional[str] = None
    created: Optional[str] = None
    url: Optional[str] = None
    additional: Optional[str] = None
    description: Optional[str] = None
    
    # Optional fields for specific task types
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    labels: Optional[List[str]] = None
    comment_count: Optional[int] = 0
    watch_count: Optional[int] = 0
    is_watching: Optional[bool] = False
    
    # PR/MR specific fields
    additions: Optional[int] = None
    deletions: Optional[int] = None
    review_decision: Optional[str] = None
    is_draft: Optional[bool] = False
    total_comments: Optional[int] = 0
    resolved_review_comments: Optional[int] = 0
    head_ref: Optional[str] = None
    base_ref: Optional[str] = None
    
    # Shortcut specific
    estimate: Optional[int] = None
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class PullRequest(Task):
    """GitHub/GitLab Pull/Merge Request."""
    
    additions: int = 0
    deletions: int = 0
    review_decision: Optional[str] = None
    is_draft: bool = False
    head_ref: str
    base_ref: str
    total_comments: int = 0
    resolved_review_comments: int = 0
    
    @field_validator('type', mode='before')
    @classmethod
    def set_type(cls, v):
        """Ensure type is PR or MR."""
        if v in [TaskType.PR, TaskType.PULL_REQUEST, TaskType.MR, TaskType.MERGE_REQUEST]:
            return v
        return TaskType.PR


class Issue(Task):
    """GitHub Issue."""
    
    labels: List[str] = Field(default_factory=list)
    comment_count: int = 0
    
    @field_validator('type', mode='before')
    @classmethod
    def set_type(cls, v):
        """Ensure type is Issue."""
        return TaskType.ISSUE


class JiraCard(Task):
    """Jira ticket."""
    
    priority: str = "None"
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    comment_count: int = 0
    watch_count: int = 0
    is_watching: bool = False
    
    @field_validator('source', mode='before')
    @classmethod
    def set_source(cls, v):
        """Ensure source is Jira."""
        return TaskSource.JIRA


class ShortcutStory(Task):
    """Shortcut story."""
    
    estimate: Optional[int] = None
    labels: List[str] = Field(default_factory=list)
    
    @field_validator('source', mode='before')
    @classmethod
    def set_source(cls, v):
        """Ensure source is Shortcut."""
        return TaskSource.SHORTCUT


class WorkSummary(BaseModel):
    """Container for all collected work items."""
    
    tasks: List[Task] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=datetime.now)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the summary."""
        self.tasks.append(task)
    
    def get_by_company(self, company: str) -> List[Task]:
        """Get tasks filtered by company."""
        return [t for t in self.tasks if t.company.lower() == company.lower()]
    
    def get_by_source(self, source: TaskSource) -> List[Task]:
        """Get tasks filtered by source."""
        return [t for t in self.tasks if t.source == source]
    
    def get_by_type(self, task_type: str) -> List[Task]:
        """Get tasks filtered by type."""
        return [t for t in self.tasks if t.type == task_type]
    
    def get_prs_and_mrs(self) -> List[Task]:
        """Get all PRs and MRs."""
        return [t for t in self.tasks if t.type in [
            TaskType.PR, TaskType.PULL_REQUEST, TaskType.MR, TaskType.MERGE_REQUEST, "PR", "MR"
        ]]
    
    def get_issues(self) -> List[Task]:
        """Get all issues."""
        return [t for t in self.tasks if t.type == TaskType.ISSUE or t.type == "Issue"]
    
    def get_cards(self) -> List[Task]:
        """Get all cards (Jira/Shortcut items that aren't PRs/MRs/Issues)."""
        return [t for t in self.tasks 
                if t.source in [TaskSource.JIRA, TaskSource.SHORTCUT]
                and t.type not in [TaskType.PR, TaskType.PULL_REQUEST, TaskType.MR, 
                                   TaskType.MERGE_REQUEST, TaskType.ISSUE, "PR", "MR", "Issue"]]
    
    @property
    def total_count(self) -> int:
        """Total number of tasks."""
        return len(self.tasks)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tasks": [task.model_dump() for task in self.tasks],
            "collected_at": self.collected_at.isoformat(),
            "total_count": self.total_count
        }
