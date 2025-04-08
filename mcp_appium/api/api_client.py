"""
API Client Module
===============

This module provides a client for making API requests to RESTful services,
with support for session management and specification-based validation.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

from .openapi_parser import OpenAPIParser
from .api_session import APISession
from .robot_generator import RobotGenerator

logger = logging.getLogger(__name__)


class APIClient:
    """
    Client for making API requests to RESTful services.
    
    This class is responsible for:
    1. Managing API sessions
    2. Loading and using OpenAPI specifications
    3. Making HTTP requests with validation
    4. Generating tests from specifications
    """
    
    def __init__(self):
        """Initialize the API client."""
        self.sessions: Dict[str, APISession] = {}
        self.parser: Optional[OpenAPIParser] = None
    
    def load_specification(self, spec_path: str) -> bool:
        """
        Load an OpenAPI specification.
        
        Args:
            spec_path: Path to the OpenAPI specification file or URL
            
        Returns:
            bool: True if the specification was loaded successfully, False otherwise
        """
        self.parser = OpenAPIParser()
        return self.parser.load_spec(spec_path)
    
    def create_session(self, session_id: str, base_url: Optional[str] = None, auth: Optional[Dict[str, Any]] = None) -> APISession:
        """
        Create a new API session.
        
        Args:
            session_id: Identifier for the session
            base_url: Base URL for API requests (optional)
            auth: Authentication details (optional)
            
        Returns:
            APISession: The created session
        """
        # Use base URL from specification if not provided
        if not base_url and self.parser:
            base_url = self.parser.get_base_url()
        
        # Create a new session
        session = APISession(session_id, base_url, auth)
        self.sessions[session_id] = session
        
        logger.info(f"Created API session: {session_id}")
        return session
    
    def close_session(self, session_id: str) -> bool:
        """
        Close an API session.
        
        Args:
            session_id: Identifier for the session
            
        Returns:
            bool: True if the session was closed successfully, False otherwise
        """
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        # Close the session
        self.sessions[session_id].close()
        del self.sessions[session_id]
        
        logger.info(f"Closed API session: {session_id}")
        return True
    
    def get_session(self, session_id: str) -> Optional[APISession]:
        """
        Get an API session by ID.
        
        Args:
            session_id: Identifier for the session
            
        Returns:
            APISession: The session, or None if not found
        """
        return self.sessions.get(session_id)
    
    def execute_request(self, 
                       path: str, 
                       method: str, 
                       params: Optional[Dict[str, Any]] = None, 
                       data: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None,
                       session_id: Optional[str] = None) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Execute an API request.
        
        Args:
            path: The endpoint path
            method: The HTTP method
            params: Query parameters (optional)
            data: Request body (optional)
            headers: Request headers (optional)
            session_id: Identifier for the session (optional)
            
        Returns:
            Tuple: (status_code, response_data, response_headers)
        """
        # Get the session
        if not session_id and self.sessions:
            # Use the first session if not specified
            session_id = next(iter(self.sessions))
        
        if not session_id or session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return 400, {"error": "Session not found"}, {}
        
        session = self.sessions[session_id]
        
        try:
            # Execute the request
            status_code, response_data, response_headers = session.execute_request(
                path, method, params, data, headers
            )
            
            # Validate the response against the specification if available
            if self.parser and status_code >= 200 and status_code < 300:
                is_valid = self.parser.validate_response(path, method, status_code, response_data)
                if not is_valid:
                    logger.warning(f"Response validation failed for {method} {path}")
            
            return status_code, response_data, response_headers
            
        except Exception as e:
            logger.error(f"Error executing request: {str(e)}")
            return 500, {"error": str(e)}, {}
    
    def generate_robot_tests(self, output_file: str) -> bool:
        """
        Generate Robot Framework tests from the loaded specification.
        
        Args:
            output_file: Path to save the generated Robot Framework test suite
            
        Returns:
            bool: True if generation was successful, False otherwise
        """
        if not self.parser:
            logger.error("No specification loaded")
            return False
        
        generator = RobotGenerator(self.parser)
        return generator.generate_robot_suite(output_file)
    
    def validate_specification(self) -> Dict[str, Any]:
        """
        Validate the loaded specification.
        
        Returns:
            Dict: Validation results
        """
        if not self.parser:
            return {"error": "No specification loaded"}
        
        # Basic validation
        results = {
            "valid": True,
            "info": True,
            "paths": True,
            "servers": True,
            "issues": []
        }
        
        # Check info section
        info = self.parser.info
        if not info:
            results["info"] = False
            results["valid"] = False
            results["issues"].append("Missing API information")
        
        # Check paths section
        paths = self.parser.paths
        if not paths:
            results["paths"] = False
            results["valid"] = False
            results["issues"].append("No API endpoints defined")
        
        # Check servers section
        servers = self.parser.servers
        if not servers:
            results["servers"] = False
            results["issues"].append("No servers defined")
        
        return results