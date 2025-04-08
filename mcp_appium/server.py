"""
Server module for MCP Appium
============================

This module provides a simple server that implements the MCP protocol
for Appium. It can be used as a standalone server or as a library.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import flask
from flask import Flask, request, jsonify

from .client import AppiumClient
from .config import DEFAULT_APPIUM_URL, DEFAULT_PORT
from .protocol import MCPRequest, MCPResponse
from .errors import AppiumMCPError

logger = logging.getLogger(__name__)

class AppiumMCPServer:
    """
    Server that implements the MCP protocol for Appium.
    
    This server acts as a bridge between an MCP client and an Appium server.
    It translates MCP commands to Appium commands and vice versa.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT,
                appium_url: str = DEFAULT_APPIUM_URL):
        """
        Initialize the Appium MCP server.
        
        Args:
            host: The host to bind to (default: 0.0.0.0)
            port: The port to listen on (default: 5000)
            appium_url: The URL of the Appium server (default: http://localhost:4723)
        """
        self.host = host
        self.port = port
        self.appium_url = appium_url
        self.app = Flask(__name__)
        self.client = AppiumClient(appium_url)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Set up routes
        self._setup_routes()
        
        logger.info(f"Initialized AppiumMCPServer at {host}:{port} with Appium URL: {appium_url}")
    
    def _setup_routes(self) -> None:
        """Set up the server routes."""
        app = self.app
        
        @app.route('/status', methods=['GET'])
        def status():
            """Get the server status."""
            try:
                appium_status = self.client.execute_command("getStatus")
                return jsonify({
                    "status": "ok",
                    "appium_status": appium_status,
                    "sessions": list(self.sessions.keys())
                })
            except AppiumMCPError as e:
                logger.error(f"Status check failed: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @app.route('/session', methods=['POST'])
        def create_session():
            """Create a new session."""
            try:
                data = request.json
                if not data or "capabilities" not in data:
                    return jsonify({"error": "Invalid request body"}), 400
                
                capabilities = data["capabilities"].get("alwaysMatch", {})
                first_match = data["capabilities"].get("firstMatch", [{}])[0]
                
                # Merge capabilities
                merged_capabilities = {**first_match, **capabilities}
                
                # Create session
                session_response = self.client.create_session(merged_capabilities)
                session_id = session_response.id
                
                # Store session
                self.sessions[session_id] = {
                    "id": session_id,
                    "capabilities": merged_capabilities
                }
                
                response = MCPResponse(
                    status=0,
                    value={
                        "sessionId": session_id,
                        "capabilities": merged_capabilities
                    }
                )
                
                return jsonify(response.to_dict())
                
            except AppiumMCPError as e:
                logger.error(f"Session creation failed: {str(e)}")
                return jsonify({
                    "status": 1,
                    "value": None,
                    "message": str(e)
                }), 500
        
        @app.route('/session/<session_id>', methods=['DELETE'])
        def delete_session(session_id):
            """Delete a session."""
            try:
                if session_id not in self.sessions:
                    return jsonify({"error": "Session not found"}), 404
                
                self.client.session_id = session_id
                self.client.quit()
                
                # Remove session
                del self.sessions[session_id]
                
                response = MCPResponse(status=0, value=None)
                return jsonify(response.to_dict())
                
            except AppiumMCPError as e:
                logger.error(f"Session deletion failed: {str(e)}")
                return jsonify({
                    "status": 1,
                    "value": None,
                    "message": str(e)
                }), 500
        
        @app.route('/session/<session_id>/element', methods=['POST'])
        def find_element(session_id):
            """Find an element."""
            try:
                if session_id not in self.sessions:
                    return jsonify({"error": "Session not found"}), 404
                
                data = request.json
                if not data or "using" not in data or "value" not in data:
                    return jsonify({"error": "Invalid request body"}), 400
                
                self.client.session_id = session_id
                result = self.client.execute_command(
                    "findElement", 
                    {
                        "using": data["using"],
                        "value": data["value"]
                    }
                )
                
                response = MCPResponse(status=0, value=result.get("value"))
                return jsonify(response.to_dict())
                
            except AppiumMCPError as e:
                logger.error(f"Find element failed: {str(e)}")
                return jsonify({
                    "status": 1,
                    "value": None,
                    "message": str(e)
                }), 500
        
        @app.route('/session/<session_id>/elements', methods=['POST'])
        def find_elements(session_id):
            """Find elements."""
            try:
                if session_id not in self.sessions:
                    return jsonify({"error": "Session not found"}), 404
                
                data = request.json
                if not data or "using" not in data or "value" not in data:
                    return jsonify({"error": "Invalid request body"}), 400
                
                self.client.session_id = session_id
                result = self.client.execute_command(
                    "findElements", 
                    {
                        "using": data["using"],
                        "value": data["value"]
                    }
                )
                
                response = MCPResponse(status=0, value=result.get("value"))
                return jsonify(response.to_dict())
                
            except AppiumMCPError as e:
                logger.error(f"Find elements failed: {str(e)}")
                return jsonify({
                    "status": 1,
                    "value": None,
                    "message": str(e)
                }), 500
        
        @app.route('/session/<session_id>/element/<element_id>/click', methods=['POST'])
        def element_click(session_id, element_id):
            """Click on an element."""
            try:
                if session_id not in self.sessions:
                    return jsonify({"error": "Session not found"}), 404
                
                self.client.session_id = session_id
                result = self.client.execute_command(
                    "click", 
                    {
                        "element_id": element_id
                    }
                )
                
                response = MCPResponse(status=0, value=result.get("value"))
                return jsonify(response.to_dict())
                
            except AppiumMCPError as e:
                logger.error(f"Element click failed: {str(e)}")
                return jsonify({
                    "status": 1,
                    "value": None,
                    "message": str(e)
                }), 500
        
        # Add more routes for other commands as needed
        
        # Generic route for commands that aren't explicitly defined
        @app.route('/session/<session_id>/<path:command>', methods=['GET', 'POST', 'DELETE'])
        def execute_command(session_id, command):
            """Execute a command."""
            try:
                if session_id not in self.sessions:
                    return jsonify({"error": "Session not found"}), 404
                
                self.client.session_id = session_id
                
                # Map the path to a command
                command_map = {
                    "back": "back",
                    "screenshot": "screenshot",
                    "source": "source",
                    "orientation": "getOrientation",
                    "context": "getCurrentContext",
                    "contexts": "getContexts",
                    # Add more mappings as needed
                }
                
                command_name = command_map.get(command, command)
                
                params = {}
                if request.method == 'POST':
                    data = request.json or {}
                    params.update(data)
                
                result = self.client.execute_command(command_name, params)
                
                response = MCPResponse(status=0, value=result.get("value"))
                return jsonify(response.to_dict())
                
            except AppiumMCPError as e:
                logger.error(f"Command execution failed: {str(e)}")
                return jsonify({
                    "status": 1,
                    "value": None,
                    "message": str(e)
                }), 500
    
    def start(self) -> None:
        """Start the server."""
        try:
            # Connect to Appium server first
            self.client.connect(self.appium_url)
            
            # Start the Flask app
            self.app.run(host=self.host, port=self.port, debug=True)
            
        except AppiumMCPError as e:
            logger.error(f"Failed to start server: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error starting server: {str(e)}")
            raise
    
    def stop(self) -> None:
        """Stop the server."""
        # Close all sessions
        for session_id in list(self.sessions.keys()):
            try:
                self.client.session_id = session_id
                self.client.quit()
            except Exception as e:
                logger.warning(f"Error closing session {session_id}: {str(e)}")
        
        # Clear sessions
        self.sessions.clear()
        logger.info("Server stopped")
