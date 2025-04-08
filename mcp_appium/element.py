"""
Element module for MCP Appium
=============================

This module provides the Element class which represents an element in the mobile application.
"""

import base64
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING

from .errors import ElementNotFoundError, InvalidArgumentError

if TYPE_CHECKING:
    from .models import Session

logger = logging.getLogger(__name__)

class Element:
    """
    Represents an element in a mobile application.
    
    This class provides methods for interacting with elements, such as clicking,
    sending keys, and getting attributes.
    """
    
    def __init__(self, session: 'Session', element_id: str, element_info: Optional[Dict[str, Any]] = None):
        """
        Initialize an Element object.
        
        Args:
            session: The session that this element belongs to
            element_id: The element ID from Appium
            element_info: Additional element information (optional)
        """
        self.session = session
        self.id = element_id
        self.info = element_info or {}
        logger.debug(f"Created element with ID: {element_id}")
    
    def click(self) -> None:
        """
        Click on the element.
        
        Raises:
            AppiumMCPError: If the click operation fails
        """
        self.session.client.execute_command("click", {"element_id": self.id})
        logger.debug(f"Clicked element with ID: {self.id}")
    
    def clear(self) -> None:
        """
        Clear the element's text content.
        
        Raises:
            AppiumMCPError: If the clear operation fails
        """
        self.session.client.execute_command("clear", {"element_id": self.id})
        logger.debug(f"Cleared element with ID: {self.id}")
    
    def send_keys(self, text: str) -> None:
        """
        Send keys to the element.
        
        Args:
            text: The text to send
            
        Raises:
            InvalidArgumentError: If text is empty
            AppiumMCPError: If the send keys operation fails
        """
        if not text:
            raise InvalidArgumentError("Text cannot be empty")
        
        self.session.client.execute_command(
            "sendKeys", 
            {
                "element_id": self.id,
                "text": text,
                "value": list(text)  # MCP expects a list of characters
            }
        )
        logger.debug(f"Sent keys '{text}' to element with ID: {self.id}")
    
    def get_text(self) -> str:
        """
        Get the element's visible text.
        
        Returns:
            str: The element's text
            
        Raises:
            AppiumMCPError: If the get text operation fails
        """
        result = self.session.client.execute_command("getText", {"element_id": self.id})
        return result.get("value", "")
    
    def get_attribute(self, name: str) -> str:
        """
        Get the value of an element's attribute.
        
        Args:
            name: The attribute name
            
        Returns:
            str: The attribute value
            
        Raises:
            InvalidArgumentError: If name is empty
            AppiumMCPError: If the get attribute operation fails
        """
        if not name:
            raise InvalidArgumentError("Attribute name cannot be empty")
        
        result = self.session.client.execute_command(
            "getAttribute", 
            {
                "element_id": self.id,
                "name": name
            }
        )
        return result.get("value", "")
    
    def is_displayed(self) -> bool:
        """
        Check if the element is displayed.
        
        Returns:
            bool: True if the element is displayed, False otherwise
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("isDisplayed", {"element_id": self.id})
        return bool(result.get("value", False))
    
    def is_enabled(self) -> bool:
        """
        Check if the element is enabled.
        
        Returns:
            bool: True if the element is enabled, False otherwise
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("isEnabled", {"element_id": self.id})
        return bool(result.get("value", False))
    
    def is_selected(self) -> bool:
        """
        Check if the element is selected.
        
        Returns:
            bool: True if the element is selected, False otherwise
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("isSelected", {"element_id": self.id})
        return bool(result.get("value", False))
    
    def find_element(self, by: str, value: str) -> 'Element':
        """
        Find a child element of this element.
        
        Args:
            by: The locator strategy, e.g., "id", "xpath", "accessibility id"
            value: The locator value
            
        Returns:
            Element: The found element
            
        Raises:
            InvalidArgumentError: If by or value is empty
            ElementNotFoundError: If the element is not found
            AppiumMCPError: If the find operation fails
        """
        if not by or not value:
            raise InvalidArgumentError("Locator strategy and value cannot be empty")
        
        result = self.session.client.execute_command(
            "findElementFromElement", 
            {
                "element_id": self.id,
                "using": by,
                "value": value
            }
        )
        
        if not result or "value" not in result or "ELEMENT" not in result["value"]:
            raise ElementNotFoundError(f"Element not found using {by}={value}")
        
        element_id = result["value"]["ELEMENT"]
        return Element(self.session, element_id, result["value"])
    
    def find_elements(self, by: str, value: str) -> List['Element']:
        """
        Find child elements of this element.
        
        Args:
            by: The locator strategy, e.g., "id", "xpath", "accessibility id"
            value: The locator value
            
        Returns:
            List[Element]: The found elements
            
        Raises:
            InvalidArgumentError: If by or value is empty
            AppiumMCPError: If the find operation fails
        """
        if not by or not value:
            raise InvalidArgumentError("Locator strategy and value cannot be empty")
        
        result = self.session.client.execute_command(
            "findElementsFromElement", 
            {
                "element_id": self.id,
                "using": by,
                "value": value
            }
        )
        
        elements = []
        if result and "value" in result:
            for element_data in result["value"]:
                if "ELEMENT" in element_data:
                    element_id = element_data["ELEMENT"]
                    elements.append(Element(self.session, element_id, element_data))
        
        return elements
    
    def __str__(self) -> str:
        """String representation of the element."""
        return f"Element(id={self.id})"
    
    def get_location(self) -> Dict[str, int]:
        """
        Get the element's location on the screen.
        
        Returns:
            Dict[str, int]: A dictionary with 'x' and 'y' coordinates
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getLocation", {"element_id": self.id})
        return result.get("value", {"x": 0, "y": 0})
    
    def get_size(self) -> Dict[str, int]:
        """
        Get the element's size.
        
        Returns:
            Dict[str, int]: A dictionary with 'width' and 'height'
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getSize", {"element_id": self.id})
        return result.get("value", {"width": 0, "height": 0})
    
    def get_rect(self) -> Dict[str, int]:
        """
        Get the element's rectangle (location and size).
        
        Returns:
            Dict[str, int]: A dictionary with 'x', 'y', 'width', and 'height'
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getRect", {"element_id": self.id})
        return result.get("value", {"x": 0, "y": 0, "width": 0, "height": 0})
    
    def get_css_value(self, property_name: str) -> str:
        """
        Get the value of a CSS property (web context only).
        
        Args:
            property_name: The CSS property name
            
        Returns:
            str: The property value
            
        Raises:
            InvalidArgumentError: If property_name is empty
            AppiumMCPError: If the operation fails
        """
        if not property_name:
            raise InvalidArgumentError("Property name cannot be empty")
        
        result = self.session.client.execute_command(
            "getCssProperty", 
            {
                "element_id": self.id,
                "property_name": property_name
            }
        )
        return result.get("value", "")
    
    def get_all_attributes(self) -> Dict[str, Any]:
        """
        Get all attributes of the element.
        
        Returns:
            Dict[str, Any]: A dictionary of all attributes
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getAttributes", {"element_id": self.id})
        return result.get("value", {})
    
    def submit(self) -> None:
        """
        Submit a form element.
        
        Raises:
            AppiumMCPError: If the submit operation fails
        """
        self.session.client.execute_command("submit", {"element_id": self.id})
        logger.debug(f"Submitted form element with ID: {self.id}")
    
    def get_tag_name(self) -> str:
        """
        Get the element's tag name.
        
        Returns:
            str: The tag name
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getName", {"element_id": self.id})
        return result.get("value", "")
    
    def get_property(self, name: str) -> Any:
        """
        Get the value of an element's property.
        
        Args:
            name: The property name
            
        Returns:
            Any: The property value
            
        Raises:
            InvalidArgumentError: If name is empty
            AppiumMCPError: If the operation fails
        """
        if not name:
            raise InvalidArgumentError("Property name cannot be empty")
        
        result = self.session.client.execute_command(
            "getProperty", 
            {
                "element_id": self.id,
                "name": name
            }
        )
        return result.get("value")
    
    def get_computed_role(self) -> str:
        """
        Get the element's computed role (accessibility).
        
        Returns:
            str: The computed role
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getComputedRole", {"element_id": self.id})
        return result.get("value", "")
    
    def get_computed_label(self) -> str:
        """
        Get the element's computed label (accessibility).
        
        Returns:
            str: The computed label
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getComputedLabel", {"element_id": self.id})
        return result.get("value", "")
    
    def take_screenshot(self) -> str:
        """
        Take a screenshot of the element.
        
        Returns:
            str: Base64-encoded string of the screenshot
            
        Raises:
            AppiumMCPError: If the screenshot operation fails
        """
        result = self.session.client.execute_command("takeElementScreenshot", {"element_id": self.id})
        return result.get("value", "")
    
    def scroll_to(self) -> None:
        """
        Scroll to the element to make it visible.
        
        Raises:
            AppiumMCPError: If the scroll operation fails
        """
        try:
            script = "arguments[0].scrollIntoView(true);"
            self.session.execute_script(script, [{"ELEMENT": self.id}])
            logger.debug(f"Scrolled to element with ID: {self.id}")
        except Exception as e:
            logger.error(f"Failed to scroll to element: {e}")
            raise
    
    def get_accessible_name(self) -> str:
        """
        Get the element's accessible name.
        
        Returns:
            str: The accessible name
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getAccessibleName", {"element_id": self.id})
        return result.get("value", "")
    
    def get_aria_role(self) -> str:
        """
        Get the element's ARIA role.
        
        Returns:
            str: The ARIA role
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.session.client.execute_command("getAriaRole", {"element_id": self.id})
        return result.get("value", "")
    
    def __repr__(self) -> str:
        """Detailed representation of the element."""
        return f"Element(id={self.id}, session_id={self.session.id})"
