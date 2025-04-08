"""
Browser Class for MCP Appium
===========================

This module provides the Browser class for interacting with web browsers using Playwright
through the MCP Appium framework.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List

from playwright.async_api import async_playwright, Browser as PlaywrightBrowser, BrowserType
from .context import BrowserContext

logger = logging.getLogger(__name__)

class Browser:
    """
    Browser class for managing browser instances using Playwright.
    
    This class provides methods for:
    - Creating and managing browser instances
    - Creating browser contexts
    - Configuring browser settings
    """
    
    def __init__(self):
        """Initialize a new Browser instance."""
        self._playwright = None
        self._browser_instance = None
        self._browser_type = None
        self._is_connected = False
        self._contexts = []
        self._loop = None
    
    async def launch(self, 
                     browser_type: str = "chromium", 
                     headless: bool = True,
                     **kwargs) -> bool:
        """
        Launch a browser instance.
        
        Args:
            browser_type: The type of browser to launch ('chromium', 'firefox', or 'webkit')
            headless: Whether to launch the browser in headless mode
            **kwargs: Additional arguments to pass to the browser.launch() method
            
        Returns:
            bool: True if the browser was launched successfully, False otherwise
        """
        if self._is_connected:
            logger.warning("Browser is already connected. Close it first.")
            return False
            
        try:
            # Create or get event loop
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            
            # Start playwright
            self._playwright = await async_playwright().start()
            
            # Get the browser type
            if browser_type == "chromium":
                self._browser_type = self._playwright.chromium
            elif browser_type == "firefox":
                self._browser_type = self._playwright.firefox
            elif browser_type == "webkit":
                self._browser_type = self._playwright.webkit
            else:
                logger.error(f"Unsupported browser type: {browser_type}")
                await self._playwright.stop()
                return False
            
            # Launch the browser
            launch_options = {"headless": headless}
            launch_options.update(kwargs)
            
            self._browser_instance = await self._browser_type.launch(**launch_options)
            self._is_connected = True
            
            logger.info(f"Browser ({browser_type}) launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error launching browser: {str(e)}")
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            return False
    
    async def connect(self, browser_ws_endpoint: str, **kwargs) -> bool:
        """
        Connect to an existing browser instance.
        
        Args:
            browser_ws_endpoint: The WebSocket endpoint of the browser to connect to
            **kwargs: Additional arguments to pass to the browser.connect() method
            
        Returns:
            bool: True if the connection was successful, False otherwise
        """
        if self._is_connected:
            logger.warning("Browser is already connected. Close it first.")
            return False
            
        try:
            # Create or get event loop
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            
            # Start playwright
            self._playwright = await async_playwright().start()
            
            # Connect to the browser
            connect_options = {}
            connect_options.update(kwargs)
            
            self._browser_instance = await self._playwright.chromium.connect_over_cdp(
                browser_ws_endpoint, **connect_options
            )
            self._browser_type = self._playwright.chromium
            self._is_connected = True
            
            logger.info(f"Connected to browser at {browser_ws_endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to browser: {str(e)}")
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            return False
    
    async def new_context(self, **kwargs) -> Optional[BrowserContext]:
        """
        Create a new browser context.
        
        Args:
            **kwargs: Arguments to pass to the browser.new_context() method
            
        Returns:
            BrowserContext: A new browser context, or None if an error occurred
        """
        if not self._is_connected:
            logger.error("Browser is not connected")
            return None
            
        try:
            # Create a new browser context
            playwright_context = await self._browser_instance.new_context(**kwargs)
            
            # Create our wrapper context
            context = BrowserContext(playwright_context, self)
            self._contexts.append(context)
            
            logger.info("Created new browser context")
            return context
            
        except Exception as e:
            logger.error(f"Error creating browser context: {str(e)}")
            return None
    
    async def close(self) -> bool:
        """
        Close the browser instance.
        
        Returns:
            bool: True if the browser was closed successfully, False otherwise
        """
        if not self._is_connected:
            logger.warning("Browser is not connected")
            return False
            
        try:
            # Close all contexts
            for context in self._contexts:
                await context.close()
            self._contexts = []
            
            # Close the browser
            await self._browser_instance.close()
            
            # Stop playwright
            await self._playwright.stop()
            
            self._browser_instance = None
            self._browser_type = None
            self._playwright = None
            self._is_connected = False
            
            logger.info("Browser closed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """
        Check if the browser is connected.
        
        Returns:
            bool: True if the browser is connected, False otherwise
        """
        return self._is_connected
    
    @property
    def contexts(self) -> List[BrowserContext]:
        """
        Get all browser contexts.
        
        Returns:
            List[BrowserContext]: A list of all browser contexts
        """
        return self._contexts
    
    @property
    def browser_instance(self) -> Optional[PlaywrightBrowser]:
        """
        Get the Playwright browser instance.
        
        Returns:
            PlaywrightBrowser: The Playwright browser instance, or None if not connected
        """
        return self._browser_instance