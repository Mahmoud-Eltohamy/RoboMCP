"""
Models module for MCP Appium
============================

This module contains data models used by the MCP Appium implementation.
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING

from .element import Element
from .errors import ElementNotFoundError, InvalidArgumentError

if TYPE_CHECKING:
    from .client import AppiumClient

logger = logging.getLogger(__name__)

class Session:
    """
    Represents an Appium session.
    
    This class provides methods for interacting with the mobile application,
    such as finding elements and navigating.
    """
    
    def __init__(self, id: str, capabilities: Dict[str, Any], client: 'AppiumClient'):
        """
        Initialize a Session object.
        
        Args:
            id: The session ID
            capabilities: The session capabilities
            client: The AppiumClient instance
        """
        self.id = id
        self.capabilities = capabilities
        self.client = client
        logger.info(f"Session initialized with ID: {id}")
        logger.debug(f"Session capabilities: {capabilities}")
    
    def find_element(self, by: str, value: str) -> Element:
        """
        Find an element in the application.
        
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
        
        result = self.client.execute_command(
            "findElement", 
            {
                "using": by,
                "value": value
            }
        )
        
        if not result or "value" not in result or not isinstance(result["value"], dict):
            raise ElementNotFoundError(f"Element not found using {by}={value}")
        
        # Handle W3C WebDriver protocol response format
        element_key = None
        for key in result["value"]:
            if key in ["ELEMENT", "element-6066-11e4-a52e-4f735466cecf"]:
                element_key = key
                break
                
        if not element_key:
            raise ElementNotFoundError(f"Element not found using {by}={value}")
            
        element_id = result["value"][element_key]
        return Element(self, element_id, result["value"])
    
    def find_elements(self, by: str, value: str) -> List[Element]:
        """
        Find elements in the application.
        
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
        
        result = self.client.execute_command(
            "findElements", 
            {
                "using": by,
                "value": value
            }
        )
        
        elements = []
        if result and "value" in result and isinstance(result["value"], list):
            for element_data in result["value"]:
                element_key = None
                for key in element_data:
                    if key in ["ELEMENT", "element-6066-11e4-a52e-4f735466cecf"]:
                        element_key = key
                        break
                        
                if element_key:
                    element_id = element_data[element_key]
                    elements.append(Element(self, element_id, element_data))
        
        return elements
    
    def get_page_source(self) -> str:
        """
        Get the page source of the current view.
        
        Returns:
            str: The page source
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("source")
        return result.get("value", "")
    
    def get_current_context(self) -> str:
        """
        Get the current context.
        
        Returns:
            str: The current context
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getCurrentContext")
        return result.get("value", "")
    
    def get_contexts(self) -> List[str]:
        """
        Get all available contexts.
        
        Returns:
            List[str]: The available contexts
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getContexts")
        contexts = result.get("value", [])
        return contexts if isinstance(contexts, list) else []
    
    def switch_to_context(self, context_name: str) -> None:
        """
        Switch to a different context.
        
        Args:
            context_name: The name of the context to switch to
            
        Raises:
            InvalidArgumentError: If context_name is empty
            AppiumMCPError: If the switch operation fails
        """
        if not context_name:
            raise InvalidArgumentError("Context name cannot be empty")
        
        self.client.execute_command("switchContext", {"name": context_name})
        logger.info(f"Switched to context: {context_name}")
    
    def back(self) -> None:
        """
        Navigate back.
        
        Raises:
            AppiumMCPError: If the back operation fails
        """
        self.client.execute_command("back")
        logger.debug("Navigated back")
    
    def get_orientation(self) -> str:
        """
        Get the current device orientation.
        
        Returns:
            str: The current orientation ("PORTRAIT" or "LANDSCAPE")
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getOrientation")
        return result.get("value", "")
    
    def set_orientation(self, orientation: str) -> None:
        """
        Set the device orientation.
        
        Args:
            orientation: The orientation to set ("PORTRAIT" or "LANDSCAPE")
            
        Raises:
            InvalidArgumentError: If orientation is not valid
            AppiumMCPError: If the operation fails
        """
        if orientation not in ["PORTRAIT", "LANDSCAPE"]:
            raise InvalidArgumentError("Orientation must be 'PORTRAIT' or 'LANDSCAPE'")
        
        self.client.execute_command("setOrientation", {"orientation": orientation})
        logger.info(f"Set orientation to: {orientation}")
    
    def get_screenshot(self) -> str:
        """
        Take a screenshot of the current view.
        
        Returns:
            str: The screenshot as a base64-encoded string
            
        Raises:
            AppiumMCPError: If the screenshot operation fails
        """
        result = self.client.execute_command("screenshot")
        return result.get("value", "")
    
    def launch_app(self) -> None:
        """
        Launch the app.
        
        Raises:
            AppiumMCPError: If the launch operation fails
        """
        self.client.execute_command("launchApp")
        logger.info("App launched")
    
    def close_app(self) -> None:
        """
        Close the app.
        
        Raises:
            AppiumMCPError: If the close operation fails
        """
        self.client.execute_command("closeApp")
        logger.info("App closed")
    
    def reset_app(self) -> None:
        """
        Reset the app.
        
        Raises:
            AppiumMCPError: If the reset operation fails
        """
        self.client.execute_command("resetApp")
        logger.info("App reset")
    
    def execute_script(self, script: str, args: Optional[List[Any]] = None) -> Any:
        """
        Execute JavaScript in the context of the current page.
        
        Args:
            script: The script to execute
            args: The arguments to pass to the script
            
        Returns:
            Any: The result of the script execution
            
        Raises:
            InvalidArgumentError: If script is empty
            AppiumMCPError: If the script execution fails
        """
        if not script:
            raise InvalidArgumentError("Script cannot be empty")
        
        result = self.client.execute_command(
            "executeScript", 
            {
                "script": script,
                "args": args or []
            }
        )
        return result.get("value")
    
    def execute_async_script(self, script: str, args: Optional[List[Any]] = None) -> Any:
        """
        Execute asynchronous JavaScript in the context of the current page.
        
        Args:
            script: The script to execute
            args: The arguments to pass to the script
            
        Returns:
            Any: The result of the script execution
            
        Raises:
            InvalidArgumentError: If script is empty
            AppiumMCPError: If the script execution fails
        """
        if not script:
            raise InvalidArgumentError("Script cannot be empty")
        
        result = self.client.execute_command(
            "executeAsyncScript", 
            {
                "script": script,
                "args": args or []
            }
        )
        return result.get("value")
    
    def set_timeouts(self, implicit: Optional[int] = None, page_load: Optional[int] = None, 
                    script: Optional[int] = None) -> None:
        """
        Set timeouts for the session.
        
        Args:
            implicit: Implicit wait timeout in milliseconds
            page_load: Page load timeout in milliseconds
            script: Script timeout in milliseconds
            
        Raises:
            AppiumMCPError: If the set timeouts operation fails
        """
        timeouts = {}
        if implicit is not None:
            timeouts["implicit"] = implicit
        if page_load is not None:
            timeouts["pageLoad"] = page_load
        if script is not None:
            timeouts["script"] = script
        
        if timeouts:
            self.client.execute_command("setTimeouts", timeouts)
            logger.info(f"Set timeouts: {timeouts}")
    
    def get_current_activity(self) -> str:
        """
        Get the current activity (Android only).
        
        Returns:
            str: The current activity name
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getCurrentActivity")
        return result.get("value", "")
    
    def get_current_package(self) -> str:
        """
        Get the current package (Android only).
        
        Returns:
            str: The current package name
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getCurrentPackage")
        return result.get("value", "")
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 800) -> None:
        """
        Perform a swipe gesture.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of swipe in milliseconds
            
        Raises:
            AppiumMCPError: If the swipe operation fails
        """
        self.client.execute_command(
            "swipe", 
            {
                "startX": start_x,
                "startY": start_y,
                "endX": end_x,
                "endY": end_y,
                "duration": duration
            }
        )
        logger.debug(f"Performed swipe from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        
    def scroll(self, direction: str, percent: float = 0.5, duration: int = 800) -> None:
        """
        Perform a scroll gesture in the specified direction.
        
        Args:
            direction: Direction to scroll ("up", "down", "left", "right")
            percent: Percentage of the screen to scroll (0.0 to 1.0)
            duration: Duration of scroll in milliseconds
            
        Raises:
            InvalidArgumentError: If direction is invalid
            AppiumMCPError: If the scroll operation fails
        """
        if direction not in ["up", "down", "left", "right"]:
            raise InvalidArgumentError("Direction must be 'up', 'down', 'left', or 'right'")
            
        # Get screen size to calculate coordinates
        result = self.client.execute_command("getWindowSize")
        window_size = result.get("value", {"width": 0, "height": 0})
        width = window_size.get("width", 0)
        height = window_size.get("height", 0)
        
        # Calculate start and end coordinates based on direction
        if direction == "up":
            start_x = int(width * 0.5)
            start_y = int(height * 0.7)
            end_x = int(width * 0.5)
            end_y = int(height * (0.7 - percent))
        elif direction == "down":
            start_x = int(width * 0.5)
            start_y = int(height * 0.3)
            end_x = int(width * 0.5)
            end_y = int(height * (0.3 + percent))
        elif direction == "left":
            start_x = int(width * 0.7)
            start_y = int(height * 0.5)
            end_x = int(width * (0.7 - percent))
            end_y = int(height * 0.5)
        else:  # right
            start_x = int(width * 0.3)
            start_y = int(height * 0.5)
            end_x = int(width * (0.3 + percent))
            end_y = int(height * 0.5)
            
        # Perform the swipe
        self.swipe(start_x, start_y, end_x, end_y, duration)
        logger.debug(f"Performed scroll {direction} with {percent*100}% of the screen")
    
    def long_press(self, x: int, y: int, duration: int = 1000) -> None:
        """
        Perform a long press gesture at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of press in milliseconds
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        actions = [
            {"action": "press", "options": {"x": x, "y": y}},
            {"action": "wait", "options": {"ms": duration}},
            {"action": "release", "options": {}}
        ]
        
        self.client.execute_command("touchPerform", {"actions": actions})
        logger.debug(f"Performed long press at ({x}, {y}) for {duration}ms")
        
    def pinch(self, scale: float, velocity: float = 1.0) -> None:
        """
        Perform a pinch gesture (zoom in/out).
        
        Args:
            scale: Scale factor (< 1.0 for pinch in, > 1.0 for pinch out)
            velocity: Speed of the gesture
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        self.client.execute_command(
            "pinch", 
            {
                "scale": scale,
                "velocity": velocity
            }
        )
        action = "in" if scale < 1.0 else "out"
        logger.debug(f"Performed pinch {action} with scale {scale}")
        
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000) -> None:
        """
        Perform a drag and drop gesture.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of gesture in milliseconds
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        actions = [
            {"action": "press", "options": {"x": start_x, "y": start_y}},
            {"action": "wait", "options": {"ms": duration}},
            {"action": "moveTo", "options": {"x": end_x, "y": end_y}},
            {"action": "release", "options": {}}
        ]
        
        self.client.execute_command("touchPerform", {"actions": actions})
        logger.debug(f"Performed drag and drop from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        
    def double_tap(self, x: int, y: int) -> None:
        """
        Perform a double tap gesture at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        actions = [
            {"action": "tap", "options": {"x": x, "y": y, "count": 2}}
        ]
        
        self.client.execute_command("touchPerform", {"actions": actions})
        logger.debug(f"Performed double tap at ({x}, {y})")
        

    
    def tap(self, x: int, y: int) -> None:
        """
        Tap at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Raises:
            AppiumMCPError: If the tap operation fails
        """
        self.client.execute_command(
            "tap", 
            {
                "x": x,
                "y": y
            }
        )
        logger.debug(f"Tapped at coordinates ({x}, {y})")
    
    def multi_touch_perform(self, actions: List[Dict[str, Any]]) -> None:
        """
        Perform multi-touch actions.
        
        Args:
            actions: List of touch actions to perform
            
        Raises:
            InvalidArgumentError: If actions is empty
            AppiumMCPError: If the operation fails
        """
        if not actions:
            raise InvalidArgumentError("Actions cannot be empty")
        
        self.client.execute_command("multiTouchPerform", {"actions": actions})
        logger.debug("Performed multi-touch actions")
    
    def touch_perform(self, actions: List[Dict[str, Any]]) -> None:
        """
        Perform touch actions.
        
        Args:
            actions: List of touch actions to perform
            
        Raises:
            InvalidArgumentError: If actions is empty
            AppiumMCPError: If the operation fails
        """
        if not actions:
            raise InvalidArgumentError("Actions cannot be empty")
        
        self.client.execute_command("touchPerform", {"actions": actions})
        logger.debug("Performed touch actions")
    
    def w3c_actions(self, actions: Dict[str, Any]) -> None:
        """
        Perform W3C actions.
        
        Args:
            actions: The W3C actions to perform
            
        Raises:
            InvalidArgumentError: If actions is empty
            AppiumMCPError: If the operation fails
        """
        if not actions:
            raise InvalidArgumentError("Actions cannot be empty")
        
        self.client.execute_command("w3cActions", {"actions": actions})
        logger.debug("Performed W3C actions")
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get information about all active sessions.
        
        Returns:
            List[Dict[str, Any]]: Information about all active sessions
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getSessions")
        return result.get("value", [])
    
    def get_available_ime_engines(self) -> List[str]:
        """
        Get available IME engines (Android only).
        
        Returns:
            List[str]: Available IME engines
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getAvailableIMEEngines")
        return result.get("value", [])
    
    def get_device_time(self) -> str:
        """
        Get the device time.
        
        Returns:
            str: The device time
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getDeviceTime")
        return result.get("value", "")
    
    def get_session_capabilities(self) -> Dict[str, Any]:
        """
        Get the session capabilities.
        
        Returns:
            Dict[str, Any]: The session capabilities
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getSessionCapabilities")
        return result.get("value", {})
    
    def set_immediate_value(self, element_id: str, value: str) -> None:
        """
        Set the value of an element immediately without clear/send_keys.
        
        Args:
            element_id: The element ID
            value: The value to set
            
        Raises:
            InvalidArgumentError: If element_id or value is empty
            AppiumMCPError: If the operation fails
        """
        if not element_id or not value:
            raise InvalidArgumentError("Element ID and value cannot be empty")
        
        self.client.execute_command(
            "setImmediateValue", 
            {
                "element_id": element_id,
                "value": value
            }
        )
        logger.debug(f"Set immediate value '{value}' for element {element_id}")
    
    def start_activity(self, app_package: str, app_activity: str, app_wait_package: Optional[str] = None,
                     app_wait_activity: Optional[str] = None) -> None:
        """
        Start an Android activity (Android only).
        
        Args:
            app_package: The package name
            app_activity: The activity name
            app_wait_package: The package name to wait for
            app_wait_activity: The activity name to wait for
            
        Raises:
            InvalidArgumentError: If app_package or app_activity is empty
            AppiumMCPError: If the operation fails
        """
        if not app_package or not app_activity:
            raise InvalidArgumentError("Package name and activity name cannot be empty")
        
        params = {
            "appPackage": app_package,
            "appActivity": app_activity
        }
        
        if app_wait_package:
            params["appWaitPackage"] = app_wait_package
        if app_wait_activity:
            params["appWaitActivity"] = app_wait_activity
        
        self.client.execute_command("startActivity", params)
        logger.info(f"Started activity {app_package}/{app_activity}")
    
    def toggle_location_services(self) -> None:
        """
        Toggle location services on the device.
        
        Raises:
            AppiumMCPError: If the operation fails
        """
        self.client.execute_command("toggleLocationServices")
        logger.info("Toggled location services")
    
    def hide_keyboard_with_params(self, strategy: Optional[str] = None, key: Optional[str] = None) -> None:
        """
        Hide the keyboard with specific strategy or key.
        
        Args:
            strategy: Optional strategy to hide keyboard ("tapOutside", "pressKey", etc.)
            key: Optional key to press to hide keyboard
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        params = {}
        if strategy:
            params["strategy"] = strategy
        if key:
            params["key"] = key
            
        self.client.execute_command("hideKeyboard", params)
        logger.debug(f"Hidden keyboard with strategy: {strategy}, key: {key}")
    
    def is_keyboard_shown_with_timeout(self, timeout: int = 5) -> bool:
        """
        Check if the keyboard is shown with specified timeout.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bool: True if the keyboard is shown, False otherwise
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("isKeyboardShown", {"timeout": timeout})
        return bool(result.get("value", False))
    
    def set_geolocation(self, latitude: float, longitude: float, altitude: float = 0.0) -> None:
        """
        Set the geolocation of the device.
        
        Args:
            latitude: The latitude
            longitude: The longitude
            altitude: The altitude
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        self.client.execute_command(
            "setGeolocation", 
            {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude
                }
            }
        )
        logger.info(f"Set geolocation to lat:{latitude}, long:{longitude}, alt:{altitude}")
    
    def get_geolocation(self) -> Dict[str, float]:
        """
        Get the geolocation of the device.
        
        Returns:
            Dict[str, float]: The geolocation
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getGeolocation")
        return result.get("value", {})
        
    # iOS-specific methods
    
    def shake(self) -> None:
        """
        Shake the device (iOS only).
        
        Raises:
            AppiumMCPError: If the operation fails
        """
        self.client.execute_command("shake")
        logger.info("Shook the device")
        
    def touch_id(self, match: bool) -> None:
        """
        Simulate Touch ID on iOS (iOS only).
        
        Args:
            match: True for a successful match, False for a failed match
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        self.client.execute_command("touchId", {"match": match})
        logger.info(f"Simulated Touch ID with match={match}")
        
    def toggle_airplane_mode(self) -> None:
        """
        Toggle airplane mode (iOS and Android).
        
        Raises:
            AppiumMCPError: If the operation fails
        """
        self.client.execute_command("toggleAirplaneMode")
        logger.info("Toggled airplane mode")
        
    def set_clipboard(self, content: str, content_type: str = "plaintext") -> None:
        """
        Set the content of the clipboard.
        
        Args:
            content: The content to set
            content_type: The type of content (plaintext, image, url)
            
        Raises:
            InvalidArgumentError: If content is empty
            AppiumMCPError: If the operation fails
        """
        if not content:
            raise InvalidArgumentError("Content cannot be empty")
        
        self.client.execute_command(
            "setClipboard", 
            {
                "content": content,
                "contentType": content_type
            }
        )
        logger.debug(f"Set clipboard content of type {content_type}")
        
    def get_clipboard(self, content_type: str = "plaintext") -> str:
        """
        Get the content of the clipboard.
        
        Args:
            content_type: The type of content to get (plaintext, image, url)
            
        Returns:
            str: The clipboard content
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command(
            "getClipboard", 
            {
                "contentType": content_type
            }
        )
        return result.get("value", "")
        
    def install_app(self, app_path: str) -> None:
        """
        Install an app on the device.
        
        Args:
            app_path: Path to the app
            
        Raises:
            InvalidArgumentError: If app_path is empty
            AppiumMCPError: If the operation fails
        """
        if not app_path:
            raise InvalidArgumentError("App path cannot be empty")
        
        self.client.execute_command("installApp", {"appPath": app_path})
        logger.info(f"Installed app from {app_path}")
        
    def remove_app(self, app_id: str) -> None:
        """
        Remove an app from the device.
        
        Args:
            app_id: Bundle ID or package name of the app
            
        Raises:
            InvalidArgumentError: If app_id is empty
            AppiumMCPError: If the operation fails
        """
        if not app_id:
            raise InvalidArgumentError("App ID cannot be empty")
        
        self.client.execute_command("removeApp", {"appId": app_id})
        logger.info(f"Removed app with ID {app_id}")
        
    def is_app_installed(self, app_id: str) -> bool:
        """
        Check if an app is installed on the device.
        
        Args:
            app_id: Bundle ID or package name of the app
            
        Returns:
            bool: True if the app is installed, False otherwise
            
        Raises:
            InvalidArgumentError: If app_id is empty
            AppiumMCPError: If the operation fails
        """
        if not app_id:
            raise InvalidArgumentError("App ID cannot be empty")
        
        result = self.client.execute_command("isAppInstalled", {"bundleId": app_id})
        return bool(result.get("value", False))
        
    def get_window_size(self) -> Dict[str, int]:
        """
        Get the window size of the device.
        
        Returns:
            Dict[str, int]: A dictionary with 'width' and 'height'
            
        Raises:
            AppiumMCPError: If the operation fails
        """
        result = self.client.execute_command("getWindowSize")
        return result.get("value", {"width": 0, "height": 0})
    
    def quit(self) -> None:
        """
        Quit the session.
        
        Raises:
            AppiumMCPError: If the quit operation fails
        """
        self.client.quit()
        logger.info("Session quit")
    
    def __str__(self) -> str:
        """String representation of the session."""
        return f"Session(id={self.id})"
    
    def __repr__(self) -> str:
        """Detailed representation of the session."""
        return f"Session(id={self.id}, capabilities={self.capabilities})"
