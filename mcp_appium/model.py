"""
Model module implements the AppiumModel class for element representation.

This module implements the Model component of the Model Context Protocol for Appium,
providing a way to represent and interact with elements in a mobile application.
"""

import logging
from typing import Dict, Any, List, Optional, Union

from mcp_appium.commands import By
from mcp_appium.context import AppiumContext
from mcp_appium.exceptions import ElementNotFoundError, InvalidArgumentError

logger = logging.getLogger(__name__)

class AppiumModel:
    """
    Model class for representing and interacting with UI elements.
    
    The AppiumModel class represents an element in a mobile application and
    provides methods to interact with it. Models are bound to a context
    and use that context to execute commands.
    """
    
    def __init__(self, context: AppiumContext, by: Union[str, By], value: str, name: str = None):
        """
        Initialize an Appium model.
        
        Args:
            context: AppiumContext for command execution
            by: Locator strategy (can be string or By enum)
            value: Locator value
            name: Optional friendly name for the element
        """
        self.context = context
        self.by = by if isinstance(by, str) else by.value
        self.value = value
        self.name = name or f"{self.by}={self.value}"
        self.element_id = None
        
        logger.debug(f"Initialized AppiumModel '{self.name}' with {self.by}='{self.value}'")
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"AppiumModel(name='{self.name}', by='{self.by}', value='{self.value}')"
    
    def locate(self) -> bool:
        """
        Locate the element in the current context.
        
        Returns:
            True if element is found, False otherwise
        """
        try:
            self.element_id = self.context.find_element(self.by, self.value)
            return True
        except ElementNotFoundError:
            self.element_id = None
            return False
    
    def assert_located(self) -> None:
        """
        Assert that the element is located, finding it if necessary.
        
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        if not self.element_id and not self.locate():
            raise ElementNotFoundError(f"Element '{self.name}' not found with {self.by}='{self.value}'")
    
    def click(self) -> 'AppiumModel':
        """
        Click on the element.
        
        Returns:
            Self for method chaining
            
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        logger.info(f"Clicking on element '{self.name}'")
        self.assert_located()
        self.context.click_element(self.element_id)
        return self
    
    def send_keys(self, text: str) -> 'AppiumModel':
        """
        Send keys to the element.
        
        Args:
            text: Text to send
            
        Returns:
            Self for method chaining
            
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        logger.info(f"Sending keys '{text}' to element '{self.name}'")
        self.assert_located()
        self.context.send_keys(self.element_id, text)
        return self
    
    def get_text(self) -> str:
        """
        Get text from the element.
        
        Returns:
            Element text
            
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        logger.info(f"Getting text from element '{self.name}'")
        self.assert_located()
        return self.context.get_text(self.element_id)
    
    def is_displayed(self) -> bool:
        """
        Check if element is displayed.
        
        Returns:
            True if element is displayed, False otherwise or if not found
        """
        try:
            self.assert_located()
            result = self.context.execute("isDisplayed", {"elementId": self.element_id})
            return bool(result.get("value", False))
        except ElementNotFoundError:
            return False
    
    def is_enabled(self) -> bool:
        """
        Check if element is enabled.
        
        Returns:
            True if element is enabled, False otherwise or if not found
        """
        try:
            self.assert_located()
            result = self.context.execute("isEnabled", {"elementId": self.element_id})
            return bool(result.get("value", False))
        except ElementNotFoundError:
            return False
    
    def clear(self) -> 'AppiumModel':
        """
        Clear the element (usually for input fields).
        
        Returns:
            Self for method chaining
            
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        logger.info(f"Clearing element '{self.name}'")
        self.assert_located()
        self.context.execute("clear", {"elementId": self.element_id})
        return self
    
    def tap(self, x: Optional[int] = None, y: Optional[int] = None) -> 'AppiumModel':
        """
        Tap on the element or at specific coordinates.
        
        Args:
            x: Optional x coordinate within the element
            y: Optional y coordinate within the element
            
        Returns:
            Self for method chaining
            
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        self.assert_located()
        
        if x is None or y is None:
            logger.info(f"Tapping on element '{self.name}'")
            self.context.execute("tap", {"elementId": self.element_id})
        else:
            logger.info(f"Tapping on element '{self.name}' at coordinates ({x}, {y})")
            self.context.execute("tap", {"elementId": self.element_id, "x": x, "y": y})
            
        return self
    
    def swipe(self, direction: str, percentage: float = 0.5, speed: int = 800) -> 'AppiumModel':
        """
        Swipe on the element in a specific direction.
        
        Args:
            direction: Direction to swipe ('up', 'down', 'left', 'right')
            percentage: Percentage of the element size to swipe (0.0-1.0)
            speed: Swipe speed in milliseconds
            
        Returns:
            Self for method chaining
            
        Raises:
            ElementNotFoundError: If element cannot be found
            InvalidArgumentError: If direction is invalid
        """
        valid_directions = ('up', 'down', 'left', 'right')
        if direction not in valid_directions:
            raise InvalidArgumentError(f"Invalid swipe direction '{direction}'. Must be one of {valid_directions}")
            
        if not 0.0 <= percentage <= 1.0:
            raise InvalidArgumentError(f"Invalid swipe percentage '{percentage}'. Must be between 0.0 and 1.0")
            
        self.assert_located()
        logger.info(f"Swiping {direction} on element '{self.name}'")
        
        params = {
            "elementId": self.element_id,
            "direction": direction,
            "percent": percentage,
            "speed": speed
        }
        
        self.context.execute("swipe", params)
        return self
    
    def long_press(self, duration: int = 1000) -> 'AppiumModel':
        """
        Long press on the element.
        
        Args:
            duration: Press duration in milliseconds
            
        Returns:
            Self for method chaining
            
        Raises:
            ElementNotFoundError: If element cannot be found
        """
        self.assert_located()
        logger.info(f"Long pressing on element '{self.name}' for {duration}ms")
        
        params = {
            "elementId": self.element_id,
            "duration": duration
        }
        
        self.context.execute("longPress", params)
        return self
    
    def find_child(self, by: Union[str, By], value: str, name: str = None) -> 'AppiumModel':
        """
        Find a child element relative to this element.
        
        Args:
            by: Locator strategy
            value: Locator value
            name: Optional friendly name for the child element
            
        Returns:
            New AppiumModel for the child element
            
        Raises:
            ElementNotFoundError: If parent element cannot be found
        """
        self.assert_located()
        child_name = name or f"{self.name} > {by}={value}"
        
        # Create an XPath expression to find elements under this element
        if isinstance(by, By):
            by = by.value
            
        if by == "id":
            child_locator = f".//*[@resource-id='{value}']"
        elif by == "xpath":
            # Ensure the provided xpath is relative to the current element
            if value.startswith("//"):
                child_locator = f".{value}"
            else:
                child_locator = value
        elif by == "class name":
            child_locator = f".//*[@class='{value}']"
        elif by == "accessibility id":
            child_locator = f".//*[@content-desc='{value}']"
        else:
            # For unsupported locator types, we'll use the find_element in the context
            # but this is less efficient as it doesn't use the parent element's scope
            logger.warning(f"Finding child with '{by}' strategy is not optimized")
            child_model = AppiumModel(self.context, by, value, name=child_name)
            if child_model.locate():
                return child_model
            raise ElementNotFoundError(f"Child element not found with {by}='{value}'")
            
        # Use XPath to find the child element
        child_model = AppiumModel(self.context, "xpath", child_locator, name=child_name)
        if child_model.locate():
            return child_model
            
        raise ElementNotFoundError(f"Child element not found with {by}='{value}'")
