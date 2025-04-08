"""
Browser Context Class for MCP Appium
===================================

This module provides the BrowserContext class for managing browser contexts using Playwright
through the MCP Appium framework.
"""

import base64
import logging
import os
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from playwright.async_api import BrowserContext as PlaywrightBrowserContext, Page as PlaywrightPage

if TYPE_CHECKING:
    from .browser import Browser
    from .page import Page

logger = logging.getLogger(__name__)

class BrowserContext:
    """
    BrowserContext class for managing browser contexts using Playwright.
    
    This class provides methods for:
    - Creating and managing pages
    - Handling cookies and storage
    - Configuring context settings
    """
    
    def __init__(self, 
                 playwright_context: PlaywrightBrowserContext, 
                 browser: 'Browser'):
        """
        Initialize a new BrowserContext instance.
        
        Args:
            playwright_context: The Playwright browser context
            browser: The parent Browser instance
        """
        self._playwright_context = playwright_context
        self._browser = browser
        self._pages = []
        self._current_page_index = -1
    
    async def new_page(self) -> Optional['Page']:
        """
        Create a new page in this context.
        
        Returns:
            Page: A new page, or None if an error occurred
        """
        from .page import Page
        
        try:
            # Create a new page
            playwright_page = await self._playwright_context.new_page()
            
            # Create our wrapper page
            page = Page(playwright_page, self)
            self._pages.append(page)
            
            # Set as current page
            self._current_page_index = len(self._pages) - 1
            
            logger.info("Created new page")
            return page
            
        except Exception as e:
            logger.error(f"Error creating page: {str(e)}")
            return None
    
    async def close(self) -> bool:
        """
        Close this browser context.
        
        Returns:
            bool: True if the context was closed successfully, False otherwise
        """
        try:
            # Close all pages (they will be automatically closed by Playwright when closing context,
            # but we need to clear our references)
            self._pages = []
            self._current_page_index = -1
            
            # Close the context
            await self._playwright_context.close()
            
            logger.info("Browser context closed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error closing browser context: {str(e)}")
            return False
    
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """
        Get all cookies for this context.
        
        Returns:
            List[Dict[str, Any]]: A list of cookies
        """
        try:
            return await self._playwright_context.cookies()
        except Exception as e:
            logger.error(f"Error getting cookies: {str(e)}")
            return []
    
    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> bool:
        """
        Set cookies for this context.
        
        Args:
            cookies: A list of cookies to set
            
        Returns:
            bool: True if the cookies were set successfully, False otherwise
        """
        try:
            await self._playwright_context.add_cookies(cookies)
            return True
        except Exception as e:
            logger.error(f"Error setting cookies: {str(e)}")
            return False
    
    async def clear_cookies(self) -> bool:
        """
        Clear all cookies for this context.
        
        Returns:
            bool: True if the cookies were cleared successfully, False otherwise
        """
        try:
            await self._playwright_context.clear_cookies()
            return True
        except Exception as e:
            logger.error(f"Error clearing cookies: {str(e)}")
            return False
    
    async def get_current_page(self) -> Optional['Page']:
        """
        Get the current page.
        
        Returns:
            Page: The current page, or None if there are no pages
        """
        if self._current_page_index < 0 or self._current_page_index >= len(self._pages):
            if len(self._pages) > 0:
                # Update to point to the first page if we have pages but index is invalid
                self._current_page_index = 0
                return self._pages[0]
            return None
        
        return self._pages[self._current_page_index]
    
    async def set_current_page(self, page_index: int) -> bool:
        """
        Set the current page by index.
        
        Args:
            page_index: The index of the page to set as current
            
        Returns:
            bool: True if the current page was set successfully, False otherwise
        """
        if page_index < 0 or page_index >= len(self._pages):
            logger.error(f"Invalid page index: {page_index}")
            return False
        
        self._current_page_index = page_index
        return True
    
    @property
    def pages(self) -> List['Page']:
        """
        Get all pages.
        
        Returns:
            List[Page]: A list of all pages
        """
        return self._pages
    
    @property
    def browser(self) -> 'Browser':
        """
        Get the parent browser.
        
        Returns:
            Browser: The parent browser
        """
        return self._browser
    
    @property
    def playwright_context(self) -> PlaywrightBrowserContext:
        """
        Get the Playwright browser context.
        
        Returns:
            PlaywrightBrowserContext: The Playwright browser context
        """
        return self._playwright_context