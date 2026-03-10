"""
Shortcut collector for stories.

Uses Shortcut REST API for data collection.
"""

import logging
from typing import List, Optional, Dict, Any

from work_summary.collectors.base import BaseCollector, AuthenticationError, APIError
from work_summary.models import Task, TaskSource
from work_summary.config import ShortcutConfig


logger = logging.getLogger(__name__)


class ShortcutCollector(BaseCollector):
    """Collector for Shortcut stories."""
    
    def __init__(
        self,
        config: ShortcutConfig,
        **kwargs
    ):
        """
        Initialize Shortcut collector.
        
        Args:
            config: Shortcut configuration
            **kwargs: Additional arguments for BaseCollector
        """
        super().__init__(**kwargs)
        self.config = config
        self.api_base = "https://api.app.shortcut.com/api/v3"
        self.member_id: Optional[str] = None
        self.mention_name: Optional[str] = None
        
        if not self.config.api_key:
            logger.warning("No Shortcut API key provided. Shortcut collector will be disabled.")
            self.enabled = False
    
    async def start(self) -> None:
        """Start collector and get member info."""
        await super().start()
        
        if not self.enabled:
            return
        
        try:
            # Get current member info
            member_info = await self._get_member_info()
            self.member_id = member_info.get('id')
            self.mention_name = member_info.get('mention_name')
            
            if not self.member_id or not self.mention_name:
                self._handle_auth_error("Failed to get member info from Shortcut")
            
            self.log_progress(f"Authenticated as {self.mention_name}")
            
        except Exception as e:
            self._handle_api_error(e, "Failed to initialize Shortcut client")
    
    async def collect(self) -> List[Task]:
        """
        Collect all Shortcut tasks.
        
        Returns:
            List of tasks from Shortcut
        """
        if not self.enabled:
            self.log_progress("Shortcut collector is disabled")
            return []
        
        self.log_progress("Collecting Shortcut stories...")
        
        tasks = await self._collect_stories()
        
        self.log_progress(f"Collected {len(tasks)} tasks from Shortcut")
        return tasks
    
    async def _get_member_info(self) -> Dict[str, Any]:
        """
        Get current member information.
        
        Returns:
            Member info dictionary
        """
        headers = {
            'Shortcut-Token': self.config.api_key,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_base}/member"
        
        try:
            response = await self.http_client.get(url, headers=headers)
            data = await response.json()
            
            if 'error' in data:
                raise APIError(f"Shortcut API error: {data['error']}")
            
            return data
            
        except Exception as e:
            raise APIError(f"Failed to get member info: {e}")
    
    async def _collect_stories(self) -> List[Task]:
        """
        Collect stories owned by current user.
        
        Returns:
            List of tasks
        """
        self.log_progress("Collecting stories...")
        
        headers = {
            'Shortcut-Token': self.config.api_key,
            'Content-Type': 'application/json'
        }
        
        # Try searching by mention_name first
        url = f"{self.api_base}/search/stories"
        params = {
            'query': f'owner:{self.mention_name}',
            'page_size': 100
        }
        
        try:
            response = await self.http_client.get(url, headers=headers, params=params)
            data = await response.json()
            
            if 'error' in data:
                # Fallback: get all open stories and filter
                return await self._collect_stories_fallback(headers)
            
            stories = data.get('data', [])
            total = data.get('total', 0)
            
            if total == 0:
                # Fallback: get all open stories and filter
                return await self._collect_stories_fallback(headers)
            
            # Filter out completed/archived stories
            active_stories = [
                story for story in stories
                if not self._is_story_completed(story)
            ]
            
            tasks = [self._story_to_task(story) for story in active_stories]
            
            self.log_progress(f"Collected {len(tasks)} stories")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to collect stories: {e}")
            return []
    
    async def _collect_stories_fallback(self, headers: Dict[str, str]) -> List[Task]:
        """
        Fallback method to collect stories by filtering all open stories.
        
        Args:
            headers: Request headers
            
        Returns:
            List of tasks
        """
        self.log_progress("Using fallback method to collect stories...")
        
        url = f"{self.api_base}/search/stories"
        params = {
            'query': 'is:open is:story',
            'page_size': 100
        }
        
        try:
            response = await self.http_client.get(url, headers=headers, params=params)
            data = await response.json()
            
            if 'error' in data:
                logger.error(f"Fallback search failed: {data['error']}")
                return []
            
            stories = data.get('data', [])
            
            # Filter by owner_ids containing member_id
            my_stories = [
                story for story in stories
                if self.member_id in story.get('owner_ids', [])
                and not self._is_story_completed(story)
            ]
            
            tasks = [self._story_to_task(story) for story in my_stories]
            
            self.log_progress(f"Collected {len(tasks)} stories (fallback)")
            return tasks
            
        except Exception as e:
            logger.error(f"Fallback collection failed: {e}")
            return []
    
    @staticmethod
    def _is_story_completed(story: Dict[str, Any]) -> bool:
        """
        Check if story is completed or archived.
        
        Args:
            story: Story dictionary
            
        Returns:
            True if completed/archived
        """
        workflow_state = story.get('workflow_state_name', '').lower()
        archived = story.get('archived', False)
        
        return archived or workflow_state in ['done', 'completed']
    
    def _story_to_task(self, story: Dict[str, Any]) -> Task:
        """
        Convert Shortcut story to Task.
        
        Args:
            story: Story dictionary
            
        Returns:
            Task object
        """
        # Extract fields
        story_id = story.get('id', '')
        name = story.get('name', 'Untitled')
        state = story.get('workflow_state_name') or story.get('workflow_state', {}).get('name', 'Open')
        
        # Project info
        project = story.get('project', {}).get('name') or story.get('group', {}).get('name', 'Unknown')
        
        # Dates
        updated = story.get('updated_at', '')
        if updated:
            updated = updated.split('T')[0]
        
        # URL
        url = story.get('app_url', '')
        
        # Description
        description = story.get('description', '')
        if description and len(description) > 500:
            description = description[:500]
        
        # Story type and estimate
        story_type = story.get('story_type', 'Story')
        estimate = story.get('estimate', 0)
        
        # Labels
        labels = [label.get('name', '') for label in story.get('labels', [])]
        labels_str = ', '.join(labels) if labels else 'None'
        
        # Build additional info
        additional_parts = [f"Type: {story_type}"]
        
        if estimate and estimate > 0:
            additional_parts.append(f"Estimate: {estimate} pts")
        
        if labels_str != 'None':
            additional_parts.append(f"Labels: {labels_str}")
        
        additional = " | ".join(additional_parts)
        
        return Task(
            company="sanctum",
            source=TaskSource.SHORTCUT,
            type=story_type,
            id=f"#{story_id}",
            title=name,
            status=state,
            repo=project,
            updated=updated,
            url=url,
            additional=additional,
            description=description,
            estimate=estimate,
            labels=labels,
        )
