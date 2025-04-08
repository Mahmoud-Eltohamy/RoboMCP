"""
Protocol module for MCP Appium
==============================

This module contains classes for the MCP protocol messages.
"""

import json
from typing import Dict, Any, Optional, List, Union


class MCPRequest:
    """
    Class representing an MCP request.
    
    This class encapsulates the structure of an MCP request according to
    the Model Context Protocol specification.
    """
    
    def __init__(self, method: str, url: str, body: Optional[Dict[str, Any]] = None):
        """
        Initialize an MCP request.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            url: URL for the request
            body: Request body (optional)
        """
        self.method = method
        self.url = url
        self.body = body or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the MCP request to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the request
        """
        return {
            "method": self.method,
            "url": self.url,
            "body": self.body
        }
    
    def to_json(self) -> str:
        """
        Convert the MCP request to a JSON string.
        
        Returns:
            str: JSON string representation of the request
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPRequest':
        """
        Create an MCP request from a dictionary.
        
        Args:
            data: Dictionary containing the request data
            
        Returns:
            MCPRequest: New MCP request object
        """
        return cls(
            method=data.get("method", "GET"),
            url=data.get("url", ""),
            body=data.get("body")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPRequest':
        """
        Create an MCP request from a JSON string.
        
        Args:
            json_str: JSON string containing the request data
            
        Returns:
            MCPRequest: New MCP request object
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class MCPResponse:
    """
    Class representing an MCP response.
    
    This class encapsulates the structure of an MCP response according to
    the Model Context Protocol specification.
    """
    
    def __init__(self, status: int, value: Any, message: Optional[str] = None):
        """
        Initialize an MCP response.
        
        Args:
            status: Status code (0 for success, non-zero for error)
            value: Response value
            message: Error message (if status is non-zero)
        """
        self.status = status
        self.value = value
        self.message = message
        self.data = {"value": value}
        if status != 0:
            self.data["status"] = status
        if message:
            self.data["message"] = message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the MCP response to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the response
        """
        result = {"value": self.value}
        if self.status != 0:
            result["status"] = self.status
        if self.message:
            result["message"] = self.message
        return result
    
    def to_json(self) -> str:
        """
        Convert the MCP response to a JSON string.
        
        Returns:
            str: JSON string representation of the response
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPResponse':
        """
        Create an MCP response from a dictionary.
        
        Args:
            data: Dictionary containing the response data
            
        Returns:
            MCPResponse: New MCP response object
        """
        status = data.get("status", 0)
        value = data.get("value")
        message = data.get("message")
        return cls(status=status, value=value, message=message)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPResponse':
        """
        Create an MCP response from a JSON string.
        
        Args:
            json_str: JSON string containing the response data
            
        Returns:
            MCPResponse: New MCP response object
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_appium_response(cls, data: Dict[str, Any]) -> 'MCPResponse':
        """
        Create an MCP response from an Appium response.
        
        Args:
            data: Dictionary containing the Appium response data
            
        Returns:
            MCPResponse: New MCP response object
        """
        if "status" in data:
            status = data["status"]
            value = data.get("value")
            message = data.get("message")
        else:
            status = 0
            value = data.get("value")
            message = None
        
        return cls(status=status, value=value, message=message)
