"""
MCP Appium Browser Client Adapter
================================

This module provides an adapter to integrate the Playwright-based browser automation
with the MCP Appium client API, allowing for a unified interface for both mobile
and web automation.
"""

import asyncio
import base64
import logging
import os
from typing import Dict, Any, Optional, List, Union

from ..client import AppiumClient
from ..models import Session
from ..errors import AppiumMCPError
from .browser import Browser
from .context import BrowserContext
from .page import Page

logger = logging.getLogger(__name__)

class BrowserAdapter:
    """
    Adapter for integrating the browser automation with the MCP Appium client API.
    
    This class provides methods for:
    - Bridging browser interactions with the MCP Appium API
    - Managing browser sessions
    - Translating between MCP commands and browser actions
    """
    
    def __init__(self, client: AppiumClient = None):
        """
        Initialize a new BrowserAdapter instance.
        
        Args:
            client: The MCP Appium client to adapt (optional)
        """
        self._client = client
        self._browser = None
        self._browser_context = None
        self._current_page = None
        self._event_loop = None
        self._is_connected = False
        self._session = None
    
    async def _initialize_browser(self) -> None:
        """Initialize the browser instance."""
        if not self._browser:
            self._browser = Browser()
    
    def _ensure_event_loop(self) -> None:
        """Ensure that we have an event loop."""
        try:
            self._event_loop = asyncio.get_event_loop()
        except RuntimeError:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
    
    def connect(self, browser_type: str = "chromium", headless: bool = True, **kwargs) -> bool:
        """
        Connect to a browser.
        
        Args:
            browser_type: The type of browser to connect to
            headless: Whether to run in headless mode
            **kwargs: Additional options to pass to the browser
            
        Returns:
            bool: True if the connection was successful, False otherwise
        """
        try:
            self._ensure_event_loop()
            
            # Initialize and launch the browser
            async def _connect():
                await self._initialize_browser()
                return await self._browser.launch(browser_type=browser_type, headless=headless, **kwargs)
            
            success = self._event_loop.run_until_complete(_connect())
            
            if success:
                self._is_connected = True
                logger.info(f"Connected to browser ({browser_type})")
                return True
            else:
                logger.error(f"Failed to connect to browser ({browser_type})")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to browser: {str(e)}")
            return False
    
    def create_session(self, capabilities: Dict[str, Any]) -> Optional[Session]:
        """
        Create a browser session with the specified capabilities.
        
        Args:
            capabilities: The browser capabilities
            
        Returns:
            Session: The created session, or None if creation failed
        """
        if not self._is_connected:
            logger.error("Browser is not connected")
            return None
        
        try:
            self._ensure_event_loop()
            
            # Create a browser context and page
            async def _create_session():
                browser_context_options = {}
                
                # Extract browser context options from capabilities
                if "viewport" in capabilities:
                    browser_context_options["viewport"] = capabilities["viewport"]
                if "user_agent" in capabilities:
                    browser_context_options["user_agent"] = capabilities["user_agent"]
                if "locale" in capabilities:
                    browser_context_options["locale"] = capabilities["locale"]
                if "timezone_id" in capabilities:
                    browser_context_options["timezone_id"] = capabilities["timezone_id"]
                if "geolocation" in capabilities:
                    browser_context_options["geolocation"] = capabilities["geolocation"]
                if "permissions" in capabilities:
                    browser_context_options["permissions"] = capabilities["permissions"]
                
                # Create a browser context
                self._browser_context = await self._browser.new_context(**browser_context_options)
                
                if not self._browser_context:
                    return None
                
                # Create a page
                self._current_page = await self._browser_context.new_page()
                
                if not self._current_page:
                    await self._browser_context.close()
                    self._browser_context = None
                    return None
                
                # Navigate to the initial URL if provided
                if "initial_url" in capabilities:
                    await self._current_page.goto(capabilities["initial_url"])
                
                return True
            
            success = self._event_loop.run_until_complete(_create_session())
            
            if not success:
                logger.error("Failed to create browser session")
                return None
            
            # Create a session object
            session_id = f"browser-{id(self._browser_context)}"
            self._session = Session(session_id, capabilities)
            
            logger.info(f"Created browser session with ID: {session_id}")
            return self._session
            
        except Exception as e:
            logger.error(f"Error creating browser session: {str(e)}")
            return None
    
    def quit(self) -> bool:
        """
        Quit the browser session.
        
        Returns:
            bool: True if the session was quit successfully, False otherwise
        """
        if not self._is_connected or not self._browser:
            logger.warning("Browser is not connected")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Close the browser
            async def _quit():
                result = await self._browser.close()
                self._browser = None
                self._browser_context = None
                self._current_page = None
                self._is_connected = False
                self._session = None
                return result
            
            success = self._event_loop.run_until_complete(_quit())
            
            if success:
                logger.info("Browser session quit successfully")
                return True
            else:
                logger.error("Failed to quit browser session")
                return False
                
        except Exception as e:
            logger.error(f"Error quitting browser session: {str(e)}")
            return False
    
    def find_element(self, by: str, value: str) -> Union[Dict[str, Any], None]:
        """
        Find an element in the browser.
        
        Args:
            by: The method to find the element (only 'css' or 'xpath' supported)
            value: The selector value
            
        Returns:
            Dict: Element representation if found, None otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return None
        
        try:
            self._ensure_event_loop()
            
            # Convert Appium locator strategy to CSS/XPath
            selector = value
            if by.lower() not in ['css selector', 'css', 'xpath']:
                logger.warning(f"Unsupported locator strategy '{by}' for browser. Using as CSS selector.")
            
            if by.lower() == 'xpath':
                # Keep xpath as is
                pass
            else:
                # Treat as CSS selector
                pass
            
            # Find the element
            async def _find_element():
                element = await self._current_page.find_element(selector)
                
                if not element:
                    return None
                
                # Return a representation of the element
                return {
                    "element_id": f"browser-element-{id(element)}",
                    "element": element,
                    "selector": selector
                }
            
            result = self._event_loop.run_until_complete(_find_element())
            
            if result:
                logger.info(f"Found element with selector: {selector}")
                return result
            else:
                logger.warning(f"Element not found with selector: {selector}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding element: {str(e)}")
            return None
    
    def find_elements(self, by: str, value: str) -> List[Dict[str, Any]]:
        """
        Find elements in the browser.
        
        Args:
            by: The method to find the elements (only 'css' or 'xpath' supported)
            value: The selector value
            
        Returns:
            List[Dict]: List of element representations
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return []
        
        try:
            self._ensure_event_loop()
            
            # Convert Appium locator strategy to CSS/XPath
            selector = value
            if by.lower() not in ['css selector', 'css', 'xpath']:
                logger.warning(f"Unsupported locator strategy '{by}' for browser. Using as CSS selector.")
            
            if by.lower() == 'xpath':
                # Keep xpath as is
                pass
            else:
                # Treat as CSS selector
                pass
            
            # Find the elements
            async def _find_elements():
                elements = await self._current_page.find_elements(selector)
                
                # Return representations of the elements
                result = []
                for element in elements:
                    result.append({
                        "element_id": f"browser-element-{id(element)}",
                        "element": element,
                        "selector": selector
                    })
                
                return result
            
            result = self._event_loop.run_until_complete(_find_elements())
            
            logger.info(f"Found {len(result)} elements with selector: {selector}")
            return result
                
        except Exception as e:
            logger.error(f"Error finding elements: {str(e)}")
            return []
    
    def get_page_source(self) -> str:
        """
        Get the HTML source of the current page.
        
        Returns:
            str: The HTML source
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return ""
        
        try:
            self._ensure_event_loop()
            
            # Get the page source
            async def _get_page_source():
                return await self._current_page.get_content()
            
            result = self._event_loop.run_until_complete(_get_page_source())
            
            logger.info(f"Got page source ({len(result)} characters)")
            return result
                
        except Exception as e:
            logger.error(f"Error getting page source: {str(e)}")
            return ""
    
    def get_screenshot(self) -> Optional[str]:
        """
        Take a screenshot of the current page.
        
        Returns:
            str: The screenshot as a base64-encoded string, or None if failed
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return None
        
        try:
            self._ensure_event_loop()
            
            # Take a screenshot
            async def _get_screenshot():
                return await self._current_page.get_screenshot(as_base64=True)
            
            result = self._event_loop.run_until_complete(_get_screenshot())
            
            if result:
                logger.info("Took screenshot of current page")
                return result
            else:
                logger.error("Failed to take screenshot")
                return None
                
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return None
    
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Navigate to the URL
            async def _navigate_to():
                return await self._current_page.goto(url)
            
            result = self._event_loop.run_until_complete(_navigate_to())
            
            if result:
                logger.info(f"Navigated to URL: {url}")
                return True
            else:
                logger.error(f"Failed to navigate to URL: {url}")
                return False
                
        except Exception as e:
            logger.error(f"Error navigating to URL: {str(e)}")
            return False
    
    def get_url(self) -> str:
        """
        Get the current URL.
        
        Returns:
            str: The current URL
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return ""
        
        try:
            self._ensure_event_loop()
            
            # Get the current URL
            async def _get_url():
                return await self._current_page.get_url()
            
            result = self._event_loop.run_until_complete(_get_url())
            
            logger.info(f"Current URL: {result}")
            return result
                
        except Exception as e:
            logger.error(f"Error getting current URL: {str(e)}")
            return ""
    
    def get_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            str: The page title
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return ""
        
        try:
            self._ensure_event_loop()
            
            # Get the page title
            async def _get_title():
                return await self._current_page.get_title()
            
            result = self._event_loop.run_until_complete(_get_title())
            
            logger.info(f"Page title: {result}")
            return result
                
        except Exception as e:
            logger.error(f"Error getting page title: {str(e)}")
            return ""
    
    def execute_script(self, script: str, args: List[Any] = None) -> Any:
        """
        Execute JavaScript in the browser.
        
        Args:
            script: The JavaScript to execute
            args: Arguments to pass to the script
            
        Returns:
            Any: The result of the script execution
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return None
        
        try:
            self._ensure_event_loop()
            
            # Prepare the arguments
            arg = args[0] if args and len(args) > 0 else None
            
            # Execute the script
            async def _execute_script():
                return await self._current_page.evaluate(script, arg)
            
            result = self._event_loop.run_until_complete(_execute_script())
            
            logger.info("Executed script in browser")
            return result
                
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            return None
    
    def create_new_tab(self) -> bool:
        """
        Create a new browser tab.
        
        Returns:
            bool: True if the tab was created successfully, False otherwise
        """
        if not self._is_connected or not self._browser_context:
            logger.error("Browser session not started")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Create a new page (tab)
            async def _create_new_tab():
                new_page = await self._browser_context.new_page()
                if new_page:
                    self._current_page = new_page
                    return True
                return False
            
            result = self._event_loop.run_until_complete(_create_new_tab())
            
            if result:
                logger.info("Created new browser tab")
                return True
            else:
                logger.error("Failed to create new browser tab")
                return False
                
        except Exception as e:
            logger.error(f"Error creating new tab: {str(e)}")
            return False
    
    def switch_to_tab(self, tab_index: int) -> bool:
        """
        Switch to a different browser tab.
        
        Args:
            tab_index: The index of the tab to switch to
            
        Returns:
            bool: True if the switch was successful, False otherwise
        """
        if not self._is_connected or not self._browser_context:
            logger.error("Browser session not started")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Switch to the specified tab
            async def _switch_to_tab():
                success = await self._browser_context.set_current_page(tab_index)
                if success:
                    self._current_page = await self._browser_context.get_current_page()
                    return True
                return False
            
            result = self._event_loop.run_until_complete(_switch_to_tab())
            
            if result:
                logger.info(f"Switched to tab {tab_index}")
                return True
            else:
                logger.error(f"Failed to switch to tab {tab_index}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching to tab: {str(e)}")
            return False
    
    def element_click(self, element_id: str) -> bool:
        """
        Click on an element.
        
        Args:
            element_id: The ID of the element to click
            
        Returns:
            bool: True if the click was successful, False otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return False
        
        # Extract the element from the element ID
        # Note: This is a naive implementation that won't work across method calls
        # since we need the actual element instance, not just an ID
        # In a real implementation, we would maintain a map of element IDs to element instances
        if not element_id.startswith("browser-element-"):
            logger.error(f"Invalid element ID: {element_id}")
            return False
        
        # For demonstration purposes, we'll just find the element again by selector
        # In a real implementation, we would maintain a map of element IDs to element instances
        element_data = self._element_map.get(element_id)
        if not element_data:
            logger.error(f"Element not found: {element_id}")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Click the element
            async def _element_click():
                element = element_data["element"]
                return await element.click()
            
            result = self._event_loop.run_until_complete(_element_click())
            
            if result:
                logger.info(f"Clicked on element: {element_id}")
                return True
            else:
                logger.error(f"Failed to click on element: {element_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error clicking on element: {str(e)}")
            return False
    
    def element_send_keys(self, element_id: str, text: str) -> bool:
        """
        Send keys to an element.
        
        Args:
            element_id: The ID of the element to send keys to
            text: The text to send
            
        Returns:
            bool: True if sending keys was successful, False otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return False
        
        # Extract the element from the element ID
        # Note: This is a naive implementation that won't work across method calls
        element_data = self._element_map.get(element_id)
        if not element_data:
            logger.error(f"Element not found: {element_id}")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Type text into the element
            async def _element_send_keys():
                element = element_data["element"]
                return await element.fill(text)
            
            result = self._event_loop.run_until_complete(_element_send_keys())
            
            if result:
                logger.info(f"Sent keys to element: {element_id}")
                return True
            else:
                logger.error(f"Failed to send keys to element: {element_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending keys to element: {str(e)}")
            return False
    
    def element_clear(self, element_id: str) -> bool:
        """
        Clear an element.
        
        Args:
            element_id: The ID of the element to clear
            
        Returns:
            bool: True if clearing was successful, False otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return False
        
        # Extract the element from the element ID
        element_data = self._element_map.get(element_id)
        if not element_data:
            logger.error(f"Element not found: {element_id}")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Clear the element
            async def _element_clear():
                element = element_data["element"]
                return await element.fill("")
            
            result = self._event_loop.run_until_complete(_element_clear())
            
            if result:
                logger.info(f"Cleared element: {element_id}")
                return True
            else:
                logger.error(f"Failed to clear element: {element_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing element: {str(e)}")
            return False
    
    def element_get_text(self, element_id: str) -> str:
        """
        Get the text of an element.
        
        Args:
            element_id: The ID of the element to get text from
            
        Returns:
            str: The element text
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return ""
        
        # Extract the element from the element ID
        element_data = self._element_map.get(element_id)
        if not element_data:
            logger.error(f"Element not found: {element_id}")
            return ""
        
        try:
            self._ensure_event_loop()
            
            # Get the element text
            async def _element_get_text():
                element = element_data["element"]
                return await element.get_text()
            
            result = self._event_loop.run_until_complete(_element_get_text())
            
            logger.info(f"Got text from element: {element_id}")
            return result
                
        except Exception as e:
            logger.error(f"Error getting text from element: {str(e)}")
            return ""
    
    def element_get_attribute(self, element_id: str, attribute: str) -> str:
        """
        Get an attribute of an element.
        
        Args:
            element_id: The ID of the element to get attribute from
            attribute: The attribute name
            
        Returns:
            str: The attribute value
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return ""
        
        # Extract the element from the element ID
        element_data = self._element_map.get(element_id)
        if not element_data:
            logger.error(f"Element not found: {element_id}")
            return ""
        
        try:
            self._ensure_event_loop()
            
            # Get the element attribute
            async def _element_get_attribute():
                element = element_data["element"]
                return await element.get_attribute(attribute)
            
            result = self._event_loop.run_until_complete(_element_get_attribute())
            
            logger.info(f"Got attribute '{attribute}' from element: {element_id}")
            return result or ""
                
        except Exception as e:
            logger.error(f"Error getting attribute from element: {str(e)}")
            return ""
    
    def back(self) -> bool:
        """
        Navigate back in the browser.
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Navigate back
            async def _back():
                return await self._current_page.back()
            
            result = self._event_loop.run_until_complete(_back())
            
            if result:
                logger.info("Navigated back in browser")
                return True
            else:
                logger.error("Failed to navigate back in browser")
                return False
                
        except Exception as e:
            logger.error(f"Error navigating back: {str(e)}")
            return False
    
    def forward(self) -> bool:
        """
        Navigate forward in the browser.
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Navigate forward
            async def _forward():
                return await self._current_page.forward()
            
            result = self._event_loop.run_until_complete(_forward())
            
            if result:
                logger.info("Navigated forward in browser")
                return True
            else:
                logger.error("Failed to navigate forward in browser")
                return False
                
        except Exception as e:
            logger.error(f"Error navigating forward: {str(e)}")
            return False
    
    def refresh(self) -> bool:
        """
        Refresh the current page.
        
        Returns:
            bool: True if refresh was successful, False otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return False
        
        try:
            self._ensure_event_loop()
            
            # Refresh the page
            async def _refresh():
                return await self._current_page.reload()
            
            result = self._event_loop.run_until_complete(_refresh())
            
            if result:
                logger.info("Refreshed current page")
                return True
            else:
                logger.error("Failed to refresh current page")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing page: {str(e)}")
            return False
    
    def wait_for_element(self, by: str, value: str, timeout: int = 30000) -> Union[Dict[str, Any], None]:
        """
        Wait for an element to be present.
        
        Args:
            by: The method to find the element (only 'css' or 'xpath' supported)
            value: The selector value
            timeout: The maximum time to wait in milliseconds
            
        Returns:
            Dict: Element representation if found, None otherwise
        """
        if not self._is_connected or not self._current_page:
            logger.error("Browser session not started")
            return None
        
        try:
            self._ensure_event_loop()
            
            # Convert Appium locator strategy to CSS/XPath
            selector = value
            if by.lower() not in ['css selector', 'css', 'xpath']:
                logger.warning(f"Unsupported locator strategy '{by}' for browser. Using as CSS selector.")
            
            if by.lower() == 'xpath':
                # Keep xpath as is
                pass
            else:
                # Treat as CSS selector
                pass
            
            # Wait for the element
            async def _wait_for_element():
                options = {"timeout": timeout}
                element = await self._current_page.wait_for_selector(selector, options)
                
                if not element:
                    return None
                
                # Return a representation of the element
                return {
                    "element_id": f"browser-element-{id(element)}",
                    "element": element,
                    "selector": selector
                }
            
            result = self._event_loop.run_until_complete(_wait_for_element())
            
            if result:
                logger.info(f"Found element after waiting with selector: {selector}")
                return result
            else:
                logger.warning(f"Element not found after waiting with selector: {selector}")
                return None
                
        except Exception as e:
            logger.error(f"Error waiting for element: {str(e)}")
            return None
    
    @property
    def session(self) -> Optional[Session]:
        """
        Get the current session.
        
        Returns:
            Session: The current session, or None if not connected
        """
        return self._session
    
    @property
    def _element_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the element map for storing element instances.
        
        Note: This is a naive implementation. In a real implementation, we would
        maintain a proper map of element IDs to element instances.
        
        Returns:
            Dict: The element map
        """
        # This should be properly maintained across method calls
        return {}