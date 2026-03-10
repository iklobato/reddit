"""
GitHub collector for PRs, Issues, and Project items.

Uses PyGithub library for API access with async support.
"""

import asyncio
import logging
import os
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from github import Github, Auth
from github.GithubException import GithubException, BadCredentialsException

from work_summary.collectors.base import BaseCollector, AuthenticationError, APIError
from work_summary.models import Task, TaskSource
from work_summary.config import GitHubConfig


logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """Collector for GitHub PRs, Issues, and Project items."""
    
    def __init__(
        self,
        config: GitHubConfig,
        token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize GitHub collector.
        
        Args:
            config: GitHub configuration
            token: GitHub personal access token (or from GITHUB_TOKEN env)
            **kwargs: Additional arguments for BaseCollector
        """
        super().__init__(**kwargs)
        self.config = config
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.github: Optional[Github] = None
        self.user_login: Optional[str] = None
        
        if not self.token:
            logger.warning("No GitHub token provided. GitHub collector will be disabled.")
            self.enabled = False
    
    async def start(self) -> None:
        """Start collector and initialize GitHub client."""
        await super().start()
        
        if not self.enabled:
            return
        
        try:
            auth = Auth.Token(self.token)
            self.github = Github(auth=auth)
            
            # Get current user
            user = self.github.get_user()
            self.user_login = user.login
            self.log_progress(f"Authenticated as {self.user_login}")
            
        except BadCredentialsException:
            self._handle_auth_error("Invalid GitHub token")
        except GithubException as e:
            self._handle_api_error(e, "Failed to initialize GitHub client")
    
    async def close(self) -> None:
        """Close GitHub client."""
        if self.github is not None:
            self.github.close()
            self.github = None
        await super().close()
    
    async def collect(self) -> List[Task]:
        """
        Collect all GitHub tasks.
        
        Returns:
            List of tasks from GitHub
        """
        if not self.enabled:
            self.log_progress("GitHub collector is disabled")
            return []
        
        self.log_progress("Collecting GitHub tasks...")
        
        tasks = []
        
        # Collect in parallel
        results = await asyncio.gather(
            self._collect_pull_requests(),
            self._collect_issues(),
            self._collect_project_items(),
            return_exceptions=True
        )
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Collection failed: {result}")
            elif isinstance(result, list):
                tasks.extend(result)
        
        self.log_progress(f"Collected {len(tasks)} tasks from GitHub")
        return tasks
    
    async def _collect_pull_requests(self) -> List[Task]:
        """Collect pull requests from configured organizations and repos."""
        self.log_progress("Collecting pull requests...")
        
        tasks = []
        
        for org_name in self.config.organizations:
            try:
                # For precisetargetlabs, only check specific repos
                if org_name == "precisetargetlabs":
                    repos_to_check = self.config.repos
                else:
                    # For other orgs, get all repos
                    org = self.github.get_organization(org_name)
                    repos_to_check = [repo.name for repo in org.get_repos()]
                
                for repo_name in repos_to_check:
                    try:
                        repo = self.github.get_repo(f"{org_name}/{repo_name}")
                        
                        # Get PRs authored by current user
                        pulls = repo.get_pulls(
                            state='open',
                            sort='updated',
                            direction='desc'
                        )
                        
                        for pr in pulls:
                            if pr.user.login == self.user_login:
                                task = self._pr_to_task(pr, org_name)
                                tasks.append(task)
                        
                    except GithubException as e:
                        logger.warning(f"Failed to get PRs from {org_name}/{repo_name}: {e}")
                        continue
                
            except GithubException as e:
                logger.warning(f"Failed to access organization {org_name}: {e}")
                continue
        
        self.log_progress(f"Collected {len(tasks)} pull requests")
        return tasks
    
    async def _collect_issues(self) -> List[Task]:
        """Collect issues assigned to current user."""
        self.log_progress("Collecting issues...")
        
        tasks = []
        
        for org_name in self.config.organizations:
            try:
                # Search for issues assigned to current user in this org
                query = f"is:issue is:open assignee:{self.user_login} org:{org_name}"
                issues = self.github.search_issues(query)
                
                for issue in issues:
                    # Skip pull requests (they show up in issue search too)
                    if issue.pull_request is not None:
                        continue
                    
                    task = self._issue_to_task(issue, org_name)
                    tasks.append(task)
                
            except GithubException as e:
                logger.warning(f"Failed to search issues in {org_name}: {e}")
                continue
        
        self.log_progress(f"Collected {len(tasks)} issues")
        return tasks
    
    async def _collect_project_items(self) -> List[Task]:
        """Collect items from GitHub Projects."""
        if not self.config.project_number:
            return []
        
        self.log_progress("Collecting project items...")
        
        # Note: GitHub Projects V2 API requires GraphQL
        # For now, we'll skip this or implement a simpler version
        # The bash script uses GraphQL which is complex to replicate
        
        # TODO: Implement GraphQL-based project collection
        logger.info("GitHub Projects collection not yet implemented (requires GraphQL)")
        return []
    
    def _pr_to_task(self, pr, org_name: str) -> Task:
        """
        Convert GitHub PR to Task.
        
        Args:
            pr: GitHub PullRequest object
            org_name: Organization name
            
        Returns:
            Task object
        """
        # Determine company
        company = "precisetargetlabs"
        if "sanctum" in org_name.lower():
            company = "sanctum"
        
        # Build additional info
        review_status = self._get_review_status(pr)
        draft_info = "Draft" if pr.draft else ""
        branch_info = f"Branch: {pr.head.ref}→{pr.base.ref}"
        changes_info = f"Changes: +{pr.additions}/-{pr.deletions}"
        
        additional_parts = []
        if draft_info:
            additional_parts.append(draft_info)
        additional_parts.append(review_status)
        additional_parts.append(branch_info)
        additional_parts.append(changes_info)
        
        # Get reviewers
        reviewers = [r.login for r in pr.get_review_requests()[0]]
        if reviewers:
            additional_parts.append(f"Reviewers: {', '.join(reviewers)}")
        
        additional = " | ".join(additional_parts)
        
        # Get comment counts
        total_comments = pr.comments
        # Reviews that have been submitted
        reviews = list(pr.get_reviews())
        resolved_review_comments = len([r for r in reviews if r.state in ['APPROVED', 'CHANGES_REQUESTED', 'COMMENTED']])
        
        return Task(
            company=company,
            source=TaskSource.GITHUB,
            type="PR",
            id=f"#{pr.number}",
            title=pr.title,
            status=pr.state,
            repo=pr.base.repo.full_name,
            updated=pr.updated_at.strftime('%Y-%m-%d') if pr.updated_at else None,
            url=pr.html_url,
            additional=additional,
            additions=pr.additions,
            deletions=pr.deletions,
            review_decision=self._get_review_decision(pr),
            is_draft=pr.draft,
            total_comments=total_comments,
            resolved_review_comments=resolved_review_comments,
            head_ref=pr.head.ref,
            base_ref=pr.base.ref,
        )
    
    def _issue_to_task(self, issue, org_name: str) -> Task:
        """
        Convert GitHub Issue to Task.
        
        Args:
            issue: GitHub Issue object
            org_name: Organization name
            
        Returns:
            Task object
        """
        # Determine company
        company = "precisetargetlabs"
        if "sanctum" in org_name.lower():
            company = "sanctum"
        
        # Get labels
        labels = [label.name for label in issue.labels]
        labels_str = ", ".join(labels) if labels else "None"
        
        # Build additional info
        additional_parts = [f"Labels: {labels_str}"]
        if issue.comments > 0:
            additional_parts.append(f"Comments: {issue.comments}")
        if issue.user:
            additional_parts.append(f"Author: {issue.user.login}")
        
        additional = " | ".join(additional_parts)
        
        return Task(
            company=company,
            source=TaskSource.GITHUB,
            type="Issue",
            id=f"#{issue.number}",
            title=issue.title,
            status=issue.state,
            repo=issue.repository.full_name if hasattr(issue, 'repository') else None,
            updated=issue.updated_at.strftime('%Y-%m-%d') if issue.updated_at else None,
            url=issue.html_url,
            additional=additional,
            labels=labels,
            comment_count=issue.comments,
            description=issue.body[:500] if issue.body else None,
        )
    
    @staticmethod
    def _get_review_status(pr) -> str:
        """Get human-readable review status."""
        # Get the latest review decision
        reviews = list(pr.get_reviews())
        
        if not reviews:
            return "Review: Pending"
        
        # Check latest reviews by unique reviewers
        reviewer_states = {}
        for review in reviews:
            reviewer_states[review.user.login] = review.state
        
        # Determine overall status
        if any(state == 'CHANGES_REQUESTED' for state in reviewer_states.values()):
            return "Review: Changes Requested"
        elif all(state == 'APPROVED' for state in reviewer_states.values()):
            return "Review: Approved"
        elif any(state == 'APPROVED' for state in reviewer_states.values()):
            return "Review: Partially Approved"
        else:
            return "Review: Pending"
    
    @staticmethod
    def _get_review_decision(pr) -> Optional[str]:
        """Get review decision for PR."""
        reviews = list(pr.get_reviews())
        
        if not reviews:
            return "PENDING"
        
        reviewer_states = {}
        for review in reviews:
            reviewer_states[review.user.login] = review.state
        
        if any(state == 'CHANGES_REQUESTED' for state in reviewer_states.values()):
            return "CHANGES_REQUESTED"
        elif all(state == 'APPROVED' for state in reviewer_states.values()):
            return "APPROVED"
        else:
            return "PENDING"
