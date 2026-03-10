"""
Jira collector for issues and tasks.

Supports multiple Jira instances with different authentication.
"""

import logging
from typing import List, Optional, Dict, Any

from jira import JIRA
from jira.exceptions import JIRAError

from work_summary.collectors.base import BaseCollector, AuthenticationError, APIError
from work_summary.models import Task, TaskSource
from work_summary.config import JiraConfig, JiraInstance


logger = logging.getLogger(__name__)


class JiraCollector(BaseCollector):
    """Collector for Jira issues from multiple instances."""
    
    def __init__(
        self,
        config: JiraConfig,
        **kwargs
    ):
        """
        Initialize Jira collector.
        
        Args:
            config: Jira configuration with multiple instances
            **kwargs: Additional arguments for BaseCollector
        """
        super().__init__(**kwargs)
        self.config = config
        self.instances: List[JiraInstance] = []
        self.jira_clients: Dict[str, JIRA] = {}
        
        # Get instances from config
        self.instances = config.get_instances()
        
        if not self.instances:
            logger.warning("No Jira instances configured. Jira collector will be disabled.")
            self.enabled = False
    
    async def start(self) -> None:
        """Start collector and initialize Jira clients."""
        await super().start()
        
        if not self.enabled:
            return
        
        # Initialize clients for each instance
        for instance in self.instances:
            try:
                jira_client = JIRA(
                    server=instance.url,
                    basic_auth=(instance.email, instance.token)
                )
                
                # Test connection
                jira_client.myself()
                
                self.jira_clients[instance.name] = jira_client
                self.log_progress(f"Connected to Jira instance: {instance.name}")
                
            except JIRAError as e:
                if e.status_code == 401:
                    logger.error(f"Authentication failed for Jira instance {instance.name}")
                else:
                    logger.error(f"Failed to connect to Jira instance {instance.name}: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize Jira client for {instance.name}: {e}")
    
    async def collect(self) -> List[Task]:
        """
        Collect all Jira tasks from all instances.
        
        Returns:
            List of tasks from all Jira instances
        """
        if not self.enabled:
            self.log_progress("Jira collector is disabled")
            return []
        
        self.log_progress("Collecting Jira issues from all instances...")
        
        tasks = []
        
        for instance in self.instances:
            if instance.name not in self.jira_clients:
                continue
            
            try:
                instance_tasks = await self._collect_from_instance(instance)
                tasks.extend(instance_tasks)
            except Exception as e:
                logger.error(f"Failed to collect from Jira instance {instance.name}: {e}")
        
        self.log_progress(f"Collected {len(tasks)} tasks from Jira")
        return tasks
    
    async def _collect_from_instance(self, instance: JiraInstance) -> List[Task]:
        """
        Collect issues from a single Jira instance.
        
        Args:
            instance: Jira instance configuration
            
        Returns:
            List of tasks from this instance
        """
        self.log_progress(f"Collecting from {instance.name}...")
        
        jira_client = self.jira_clients[instance.name]
        tasks = []
        
        try:
            # Build JQL query for assigned or watched issues
            jql = self._build_jql_query()
            
            # Search for issues
            issues = jira_client.search_issues(
                jql,
                maxResults=100,
                fields='summary,status,project,updated,created,description,comment,priority,issuetype,assignee,reporter,watches'
            )
            
            for issue in issues:
                task = self._issue_to_task(issue, instance)
                tasks.append(task)
            
            self.log_progress(f"Collected {len(tasks)} issues from {instance.name}")
            
        except JIRAError as e:
            logger.error(f"JQL query failed for {instance.name}: {e}")
        except Exception as e:
            logger.error(f"Failed to collect issues from {instance.name}: {e}")
        
        return tasks
    
    @staticmethod
    def _build_jql_query() -> str:
        """
        Build JQL query for fetching issues.
        
        Returns:
            JQL query string
        """
        # Get issues assigned to or watched by current user
        # Exclude Done and Closed statuses
        return "(assignee = currentUser() OR watcher = currentUser()) AND status != Done AND status != Closed ORDER BY updated DESC"
    
    def _issue_to_task(self, issue, instance: JiraInstance) -> Task:
        """
        Convert Jira issue to Task.
        
        Args:
            issue: Jira Issue object
            instance: Jira instance configuration
            
        Returns:
            Task object
        """
        # Extract fields
        key = issue.key
        title = issue.fields.summary
        status = issue.fields.status.name
        project = issue.fields.project.name
        updated = issue.fields.updated.split('T')[0] if issue.fields.updated else None
        created = issue.fields.created.split('T')[0] if issue.fields.created else None
        
        # Description
        description = self._parse_description(issue.fields.description)
        
        # Priority
        priority = issue.fields.priority.name if issue.fields.priority else "None"
        
        # Issue type
        issue_type = issue.fields.issuetype.name if issue.fields.issuetype else "Task"
        
        # Assignee and reporter
        assignee = issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
        reporter = issue.fields.reporter.displayName if issue.fields.reporter else "Unknown"
        
        # Comments
        comment_count = len(issue.fields.comment.comments) if hasattr(issue.fields.comment, 'comments') else 0
        
        # Watches
        watch_count = issue.fields.watches.watchCount if issue.fields.watches else 0
        is_watching = issue.fields.watches.isWatching if issue.fields.watches else False
        
        # Build additional info
        additional_parts = [
            f"Type: {issue_type}",
            f"Priority: {priority}"
        ]
        
        if assignee != "Unassigned":
            additional_parts.append(f"Assignee: {assignee}")
        
        if is_watching:
            watching_text = "👁 Watching"
            if watch_count > 0:
                watching_text += f" ({watch_count})"
            additional_parts.append(watching_text)
        
        if comment_count > 0:
            additional_parts.append(f"Comments: {comment_count}")
        
        additional_parts.append(f"Reporter: {reporter}")
        
        additional = " | ".join(additional_parts)
        
        # Build URL
        url = f"{instance.url}/browse/{key}"
        
        return Task(
            company=instance.company,
            source=TaskSource.JIRA,
            type=issue_type,
            id=key,
            title=title,
            status=status,
            repo=project,
            updated=updated,
            created=created,
            url=url,
            additional=additional,
            description=description,
            priority=priority,
            assignee=assignee,
            reporter=reporter,
            comment_count=comment_count,
            watch_count=watch_count,
            is_watching=is_watching,
        )
    
    @staticmethod
    def _parse_description(description) -> Optional[str]:
        """
        Parse Jira description field.
        
        Jira can use different formats (plain text, ADF, etc.)
        
        Args:
            description: Description field from Jira
            
        Returns:
            Plain text description or None
        """
        if description is None:
            return None
        
        # If it's already a string, return it
        if isinstance(description, str):
            return description[:500] if len(description) > 500 else description
        
        # If it's ADF (Atlassian Document Format), try to extract text
        if isinstance(description, dict):
            try:
                return JiraCollector._extract_text_from_adf(description)
            except:
                return str(description)[:500]
        
        return None
    
    @staticmethod
    def _extract_text_from_adf(adf_doc: Dict[str, Any]) -> str:
        """
        Extract plain text from Atlassian Document Format.
        
        Args:
            adf_doc: ADF document dictionary
            
        Returns:
            Plain text content
        """
        def extract_text(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    return node.get('text', '')
                elif 'content' in node:
                    return ''.join(extract_text(child) for child in node['content'])
            return ''
        
        text = extract_text(adf_doc)
        return text[:500] if len(text) > 500 else text
