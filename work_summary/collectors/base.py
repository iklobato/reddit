"""
Base collector class for all data sources.

Provides common functionality for API calls, error handling, and retry logic.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from work_summary.models import Task, WorkSummary
from work_summary.utils.http import HTTPClient
from work_summary.utils.cache import FileCache


logger = logging.getLogger(__name__)


class CollectorError(Exception):
    """Base exception for collector errors."""
    pass


class APIError(CollectorError):
    """API request error."""
    pass


class AuthenticationError(CollectorError):
    """Authentication error."""
    pass


class BaseCollector(ABC):
    """
    Base class for all collectors.
    
    Provides common functionality:
    - HTTP client management
    - Error handling
    - Retry logic
    - Rate limiting
    - Logging
    - Optional caching
    """
    
    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        cache: Optional[FileCache] = None,
        enabled: bool = True,
    ):
        """
        Initialize collector.
        
        Args:
            http_client: HTTP client instance
            cache: Cache instance
            enabled: Whether collector is enabled
        """
        self.http_client = http_client
        self.cache = cache
        self.enabled = enabled
        self._session_started = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self) -> None:
        """Start collector (initialize HTTP client if needed)."""
        if self.http_client is None:
            self.http_client = HTTPClient()
            await self.http_client.start()
            self._session_started = True
    
    async def close(self) -> None:
        """Close collector (close HTTP client if we started it)."""
        if self._session_started and self.http_client is not None:
            await self.http_client.close()
            self._session_started = False
    
    @abstractmethod
    async def collect(self) -> List[Task]:
        """
        Collect tasks from the source.
        
        Returns:
            List of tasks
            
        Raises:
            CollectorError: If collection fails
        """
        pass
    
    def _handle_api_error(self, error: Exception, context: str = "") -> None:
        """
        Handle API errors with logging.
        
        Args:
            error: The exception that occurred
            context: Additional context for the error
            
        Raises:
            APIError: Wrapped error with context
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        logger.error(error_msg)
        raise APIError(error_msg) from error
    
    def _handle_auth_error(self, context: str = "") -> None:
        """
        Handle authentication errors.
        
        Args:
            context: Additional context for the error
            
        Raises:
            AuthenticationError: With context
        """
        error_msg = f"Authentication failed{': ' + context if context else ''}"
        logger.error(error_msg)
        raise AuthenticationError(error_msg)
    
    async def _retry_operation(
        self,
        operation,
        max_retries: int = 3,
        delay: float = 1.0,
        context: str = ""
    ) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Async function to retry
            max_retries: Maximum number of retries
            delay: Initial delay between retries
            context: Context for error messages
            
        Returns:
            Result of the operation
            
        Raises:
            CollectorError: If all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"{context} failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                
                if attempt < max_retries - 1:
                    retry_delay = delay * (2 ** attempt)
                    await asyncio.sleep(retry_delay)
        
        self._handle_api_error(last_exception, context)
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if self.cache is None:
            return None
        
        return self.cache.get(key)
    
    def _set_in_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds
        """
        if self.cache is not None:
            self.cache.set(key, value, ttl=ttl)
    
    @property
    def name(self) -> str:
        """Get collector name."""
        return self.__class__.__name__.replace('Collector', '')
    
    def log_progress(self, message: str) -> None:
        """
        Log progress message.
        
        Args:
            message: Progress message
        """
        logger.info(f"[{self.name}] {message}")
    
    def log_debug(self, message: str) -> None:
        """
        Log debug message.
        
        Args:
            message: Debug message
        """
        logger.debug(f"[{self.name}] {message}")
    
    def log_error(self, message: str) -> None:
        """
        Log error message.
        
        Args:
            message: Error message
        """
        logger.error(f"[{self.name}] {message}")
