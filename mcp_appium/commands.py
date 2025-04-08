"""
Commands module for MCP Appium
==============================

This module defines all the commands supported by the Appium MCP implementation
and their corresponding HTTP methods and URL paths.
"""

from typing import Dict, Any, Optional


class AppiumCommands:
    """
    Class that defines all the Appium commands supported by the MCP protocol.
    
    Each command defines:
    - HTTP method (GET, POST, DELETE)
    - URL path (with placeholders for parameters)
    - Parameters required/optional
    """
    
    def __init__(self):
        """
        Initialize the commands dictionary with all supported Appium commands.
        """
        # Session commands
        self._commands = {
            # Session management
            "createSession": {
                "method": "POST",
                "url": "/session",
                "parameters": ["capabilities"]
            },
            "getSession": {
                "method": "GET",
                "url": "/session/:session_id",
                "parameters": []
            },
            "getSessions": {
                "method": "GET", 
                "url": "/sessions",
                "parameters": []
            },
            "deleteSession": {
                "method": "DELETE",
                "url": "/session/:session_id",
                "parameters": []
            },
            "getStatus": {
                "method": "GET",
                "url": "/status",
                "parameters": []
            },
            
            # Element interaction
            "findElement": {
                "method": "POST",
                "url": "/session/:session_id/element",
                "parameters": ["using", "value"]
            },
            "findElements": {
                "method": "POST",
                "url": "/session/:session_id/elements",
                "parameters": ["using", "value"]
            },
            "findElementFromElement": {
                "method": "POST",
                "url": "/session/:session_id/element/:element_id/element",
                "parameters": ["using", "value"]
            },
            "findElementsFromElement": {
                "method": "POST",
                "url": "/session/:session_id/element/:element_id/elements",
                "parameters": ["using", "value"]
            },
            "click": {
                "method": "POST",
                "url": "/session/:session_id/element/:element_id/click",
                "parameters": []
            },
            "clear": {
                "method": "POST",
                "url": "/session/:session_id/element/:element_id/clear",
                "parameters": []
            },
            "sendKeys": {
                "method": "POST",
                "url": "/session/:session_id/element/:element_id/value",
                "parameters": ["text", "value"]
            },
            "getText": {
                "method": "GET",
                "url": "/session/:session_id/element/:element_id/text",
                "parameters": []
            },
            "getAttribute": {
                "method": "GET",
                "url": "/session/:session_id/element/:element_id/attribute/:name",
                "parameters": ["name"]
            },
            "isDisplayed": {
                "method": "GET",
                "url": "/session/:session_id/element/:element_id/displayed",
                "parameters": []
            },
            "isEnabled": {
                "method": "GET",
                "url": "/session/:session_id/element/:element_id/enabled",
                "parameters": []
            },
            "isSelected": {
                "method": "GET",
                "url": "/session/:session_id/element/:element_id/selected",
                "parameters": []
            },
            
            # Navigation
            "getCurrentUrl": {
                "method": "GET",
                "url": "/session/:session_id/url",
                "parameters": []
            },
            "navigateTo": {
                "method": "POST",
                "url": "/session/:session_id/url",
                "parameters": ["url"]
            },
            "back": {
                "method": "POST",
                "url": "/session/:session_id/back",
                "parameters": []
            },
            
            # Context
            "getContexts": {
                "method": "GET",
                "url": "/session/:session_id/contexts",
                "parameters": []
            },
            "getCurrentContext": {
                "method": "GET",
                "url": "/session/:session_id/context",
                "parameters": []
            },
            "switchContext": {
                "method": "POST",
                "url": "/session/:session_id/context",
                "parameters": ["name"]
            },
            
            # Mobile specific
            "getOrientation": {
                "method": "GET",
                "url": "/session/:session_id/orientation",
                "parameters": []
            },
            "setOrientation": {
                "method": "POST",
                "url": "/session/:session_id/orientation",
                "parameters": ["orientation"]
            },
            "getGeolocation": {
                "method": "GET",
                "url": "/session/:session_id/location",
                "parameters": []
            },
            "setGeolocation": {
                "method": "POST",
                "url": "/session/:session_id/location",
                "parameters": ["latitude", "longitude", "altitude"]
            },
            
            # App management
            "launchApp": {
                "method": "POST",
                "url": "/session/:session_id/appium/app/launch",
                "parameters": []
            },
            "closeApp": {
                "method": "POST",
                "url": "/session/:session_id/appium/app/close",
                "parameters": []
            },
            "resetApp": {
                "method": "POST",
                "url": "/session/:session_id/appium/app/reset",
                "parameters": []
            },
            "installApp": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/install_app",
                "parameters": ["appPath"]
            },
            "removeApp": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/remove_app",
                "parameters": ["appId"]
            },
            "isAppInstalled": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/app_installed",
                "parameters": ["bundleId"]
            },
            
            # Device interaction
            "shake": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/shake",
                "parameters": []
            },
            "lock": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/lock",
                "parameters": ["seconds"]
            },
            "unlock": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/unlock",
                "parameters": []
            },
            "pressKeyCode": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/press_keycode",
                "parameters": ["keycode", "metastate"]
            },
            "longPressKeyCode": {
                "method": "POST", 
                "url": "/session/:session_id/appium/device/long_press_keycode",
                "parameters": ["keycode", "metastate"]
            },
            
            # Touch actions
            "tap": {
                "method": "POST",
                "url": "/session/:session_id/appium/tap",
                "parameters": ["x", "y"]
            },
            "swipe": {
                "method": "POST",
                "url": "/session/:session_id/appium/device/swipe",
                "parameters": ["startX", "startY", "endX", "endY", "duration"]
            },
            "touchDown": {
                "method": "POST",
                "url": "/session/:session_id/touch/down",
                "parameters": ["x", "y"]
            },
            "touchUp": {
                "method": "POST",
                "url": "/session/:session_id/touch/up",
                "parameters": ["x", "y"]
            },
            "touchMove": {
                "method": "POST",
                "url": "/session/:session_id/touch/move",
                "parameters": ["x", "y"]
            },
            
            # Alert handling
            "getAlertText": {
                "method": "GET",
                "url": "/session/:session_id/alert/text",
                "parameters": []
            },
            "acceptAlert": {
                "method": "POST",
                "url": "/session/:session_id/alert/accept",
                "parameters": []
            },
            "dismissAlert": {
                "method": "POST",
                "url": "/session/:session_id/alert/dismiss",
                "parameters": []
            },
            
            # Screen capture
            "screenshot": {
                "method": "GET",
                "url": "/session/:session_id/screenshot",
                "parameters": []
            },
            
            # Timeouts
            "setTimeouts": {
                "method": "POST",
                "url": "/session/:session_id/timeouts",
                "parameters": ["script", "pageLoad", "implicit"]
            },
            
            # Execute
            "executeScript": {
                "method": "POST",
                "url": "/session/:session_id/execute/sync",
                "parameters": ["script", "args"]
            },
            "executeAsyncScript": {
                "method": "POST",
                "url": "/session/:session_id/execute/async",
                "parameters": ["script", "args"]
            }
        }
    
    def get_command_info(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific command.
        
        Args:
            command: The command name
            
        Returns:
            Dict containing method, url and parameters for the command,
            or None if the command is not found
        """
        return self._commands.get(command)
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all commands supported by the MCP Appium implementation.
        
        Returns:
            Dict containing all commands
        """
        return self._commands
