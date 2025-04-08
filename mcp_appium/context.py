"""
Context module provides the AppiumContext class for session management.

This module implements the Context component of the Model Context Protocol for Appium,
managing session lifecycle and providing an execution environment for models.
"""

import logging
from typing import Dict, Any, Optional, List

from mcp_appium.client import AppiumClient
from mcp_appium.commands import AppiumCommands, build_find_element_params, parse_element_result, parse_elements_result
from mcp_appium.exceptions import SessionNotCreatedError, ElementNotFoundError, CommandFailedError

logger = logging.getLogger(__name__)

class AppiumContext:
    """
    Context class for managing Appium sessions and executing commands.
    
    The AppiumContext manages the lifecycle of an Appium session and provides
    methods to execute commands within that session. It serves as the execution
    environment for AppiumModel instances.
    """
    
    def __init__(self, client: AppiumClient, capabilities: Dict[str, Any]):
        """
        Initialize an Appium context.
        
        Args:
            client: AppiumClient instance for server communication
            capabilities: Desired capabilities for the session
        """
        self.client = client
        self.capabilities = capabilities
        self.session_id = None
        logger.debug(f"Initialized AppiumContext with capabilities: {capabilities}")
        
    def __enter__(self):
        """
        Start the Appium session when entering context.
        
        Returns:
            Self for use in with statement
        
        Raises:
            SessionNotCreatedError: If session creation fails
        """
        self.start_session()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        End the Appium session when exiting context.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self.end_session()
        
    def start_session(self) -> None:
        """
        Start a new Appium session with the provided capabilities.
        
        Raises:
            SessionNotCreatedError: If session creation fails
        """
        if self.session_id:
            logger.warning("Session already exists, ending existing session first")
            self.end_session()
            
        logger.info("Starting new Appium session")
        response = self.client.create_session(self.capabilities)
        self.session_id = response["sessionId"]
        logger.info(f"Session started with ID: {self.session_id}")
        
    def end_session(self) -> None:
        """End the current Appium session if one exists."""
        if self.session_id:
            logger.info(f"Ending session: {self.session_id}")
            self.client.end_session(self.session_id)
            self.session_id = None
        else:
            logger.warning("No active session to end")
    
    def execute(self, command: str, params: Optional[Dict] = None) -> Dict:
        """
        Execute a command in the current session.
        
        Args:
            command: Command to execute
            params: Command parameters
            
        Returns:
            Command execution results
            
        Raises:
            SessionNotCreatedError: If no active session
            CommandFailedError: If command execution fails
        """
        if not self.session_id:
            raise SessionNotCreatedError("No active session")
            
        return self.client.execute_command(self.session_id, command, params)
    
    def find_element(self, by: str, value: str) -> str:
        """
        Find an element in the current session.
        
        Args:
            by: Element location strategy
            value: Element locator value
            
        Returns:
            Element ID if found
            
        Raises:
            ElementNotFoundError: If element not found
        """
        logger.debug(f"Finding element with {by}='{value}'")
        params = build_find_element_params(by, value)
        
        try:
            result = self.execute(AppiumCommands.FIND_ELEMENT, params)
            element_id = parse_element_result(result)
            
            if not element_id:
                raise ElementNotFoundError(f"Element not found with {by}='{value}'")
                
            logger.debug(f"Found element with ID: {element_id}")
            return element_id
        except Exception as e:
            logger.error(f"Failed to find element: {e}")
            raise ElementNotFoundError(f"Element not found with {by}='{value}': {e}")
    
    def find_elements(self, by: str, value: str) -> List[str]:
        """
        Find multiple elements in the current session.
        
        Args:
            by: Element location strategy
            value: Element locator value
            
        Returns:
            List of element IDs
        """
        logger.debug(f"Finding elements with {by}='{value}'")
        params = build_find_element_params(by, value)
        
        try:
            result = self.execute(AppiumCommands.FIND_ELEMENTS, params)
            element_ids = parse_elements_result(result)
            logger.debug(f"Found {len(element_ids)} elements")
            return element_ids
        except Exception as e:
            logger.error(f"Failed to find elements: {e}")
            return []
    
    def click_element(self, element_id: str) -> None:
        """
        Click on an element.
        
        Args:
            element_id: ID of the element to click
            
        Raises:
            CommandFailedError: If click action fails
        """
        logger.debug(f"Clicking element: {element_id}")
        self.execute(AppiumCommands.CLICK_ELEMENT, {"elementId": element_id})
    
    def send_keys(self, element_id: str, text: str) -> None:
        """
        Send keys to an element.
        
        Args:
            element_id: ID of the element
            text: Text to send
            
        Raises:
            CommandFailedError: If send keys action fails
        """
        logger.debug(f"Sending keys to element {element_id}: '{text}'")
        self.execute(AppiumCommands.SEND_KEYS, {"elementId": element_id, "text": text})
    
    def get_text(self, element_id: str) -> str:
        """
        Get text from an element.
        
        Args:
            element_id: ID of the element
            
        Returns:
            Element text
            
        Raises:
            CommandFailedError: If get text action fails
        """
        logger.debug(f"Getting text from element: {element_id}")
        result = self.execute(AppiumCommands.GET_ELEMENT_TEXT, {"elementId": element_id})
        return result.get("value", "")
    
    def get_page_source(self) -> str:
        """
        Get the page source.
        
        Returns:
            Page source as string
            
        Raises:
            CommandFailedError: If get page source action fails
        """
        logger.debug("Getting page source")
        result = self.execute(AppiumCommands.GET_PAGE_SOURCE)
        return result.get("value", "")
    
    def take_screenshot(self) -> str:
        """
        Take a screenshot.
        
        Returns:
            Base64 encoded screenshot
            
        Raises:
            CommandFailedError: If screenshot action fails
        """
        logger.debug("Taking screenshot")
        result = self.execute(AppiumCommands.GET_SCREENSHOT)
        return result.get("value", "")
    
    def execute_script(self, script: str, args: List[Any] = None) -> Any:
        """
        Execute JavaScript in the current context.
        
        Args:
            script: JavaScript to execute
            args: Script arguments
            
        Returns:
            Script execution result
            
        Raises:
            CommandFailedError: If script execution fails
        """
        logger.debug(f"Executing script: {script}")
        params = {
            "script": script,
            "args": args or []
        }
        result = self.execute(AppiumCommands.EXECUTE_SCRIPT, params)
        return result.get("value")
