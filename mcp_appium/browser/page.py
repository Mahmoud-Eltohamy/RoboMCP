"""
Page Class for MCP Appium
========================

This module provides the Page class for interacting with browser pages using Playwright
through the MCP Appium framework.
"""

import base64
import logging
import os
from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING, Tuple

from playwright.async_api import Page as PlaywrightPage, Locator as PlaywrightLocator

if TYPE_CHECKING:
    from .context import BrowserContext
    from .element import WebElement

logger = logging.getLogger(__name__)

class Page:
    """
    Page class for interacting with browser pages using Playwright.
    
    This class provides methods for:
    - Navigation
    - Element finding and interaction
    - Page manipulation
    - Screenshots and content extraction
    """
    
    def __init__(self, playwright_page: PlaywrightPage, context: 'BrowserContext'):
        """
        Initialize a new Page instance.
        
        Args:
            playwright_page: The Playwright page
            context: The parent BrowserContext instance
        """
        self._playwright_page = playwright_page
        self._context = context
    
    async def goto(self, url: str, options: Dict[str, Any] = None) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            options: Additional options for navigation
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.goto(url, **options)
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    async def reload(self, options: Dict[str, Any] = None) -> bool:
        """
        Reload the current page.
        
        Args:
            options: Additional options for reloading
            
        Returns:
            bool: True if reload was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.reload(**options)
            return True
        except Exception as e:
            logger.error(f"Error reloading page: {str(e)}")
            return False
    
    async def back(self, options: Dict[str, Any] = None) -> bool:
        """
        Navigate back.
        
        Args:
            options: Additional options for navigation
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.go_back(**options)
            return True
        except Exception as e:
            logger.error(f"Error navigating back: {str(e)}")
            return False
    
    async def forward(self, options: Dict[str, Any] = None) -> bool:
        """
        Navigate forward.
        
        Args:
            options: Additional options for navigation
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.go_forward(**options)
            return True
        except Exception as e:
            logger.error(f"Error navigating forward: {str(e)}")
            return False
    
    async def get_url(self) -> str:
        """
        Get the current URL.
        
        Returns:
            str: The current URL
        """
        return self._playwright_page.url
    
    async def get_title(self) -> str:
        """
        Get the page title.
        
        Returns:
            str: The page title
        """
        return await self._playwright_page.title()
    
    async def find_element(self, selector: str) -> Optional['WebElement']:
        """
        Find an element on the page.
        
        Args:
            selector: The CSS selector for the element
            
        Returns:
            WebElement: The element, or None if not found
        """
        from .element import WebElement
        
        try:
            locator = self._playwright_page.locator(selector).first
            if await locator.count() == 0:
                logger.warning(f"Element not found with selector: {selector}")
                return None
                
            return WebElement(locator, self)
        except Exception as e:
            logger.error(f"Error finding element with selector {selector}: {str(e)}")
            return None
    
    async def find_elements(self, selector: str) -> List['WebElement']:
        """
        Find elements on the page.
        
        Args:
            selector: The CSS selector for the elements
            
        Returns:
            List[WebElement]: A list of elements, or an empty list if none found
        """
        from .element import WebElement
        
        try:
            locator = self._playwright_page.locator(selector)
            count = await locator.count()
            
            elements = []
            for i in range(count):
                elements.append(WebElement(locator.nth(i), self))
                
            return elements
        except Exception as e:
            logger.error(f"Error finding elements with selector {selector}: {str(e)}")
            return []
    
    async def query_selector(self, selector: str) -> Optional['WebElement']:
        """
        Find an element on the page using querySelector.
        
        Args:
            selector: The CSS selector for the element
            
        Returns:
            WebElement: The element, or None if not found
        """
        return await self.find_element(selector)
    
    async def query_selector_all(self, selector: str) -> List['WebElement']:
        """
        Find elements on the page using querySelectorAll.
        
        Args:
            selector: The CSS selector for the elements
            
        Returns:
            List[WebElement]: A list of elements, or an empty list if none found
        """
        return await self.find_elements(selector)
    
    async def wait_for_selector(self, selector: str, options: Dict[str, Any] = None) -> Optional['WebElement']:
        """
        Wait for an element to appear on the page.
        
        Args:
            selector: The CSS selector for the element
            options: Additional options for waiting
            
        Returns:
            WebElement: The element, or None if not found
        """
        from .element import WebElement
        
        try:
            options = options or {}
            locator = self._playwright_page.locator(selector).first
            await locator.wait_for(**options)
            
            if await locator.count() == 0:
                logger.warning(f"Element not found after waiting with selector: {selector}")
                return None
                
            return WebElement(locator, self)
        except Exception as e:
            logger.error(f"Error waiting for element with selector {selector}: {str(e)}")
            return None
    
    async def wait_for_navigation(self, options: Dict[str, Any] = None) -> bool:
        """
        Wait for navigation to complete.
        
        Args:
            options: Additional options for waiting
            
        Returns:
            bool: True if navigation completed, False if timeout or error
        """
        try:
            options = options or {}
            await self._playwright_page.wait_for_navigation(**options)
            return True
        except Exception as e:
            logger.error(f"Error waiting for navigation: {str(e)}")
            return False
    
    async def wait_for_load_state(self, state: str = "load", options: Dict[str, Any] = None) -> bool:
        """
        Wait for the page to reach a specific load state.
        
        Args:
            state: The load state to wait for ('load', 'domcontentloaded', 'networkidle')
            options: Additional options for waiting
            
        Returns:
            bool: True if the load state was reached, False if timeout or error
        """
        try:
            options = options or {}
            await self._playwright_page.wait_for_load_state(state, **options)
            return True
        except Exception as e:
            logger.error(f"Error waiting for load state {state}: {str(e)}")
            return False
    
    async def evaluate(self, expression: str, arg: Any = None) -> Any:
        """
        Evaluate JavaScript in the page.
        
        Args:
            expression: The JavaScript expression to evaluate
            arg: The argument to pass to the expression
            
        Returns:
            Any: The result of the evaluation
        """
        try:
            if arg is not None:
                return await self._playwright_page.evaluate(expression, arg)
            else:
                return await self._playwright_page.evaluate(expression)
        except Exception as e:
            logger.error(f"Error evaluating expression {expression}: {str(e)}")
            return None
    
    async def get_content(self) -> str:
        """
        Get the HTML content of the page.
        
        Returns:
            str: The HTML content
        """
        try:
            return await self._playwright_page.content()
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            return ""
    
    async def get_screenshot(self, 
                            path: Optional[str] = None, 
                            full_page: bool = False,
                            as_base64: bool = False) -> Optional[Union[bool, str]]:
        """
        Take a screenshot of the page.
        
        Args:
            path: The path to save the screenshot to, or None to return as base64
            full_page: Whether to take a screenshot of the full page
            as_base64: Whether to return the screenshot as a base64 string
            
        Returns:
            If path is provided and as_base64 is False: 
                bool: True if the screenshot was saved successfully, False otherwise
            If path is not provided or as_base64 is True: 
                str: The screenshot as a base64 string, or None if an error occurred
        """
        try:
            options = {"full_page": full_page}
            
            if path:
                # Save screenshot to file
                await self._playwright_page.screenshot(path=path, **options)
                return True if not as_base64 else None
            else:
                # Return screenshot as buffer
                screenshot_buffer = await self._playwright_page.screenshot(**options)
                if as_base64:
                    return base64.b64encode(screenshot_buffer).decode('utf-8')
                
                return screenshot_buffer
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return None
    
    async def click(self, selector: str, options: Dict[str, Any] = None) -> bool:
        """
        Click on an element.
        
        Args:
            selector: The CSS selector for the element
            options: Additional options for clicking
            
        Returns:
            bool: True if the click was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.click(selector, **options)
            return True
        except Exception as e:
            logger.error(f"Error clicking on element with selector {selector}: {str(e)}")
            return False
    
    async def type(self, selector: str, text: str, options: Dict[str, Any] = None) -> bool:
        """
        Type text into an element.
        
        Args:
            selector: The CSS selector for the element
            text: The text to type
            options: Additional options for typing
            
        Returns:
            bool: True if typing was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.type(selector, text, **options)
            return True
        except Exception as e:
            logger.error(f"Error typing into element with selector {selector}: {str(e)}")
            return False
    
    async def fill(self, selector: str, value: str, options: Dict[str, Any] = None) -> bool:
        """
        Fill a form field.
        
        Args:
            selector: The CSS selector for the element
            value: The value to fill
            options: Additional options for filling
            
        Returns:
            bool: True if filling was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.fill(selector, value, **options)
            return True
        except Exception as e:
            logger.error(f"Error filling element with selector {selector}: {str(e)}")
            return False
    
    async def select_option(self, 
                            selector: str, 
                            value: Optional[Union[str, List[str]]] = None,
                            index: Optional[Union[int, List[int]]] = None,
                            label: Optional[Union[str, List[str]]] = None,
                            options: Dict[str, Any] = None) -> List[str]:
        """
        Select options in a select element.
        
        Args:
            selector: The CSS selector for the element
            value: The values to select
            index: The indices to select
            label: The labels to select
            options: Additional options for selection
            
        Returns:
            List[str]: The selected option values
        """
        try:
            options = options or {}
            select_options = {}
            
            if value is not None:
                select_options["value"] = value
            if index is not None:
                select_options["index"] = index
            if label is not None:
                select_options["label"] = label
                
            return await self._playwright_page.select_option(selector, **select_options, **options)
        except Exception as e:
            logger.error(f"Error selecting options in element with selector {selector}: {str(e)}")
            return []
    
    async def check(self, selector: str, options: Dict[str, Any] = None) -> bool:
        """
        Check a checkbox or radio button.
        
        Args:
            selector: The CSS selector for the element
            options: Additional options for checking
            
        Returns:
            bool: True if checking was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.check(selector, **options)
            return True
        except Exception as e:
            logger.error(f"Error checking element with selector {selector}: {str(e)}")
            return False
    
    async def uncheck(self, selector: str, options: Dict[str, Any] = None) -> bool:
        """
        Uncheck a checkbox.
        
        Args:
            selector: The CSS selector for the element
            options: Additional options for unchecking
            
        Returns:
            bool: True if unchecking was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.uncheck(selector, **options)
            return True
        except Exception as e:
            logger.error(f"Error unchecking element with selector {selector}: {str(e)}")
            return False
    
    async def press(self, key: str, options: Dict[str, Any] = None) -> bool:
        """
        Press a key.
        
        Args:
            key: The key to press
            options: Additional options for pressing
            
        Returns:
            bool: True if the key press was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_page.keyboard.press(key, **options)
            return True
        except Exception as e:
            logger.error(f"Error pressing key {key}: {str(e)}")
            return False
    
    async def get_viewport_size(self) -> Dict[str, int]:
        """
        Get the viewport size.
        
        Returns:
            Dict[str, int]: The viewport size as a dictionary with 'width' and 'height' keys
        """
        try:
            return self._playwright_page.viewport_size
        except Exception as e:
            logger.error(f"Error getting viewport size: {str(e)}")
            return {"width": 0, "height": 0}
    
    async def set_viewport_size(self, width: int, height: int) -> bool:
        """
        Set the viewport size.
        
        Args:
            width: The viewport width
            height: The viewport height
            
        Returns:
            bool: True if the viewport size was set successfully, False otherwise
        """
        try:
            await self._playwright_page.set_viewport_size({"width": width, "height": height})
            return True
        except Exception as e:
            logger.error(f"Error setting viewport size to {width}x{height}: {str(e)}")
            return False
    
    @property
    def context(self) -> 'BrowserContext':
        """
        Get the parent browser context.
        
        Returns:
            BrowserContext: The parent browser context
        """
        return self._context
    
    @property
    def playwright_page(self) -> PlaywrightPage:
        """
        Get the Playwright page.
        
        Returns:
            PlaywrightPage: The Playwright page
        """
        return self._playwright_page