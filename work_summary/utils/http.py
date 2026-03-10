"""
HTTP utilities for making API requests.

Provides a shared HTTP client with connection pooling, retry logic,
and rate limiting support.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError


logger = logging.getLogger(__name__)


class HTTPClient:
    """
    Async HTTP client with retry logic and rate limiting.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize HTTP client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            rate_limit_delay: Delay between requests for rate limiting
        """
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self._session: Optional[ClientSession] = None
        self._last_request_time = 0.0
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self) -> None:
        """Start the HTTP session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session is not None:
            await self._session.close()
            self._session = None
    
    async def _rate_limit(self) -> None:
        """Apply rate limiting delay."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def _retry_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments for the request
            
        Returns:
            Response object
            
        Raises:
            ClientError: If all retries fail
        """
        if self._session is None:
            await self.start()
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                await self._rate_limit()
                
                logger.debug(f"Request {method} {url} (attempt {attempt + 1}/{self.max_retries})")
                
                async with self._session.request(method, url, **kwargs) as response:
                    # Raise for HTTP errors
                    response.raise_for_status()
                    return response
                    
            except ClientError as e:
                last_exception = e
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.debug(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed for {method} {url}")
        
        raise last_exception
    
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make GET request.
        
        Args:
            url: Request URL
            headers: Request headers
            params: Query parameters
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return await self._retry_request('GET', url, headers=headers, params=params, **kwargs)
    
    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make POST request.
        
        Args:
            url: Request URL
            headers: Request headers
            json: JSON data
            data: Form data
            **kwargs: Additional arguments
            
        Returns:
            Response object
        """
        return await self._retry_request('POST', url, headers=headers, json=json, data=data, **kwargs)
    
    async def get_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make GET request and return JSON response.
        
        Args:
            url: Request URL
            headers: Request headers
            params: Query parameters
            **kwargs: Additional arguments
            
        Returns:
            JSON response as dictionary
        """
        response = await self.get(url, headers=headers, params=params, **kwargs)
        return await response.json()
    
    async def post_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make POST request and return JSON response.
        
        Args:
            url: Request URL
            headers: Request headers
            json: JSON data
            **kwargs: Additional arguments
            
        Returns:
            JSON response as dictionary
        """
        response = await self.post(url, headers=headers, json=json, **kwargs)
        return await response.json()


def with_retry(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator for adding retry logic to functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (exponential backoff)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        retry_delay = delay * (2 ** attempt)
                        await asyncio.sleep(retry_delay)
            
            raise last_exception
        
        return wrapper
    return decorator


# Global HTTP client instance
_global_http_client: Optional[HTTPClient] = None


async def get_http_client() -> HTTPClient:
    """Get the global HTTP client instance."""
    global _global_http_client
    if _global_http_client is None:
        _global_http_client = HTTPClient()
        await _global_http_client.start()
    return _global_http_client


async def close_http_client() -> None:
    """Close the global HTTP client instance."""
    global _global_http_client
    if _global_http_client is not None:
        await _global_http_client.close()
        _global_http_client = None
