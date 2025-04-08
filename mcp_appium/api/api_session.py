"""
API Session Module
================

This module provides a session class for making API requests and managing
authentication.
"""

import logging
import json
import urllib.parse
from typing import Dict, List, Any, Optional, Tuple, Union

import requests

logger = logging.getLogger(__name__)


class APISession:
    """
    Session for making API requests.
    
    This class provides functionality for:
    1. Managing API authentication
    2. Making HTTP requests
    3. Handling request/response headers
    4. Processing response data
    """
    
    def __init__(self, session_id: str, base_url: Optional[str] = None, auth: Optional[Dict[str, Any]] = None):
        """
        Initialize the API session.
        
        Args:
            session_id: Identifier for the session
            base_url: Base URL for API requests
            auth: Authentication details (optional)
        """
        self.session_id = session_id
        self.base_url = base_url or ""
        self.auth = auth or {}
        self.session = requests.Session()
        self.headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Apply authentication if provided
        if auth:
            self.set_auth(auth)
    
    def set_auth(self, auth: Dict[str, Any]) -> None:
        """
        Set authentication for the session.
        
        Args:
            auth: Authentication details
        """
        self.auth = auth
        
        # Handle different authentication types
        auth_type = auth.get("type", "")
        
        if auth_type == "basic":
            # Basic authentication
            username = auth.get("username", "")
            password = auth.get("password", "")
            self.session.auth = (username, password)
            
        elif auth_type == "bearer":
            # Bearer token authentication
            token = auth.get("token", "")
            if token:
                self.headers["Authorization"] = f"Bearer {token}"
                
        elif auth_type == "api_key":
            # API key authentication
            api_key = auth.get("key", "")
            header_name = auth.get("header_name", "X-API-Key")
            if api_key:
                self.headers[header_name] = api_key
                
        elif auth_type == "oauth":
            # OAuth authentication (simplified)
            token = auth.get("access_token", "")
            if token:
                self.headers["Authorization"] = f"Bearer {token}"
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """
        Set default headers for the session.
        
        Args:
            headers: Dictionary of headers
        """
        self.headers.update(headers)
    
    def execute_request(self, 
                       path: str, 
                       method: str, 
                       params: Optional[Dict[str, Any]] = None, 
                       data: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Execute an API request.
        
        Args:
            path: The endpoint path
            method: The HTTP method
            params: Query parameters (optional)
            data: Request body (optional)
            headers: Request headers (optional)
            
        Returns:
            Tuple: (status_code, response_data, response_headers)
        """
        # Build the full URL
        url = self._build_url(path)
        
        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare request body
        json_data = None
        if data:
            json_data = data
        
        try:
            # Execute the request
            method = method.upper()
            logger.info(f"Executing {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=request_headers
            )
            
            # Get response data
            if response.text:
                try:
                    # Try to parse response as JSON
                    response_data = response.json()
                except json.JSONDecodeError:
                    # If not JSON, return text in a dict
                    response_data = {"text": response.text}
            else:
                response_data = {}
            
            # Get response headers
            response_headers = dict(response.headers)
            
            return response.status_code, response_data, response_headers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return 500, {"error": str(e)}, {}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return 500, {"error": str(e)}, {}
    
    def _build_url(self, path: str) -> str:
        """
        Build a full URL from the base URL and path.
        
        Args:
            path: The endpoint path
            
        Returns:
            str: The full URL
        """
        # Check if path is already a full URL
        if path.startswith("http://") or path.startswith("https://"):
            return path
        
        # Handle leading slash in path
        if path.startswith("/") and self.base_url.endswith("/"):
            path = path[1:]
        elif not path.startswith("/") and not self.base_url.endswith("/"):
            path = f"/{path}"
        
        # Combine base URL and path
        return urllib.parse.urljoin(self.base_url, path)
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()