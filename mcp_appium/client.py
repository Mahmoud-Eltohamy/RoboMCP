"""
Client module for MCP Appium
============================

This module contains the AppiumClient class which is responsible for managing
the connection to the Appium server and implementing the MCP protocol.
"""

import json
import logging
import os
import requests
import time
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin

from .commands import AppiumCommands
from .errors import (
    AppiumMCPError,
    ConnectionError,
    InvalidArgumentError,
    SessionNotCreatedError,
    TimeoutError
)
from .element import Element
from .models import Session
from .config import DEFAULT_TIMEOUT
from .protocol import MCPRequest, MCPResponse

logger = logging.getLogger(__name__)

class AppiumClient:
    """
    Client for interacting with the Appium server using the Model Context Protocol.
    
    This class provides methods for creating sessions, finding elements, and 
    executing various commands on the mobile application.
    """
    
    def __init__(self, base_url: str = "http://localhost:4723", timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the Appium MCP client.
        
        Args:
            base_url: URL of the Appium server (default: http://localhost:4723)
            timeout: Default timeout for requests in seconds (default: 30)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session_id: Optional[str] = None
        self.session: Optional[Session] = None
        self.commands = AppiumCommands()
        logger.info(f"Initialized AppiumClient with base URL: {base_url}")
    
    def connect(self, url: Optional[str] = None) -> bool:
        """
        Connect to the Appium server.
        
        Args:
            url: Optional URL to connect to (overrides the base_url if provided)
            
        Returns:
            bool: True if connection was successful
            
        Raises:
            ConnectionError: If connection to Appium server fails
        """
        if url:
            self.base_url = url
        
        try:
            response = requests.get(urljoin(self.base_url, "/status"), timeout=self.timeout)
            response.raise_for_status()
            status_data = response.json()
            logger.info(f"Connected to Appium server: {self.base_url}")
            logger.debug(f"Server status: {status_data}")
            return True
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"Failed to connect to Appium server: {str(e)}")
            raise ConnectionError(f"Failed to connect to Appium server: {str(e)}")
    
    def create_session(self, capabilities: Dict[str, Any]) -> Session:
        """
        Create a new Appium session.
        
        Args:
            capabilities: Dictionary containing the desired capabilities
            
        Returns:
            Session: The created session object
            
        Raises:
            SessionNotCreatedError: If session creation fails
        """
        if not capabilities:
            raise InvalidArgumentError("Capabilities cannot be empty")
        
        # Construct the request payload following MCP format
        payload = {
            "capabilities": {
                "alwaysMatch": capabilities,
                "firstMatch": [{}]
            }
        }
        
        try:
            response = requests.post(
                urljoin(self.base_url, "/session"),
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if "value" not in data or "sessionId" not in data.get("value", {}):
                raise SessionNotCreatedError("Invalid response format from Appium server")
            
            session_id = data["value"]["sessionId"]
            self.session_id = session_id
            self.session = Session(
                id=session_id,
                capabilities=data["value"].get("capabilities", {}),
                client=self
            )
            
            logger.info(f"Created new session with ID: {session_id}")
            return self.session
            
        except requests.RequestException as e:
            logger.error(f"Session creation failed: {str(e)}")
            raise SessionNotCreatedError(f"Failed to create Appium session: {str(e)}")
    
    def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an Appium command following the MCP protocol.
        
        Args:
            command: The command to execute
            params: Parameters for the command
            
        Returns:
            Dict: The response from the Appium server
            
        Raises:
            AppiumMCPError: If command execution fails
        """
        if not self.session_id and command != "createSession":
            raise SessionNotCreatedError("No active session")
        
        command_info = self.commands.get_command_info(command)
        if not command_info:
            raise InvalidArgumentError(f"Unknown command: {command}")
        
        # Prepare request based on MCP protocol
        url = command_info["url"]
        method = command_info["method"]
        
        # Replace URL parameters
        if params and ":session_id" in url:
            url = url.replace(":session_id", self.session_id or "")
        
        for key, value in (params or {}).items():
            placeholder = f":{key}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))
                # Remove used parameters
                params = {k: v for k, v in params.items() if k != key}
        
        full_url = urljoin(self.base_url, url)
        
        mcp_request = MCPRequest(
            method=method,
            url=full_url,
            body=params
        )
        
        try:
            logger.debug(f"Executing command: {command} with params: {params}")
            
            if method == "GET":
                response = requests.get(full_url, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(full_url, json=params, timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(full_url, timeout=self.timeout)
            else:
                raise InvalidArgumentError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            # Transform response to MCP format
            mcp_response = MCPResponse.from_appium_response(result)
            
            logger.debug(f"Command result: {mcp_response.data}")
            return mcp_response.data
            
        except requests.RequestException as e:
            logger.error(f"Command execution failed: {str(e)}")
            raise AppiumMCPError(f"Failed to execute command {command}: {str(e)}")
    
    def quit(self):
        """
        Quit the current session and disconnect from the Appium server.
        """
        if self.session_id:
            try:
                self.execute_command("deleteSession")
                logger.info(f"Session {self.session_id} terminated")
            except AppiumMCPError as e:
                logger.warning(f"Error terminating session: {str(e)}")
            finally:
                self.session_id = None
                self.session = None
