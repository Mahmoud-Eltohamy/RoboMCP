"""
WebElement Class for MCP Appium
==============================

This module provides the WebElement class for interacting with web elements using Playwright
through the MCP Appium framework.
"""

import base64
import logging
import os
from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING, Tuple

from playwright.async_api import Locator as PlaywrightLocator

if TYPE_CHECKING:
    from .page import Page

logger = logging.getLogger(__name__)

class WebElement:
    """
    WebElement class for interacting with web elements using Playwright.
    
    This class provides methods for:
    - Element interaction (click, type, etc.)
    - Property and attribute access
    - State querying
    - Element finding within the element
    """
    
    def __init__(self, playwright_locator: PlaywrightLocator, page: 'Page'):
        """
        Initialize a new WebElement instance.
        
        Args:
            playwright_locator: The Playwright locator
            page: The parent Page instance
        """
        self._playwright_locator = playwright_locator
        self._page = page
    
    async def click(self, options: Dict[str, Any] = None) -> bool:
        """
        Click on the element.
        
        Args:
            options: Additional options for clicking
            
        Returns:
            bool: True if the click was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_locator.click(**options)
            return True
        except Exception as e:
            logger.error(f"Error clicking on element: {str(e)}")
            return False
    
    async def type(self, text: str, options: Dict[str, Any] = None) -> bool:
        """
        Type text into the element.
        
        Args:
            text: The text to type
            options: Additional options for typing
            
        Returns:
            bool: True if typing was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_locator.type(text, **options)
            return True
        except Exception as e:
            logger.error(f"Error typing into element: {str(e)}")
            return False
    
    async def fill(self, value: str, options: Dict[str, Any] = None) -> bool:
        """
        Fill the element with a value.
        
        Args:
            value: The value to fill
            options: Additional options for filling
            
        Returns:
            bool: True if filling was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_locator.fill(value, **options)
            return True
        except Exception as e:
            logger.error(f"Error filling element: {str(e)}")
            return False
    
    async def get_text(self) -> str:
        """
        Get the text content of the element.
        
        Returns:
            str: The text content
        """
        try:
            return await self._playwright_locator.text_content() or ""
        except Exception as e:
            logger.error(f"Error getting element text: {str(e)}")
            return ""
    
    async def get_attribute(self, name: str) -> Optional[str]:
        """
        Get an attribute of the element.
        
        Args:
            name: The attribute name
            
        Returns:
            str: The attribute value, or None if not found
        """
        try:
            return await self._playwright_locator.get_attribute(name)
        except Exception as e:
            logger.error(f"Error getting element attribute {name}: {str(e)}")
            return None
    
    async def get_property(self, name: str) -> Any:
        """
        Get a property of the element.
        
        Args:
            name: The property name
            
        Returns:
            Any: The property value
        """
        try:
            return await self._playwright_locator.evaluate(f"element => element.{name}")
        except Exception as e:
            logger.error(f"Error getting element property {name}: {str(e)}")
            return None
    
    async def get_value(self) -> str:
        """
        Get the value of the element.
        
        Returns:
            str: The value
        """
        try:
            return await self._playwright_locator.input_value()
        except Exception as e:
            logger.error(f"Error getting element value: {str(e)}")
            return ""
    
    async def check(self, options: Dict[str, Any] = None) -> bool:
        """
        Check the element (checkbox or radio).
        
        Args:
            options: Additional options for checking
            
        Returns:
            bool: True if checking was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_locator.check(**options)
            return True
        except Exception as e:
            logger.error(f"Error checking element: {str(e)}")
            return False
    
    async def uncheck(self, options: Dict[str, Any] = None) -> bool:
        """
        Uncheck the element (checkbox).
        
        Args:
            options: Additional options for unchecking
            
        Returns:
            bool: True if unchecking was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_locator.uncheck(**options)
            return True
        except Exception as e:
            logger.error(f"Error unchecking element: {str(e)}")
            return False
    
    async def is_checked(self) -> bool:
        """
        Check if the element is checked.
        
        Returns:
            bool: True if the element is checked, False otherwise
        """
        try:
            return await self._playwright_locator.is_checked()
        except Exception as e:
            logger.error(f"Error checking if element is checked: {str(e)}")
            return False
    
    async def is_disabled(self) -> bool:
        """
        Check if the element is disabled.
        
        Returns:
            bool: True if the element is disabled, False otherwise
        """
        try:
            return await self._playwright_locator.is_disabled()
        except Exception as e:
            logger.error(f"Error checking if element is disabled: {str(e)}")
            return False
    
    async def is_editable(self) -> bool:
        """
        Check if the element is editable.
        
        Returns:
            bool: True if the element is editable, False otherwise
        """
        try:
            return await self._playwright_locator.is_editable()
        except Exception as e:
            logger.error(f"Error checking if element is editable: {str(e)}")
            return False
    
    async def is_enabled(self) -> bool:
        """
        Check if the element is enabled.
        
        Returns:
            bool: True if the element is enabled, False otherwise
        """
        try:
            return await self._playwright_locator.is_enabled()
        except Exception as e:
            logger.error(f"Error checking if element is enabled: {str(e)}")
            return False
    
    async def is_visible(self) -> bool:
        """
        Check if the element is visible.
        
        Returns:
            bool: True if the element is visible, False otherwise
        """
        try:
            return await self._playwright_locator.is_visible()
        except Exception as e:
            logger.error(f"Error checking if element is visible: {str(e)}")
            return False
    
    async def find_element(self, selector: str) -> Optional['WebElement']:
        """
        Find an element within this element.
        
        Args:
            selector: The CSS selector for the element
            
        Returns:
            WebElement: The element, or None if not found
        """
        try:
            locator = self._playwright_locator.locator(selector).first
            if await locator.count() == 0:
                logger.warning(f"Element not found with selector: {selector}")
                return None
                
            return WebElement(locator, self._page)
        except Exception as e:
            logger.error(f"Error finding element with selector {selector}: {str(e)}")
            return None
    
    async def find_elements(self, selector: str) -> List['WebElement']:
        """
        Find elements within this element.
        
        Args:
            selector: The CSS selector for the elements
            
        Returns:
            List[WebElement]: A list of elements, or an empty list if none found
        """
        try:
            locator = self._playwright_locator.locator(selector)
            count = await locator.count()
            
            elements = []
            for i in range(count):
                elements.append(WebElement(locator.nth(i), self._page))
                
            return elements
        except Exception as e:
            logger.error(f"Error finding elements with selector {selector}: {str(e)}")
            return []
    
    async def get_screenshot(self, 
                            path: Optional[str] = None, 
                            as_base64: bool = False) -> Optional[Union[bool, str]]:
        """
        Take a screenshot of the element.
        
        Args:
            path: The path to save the screenshot to, or None to return as base64
            as_base64: Whether to return the screenshot as a base64 string
            
        Returns:
            If path is provided and as_base64 is False: 
                bool: True if the screenshot was saved successfully, False otherwise
            If path is not provided or as_base64 is True: 
                str: The screenshot as a base64 string, or None if an error occurred
        """
        try:
            if path:
                # Save screenshot to file
                await self._playwright_locator.screenshot(path=path)
                return True if not as_base64 else None
            else:
                # Return screenshot as buffer
                screenshot_buffer = await self._playwright_locator.screenshot()
                if as_base64:
                    return base64.b64encode(screenshot_buffer).decode('utf-8')
                
                return screenshot_buffer
        except Exception as e:
            logger.error(f"Error taking screenshot of element: {str(e)}")
            return None
    
    async def get_bounding_box(self) -> Dict[str, float]:
        """
        Get the bounding box of the element.
        
        Returns:
            Dict[str, float]: The bounding box as a dictionary with 'x', 'y', 'width', and 'height' keys
        """
        try:
            box = await self._playwright_locator.bounding_box()
            if box:
                return box
            else:
                return {"x": 0, "y": 0, "width": 0, "height": 0}
        except Exception as e:
            logger.error(f"Error getting element bounding box: {str(e)}")
            return {"x": 0, "y": 0, "width": 0, "height": 0}
    
    async def wait_for(self, state: str = "visible", options: Dict[str, Any] = None) -> bool:
        """
        Wait for the element to reach a specific state.
        
        Args:
            state: The state to wait for ('attached', 'detached', 'visible', 'hidden')
            options: Additional options for waiting
            
        Returns:
            bool: True if the state was reached, False if timeout or error
        """
        try:
            options = options or {}
            await self._playwright_locator.wait_for(state=state, **options)
            return True
        except Exception as e:
            logger.error(f"Error waiting for element state {state}: {str(e)}")
            return False
    
    async def hover(self, options: Dict[str, Any] = None) -> bool:
        """
        Hover over the element.
        
        Args:
            options: Additional options for hovering
            
        Returns:
            bool: True if hovering was successful, False otherwise
        """
        try:
            options = options or {}
            await self._playwright_locator.hover(**options)
            return True
        except Exception as e:
            logger.error(f"Error hovering over element: {str(e)}")
            return False
    
    async def select_option(self, 
                           value: Optional[Union[str, List[str]]] = None,
                           index: Optional[Union[int, List[int]]] = None,
                           label: Optional[Union[str, List[str]]] = None,
                           options: Dict[str, Any] = None) -> List[str]:
        """
        Select options in a select element.
        
        Args:
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
                
            return await self._playwright_locator.select_option(**select_options, **options)
        except Exception as e:
            logger.error(f"Error selecting options in element: {str(e)}")
            return []
    
    async def dispatch_event(self, type: str, event_init: Dict[str, Any] = None) -> bool:
        """
        Dispatch an event on the element.
        
        Args:
            type: The event type
            event_init: The event initialization properties
            
        Returns:
            bool: True if the event was dispatched successfully, False otherwise
        """
        try:
            event_init = event_init or {}
            await self._playwright_locator.dispatch_event(type, event_init)
            return True
        except Exception as e:
            logger.error(f"Error dispatching event {type} on element: {str(e)}")
            return False
    
    @property
    def page(self) -> 'Page':
        """
        Get the parent page.
        
        Returns:
            Page: The parent page
        """
        return self._page
    
    @property
    def playwright_locator(self) -> PlaywrightLocator:
        """
        Get the Playwright locator.
        
        Returns:
            PlaywrightLocator: The Playwright locator
        """
        return self._playwright_locator