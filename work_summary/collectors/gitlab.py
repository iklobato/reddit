"""
GitLab collector for Merge Requests.

Uses python-gitlab library for API access.
"""

import logging
import os
import re
from typing import List, Optional, Dict, Any

import gitlab
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError

from work_summary.collectors.base import BaseCollector, AuthenticationError, APIError
from work_summary.models import Task, TaskSource
from work_summary.config import GitLabConfig


logger = logging.getLogger(__name__)


class GitLabCollector(BaseCollector):
    """Collector for GitLab Merge Requests."""
    
    def __init__(
        self,
        config: GitLabConfig,
        token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize GitLab collector.
        
        Args:
            config: GitLab configuration
            token: GitLab personal access token (or from GITLAB_TOKEN env)
            **kwargs: Additional arguments for BaseCollector
        """
        super().__init__(**kwargs)
        self.config = config
        self.token = token or os.getenv('GITLAB_TOKEN')
        self.gitlab: Optional[gitlab.Gitlab] = None
        self.user_username: Optional[str] = None
        
        if not self.token:
            logger.warning("No GitLab token provided. GitLab collector will be disabled.")
            self.enabled = False
    
    async def start(self) -> None:
        """Start collector and initialize GitLab client."""
        await super().start()
        
        if not self.enabled:
            return
        
        try:
            self.gitlab = gitlab.Gitlab(private_token=self.token)
            self.gitlab.auth()
            
            # Get current user
            user = self.gitlab.user
            self.user_username = user.username
            self.log_progress(f"Authenticated as {self.user_username}")
            
        except GitlabAuthenticationError:
            self._handle_auth_error("Invalid GitLab token")
        except Exception as e:
            self._handle_api_error(e, "Failed to initialize GitLab client")
    
    async def collect(self) -> List[Task]:
        """
        Collect all GitLab tasks.
        
        Returns:
            List of tasks from GitLab
        """
        if not self.enabled:
            self.log_progress("GitLab collector is disabled")
            return []
        
        self.log_progress("Collecting GitLab merge requests...")
        
        tasks = await self._collect_merge_requests()
        
        self.log_progress(f"Collected {len(tasks)} tasks from GitLab")
        return tasks
    
    async def _collect_merge_requests(self) -> List[Task]:
        """Collect merge requests authored by current user."""
        self.log_progress("Collecting merge requests...")
        
        tasks = []
        
        try:
            # Get all MRs authored by current user
            mrs = self.gitlab.mergerequests.list(
                author_username=self.user_username,
                state='opened',
                per_page=100
            )
            
            for mr in mrs:
                # Filter for configured organizations (e.g., Rivian)
                if not self._is_from_configured_org(mr.web_url):
                    continue
                
                # Get full MR details
                try:
                    project = self.gitlab.projects.get(mr.project_id)
                    full_mr = project.mergerequests.get(mr.iid)
                    
                    task = self._mr_to_task(full_mr, project)
                    tasks.append(task)
                    
                except GitlabGetError as e:
                    logger.warning(f"Failed to get MR details for !{mr.iid}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to collect merge requests: {e}")
        
        self.log_progress(f"Collected {len(tasks)} merge requests")
        return tasks
    
    def _is_from_configured_org(self, url: str) -> bool:
        """
        Check if URL is from a configured organization.
        
        Args:
            url: GitLab URL
            
        Returns:
            True if from configured org
        """
        url_lower = url.lower()
        return any(org.lower() in url_lower for org in self.config.organizations)
    
    def _mr_to_task(self, mr, project) -> Task:
        """
        Convert GitLab MR to Task.
        
        Args:
            mr: GitLab MergeRequest object
            project: GitLab Project object
            
        Returns:
            Task object
        """
        # Determine company (usually Rivian for GitLab)
        company = "rivian"
        
        # Calculate diff stats
        additions, deletions = self._calculate_diff_stats(mr)
        
        # Build additional info
        wip_info = "WIP" if mr.work_in_progress else ""
        merge_info = self._get_merge_status(mr)
        approval_info = self._get_approval_info(mr)
        branch_info = f"Branch: {mr.source_branch}→{mr.target_branch}"
        
        changes_info = f"Files: {mr.changes_count if hasattr(mr, 'changes_count') else 0}"
        if additions > 0 or deletions > 0:
            changes_info += f" | Lines: +{additions}/-{deletions}"
        
        additional_parts = []
        if wip_info:
            additional_parts.append(wip_info)
        additional_parts.append(merge_info)
        additional_parts.append(approval_info)
        additional_parts.append(branch_info)
        additional_parts.append(changes_info)
        
        additional = " | ".join(additional_parts)
        
        # Get comment counts
        try:
            notes = mr.notes.list(per_page=100)
            total_comments = len(notes)
            resolved_comments = len([n for n in notes if hasattr(n, 'resolved') and n.resolved])
        except:
            total_comments = 0
            resolved_comments = 0
        
        return Task(
            company=company,
            source=TaskSource.GITLAB,
            type="MR",
            id=f"!{mr.iid}",
            title=mr.title,
            status=mr.state,
            repo=project.path_with_namespace,
            updated=mr.updated_at.split('T')[0] if mr.updated_at else None,
            url=mr.web_url,
            additional=additional,
            additions=additions,
            deletions=deletions,
            is_draft=mr.work_in_progress,
            total_comments=total_comments,
            resolved_review_comments=resolved_comments,
            head_ref=mr.source_branch,
            base_ref=mr.target_branch,
        )
    
    def _calculate_diff_stats(self, mr) -> tuple[int, int]:
        """
        Calculate additions and deletions from MR diff.
        
        Args:
            mr: GitLab MergeRequest object
            
        Returns:
            Tuple of (additions, deletions)
        """
        try:
            changes = mr.changes()
            additions = 0
            deletions = 0
            
            for change in changes.get('changes', []):
                diff = change.get('diff', '')
                if not diff:
                    continue
                
                # Count additions and deletions
                for line in diff.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        additions += 1
                    elif line.startswith('-') and not line.startswith('---'):
                        deletions += 1
            
            return additions, deletions
            
        except Exception as e:
            logger.debug(f"Failed to calculate diff stats: {e}")
            return 0, 0
    
    @staticmethod
    def _get_merge_status(mr) -> str:
        """Get human-readable merge status."""
        if not hasattr(mr, 'merge_status'):
            return "Merge: Unknown"
        
        status = mr.merge_status
        if status == 'can_be_merged':
            return "Merge: Ready"
        elif status == 'cannot_be_merged':
            return "Merge: Blocked"
        elif status == 'checking':
            return "Merge: Checking"
        else:
            return f"Merge: {status}"
    
    @staticmethod
    def _get_approval_info(mr) -> str:
        """Get approval information."""
        try:
            if hasattr(mr, 'approvals'):
                approvals = mr.approvals.get()
                approved = approvals.approved
                approvals_required = approvals.approvals_required
                approvals_left = approvals.approvals_left
                
                if approvals_required > 0:
                    if approvals_left == 0:
                        return f"Approved ({approvals_required}/{approvals_required})"
                    else:
                        return f"Pending ({approvals_left} more)"
                else:
                    return "Not required"
            else:
                return "Not required"
        except:
            return "Not required"
