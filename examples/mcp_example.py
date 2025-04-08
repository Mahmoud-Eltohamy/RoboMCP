#!/usr/bin/env python3
"""
MCP Protocol Example for MCP Appium
==================================

This module demonstrates how to use the MCP Protocol to interact with the MCP Appium server.
It shows how to:
1. Connect to the MCP server
2. Use the MCP tools to control a mobile device
3. Leverage AI capabilities for mobile test automation
"""

import os
import sys
import argparse
import json
import base64
import time
from typing import Dict, Any, List

import requests

# Default server URL
DEFAULT_SERVER_URL = "http://localhost:5000"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MCP Appium MCP Protocol Example")
    
    parser.add_argument(
        "--server-url",
        default=os.environ.get("MCP_SERVER_URL", DEFAULT_SERVER_URL),
        help=f"URL of the MCP server (default: {DEFAULT_SERVER_URL})"
    )
    
    parser.add_argument(
        "--platform",
        choices=["android", "ios"],
        default="android",
        help="Mobile platform (default: android)"
    )
    
    parser.add_argument(
        "--app",
        help="Path to the mobile app to test"
    )
    
    return parser.parse_args()

def call_mcp_tool(server_url: str, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Call an MCP tool on the server.
    
    Args:
        server_url: URL of the MCP server
        tool_name: Name of the tool to call
        params: Parameters for the tool
    
    Returns:
        Dictionary with the tool result
    """
    if params is None:
        params = {}
    
    payload = {
        "name": tool_name,
        "arguments": params
    }
    
    try:
        response = requests.post(
            f"{server_url}/mcp/tool",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling MCP tool: {str(e)}")
        return {"error": str(e)}

def get_capabilities(args) -> Dict[str, Any]:
    """
    Get the desired capabilities based on the platform and app.
    
    Args:
        args: Command line arguments
    
    Returns:
        Dict: Desired capabilities
    """
    capabilities = {
        "platformName": args.platform.capitalize(),
        "automationName": "UiAutomator2" if args.platform == "android" else "XCUITest",
        "newCommandTimeout": 300
    }
    
    # Use the Sauce Labs Demo app as default for Android
    if args.platform == "android" and not args.app:
        capabilities["app"] = os.path.abspath("app_tests/sauce_labs_demo/sauce_labs_demo.apk")
    # Use a sample app path for iOS (this is just a placeholder)
    elif args.platform == "ios" and not args.app:
        capabilities["app"] = os.path.abspath("app_tests/sample_ios_app.app")
    # Use the specified app path
    elif args.app:
        capabilities["app"] = os.path.abspath(args.app)
    
    # Additional platform-specific capabilities
    if args.platform == "android":
        capabilities["deviceName"] = "Android Emulator"
        capabilities["appPackage"] = "com.saucelabs.mydemoapp.android"
        capabilities["appActivity"] = ".MainActivity"
    else:  # iOS
        capabilities["deviceName"] = "iPhone Simulator"
        capabilities["platformVersion"] = "15.0"
    
    return capabilities

def connect_to_device(server_url: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connect to a mobile device using the MCP server.
    
    Args:
        server_url: URL of the MCP server
        capabilities: Appium capabilities
    
    Returns:
        Dictionary with the connection result
    """
    print("Connecting to device...")
    result = call_mcp_tool(server_url, "connect_to_device", {"capabilities": capabilities})
    
    if result.get("status") == "success":
        print("Successfully connected to device!")
        print(f"Session ID: {result.get('session_id')}")
    else:
        print(f"Failed to connect to device: {result.get('message')}")
    
    return result

def take_and_save_screenshot(server_url: str, filename: str = "screenshot.png") -> bool:
    """
    Take a screenshot and save it to a file.
    
    Args:
        server_url: URL of the MCP server
        filename: Name of the file to save the screenshot to
    
    Returns:
        True if successful, False otherwise
    """
    print("Taking screenshot...")
    result = call_mcp_tool(server_url, "take_screenshot")
    
    if result.get("status") == "success":
        # Save the screenshot to a file
        with open(filename, "wb") as f:
            f.write(base64.b64decode(result.get("screenshot")))
        print(f"Screenshot saved to {filename}")
        return True
    else:
        print(f"Failed to take screenshot: {result.get('message')}")
        return False

def describe_current_screen(server_url: str) -> str:
    """
    Get an AI-generated description of the current screen.
    
    Args:
        server_url: URL of the MCP server
    
    Returns:
        The screen description
    """
    print("Getting AI description of the current screen...")
    result = call_mcp_tool(server_url, "describe_screen")
    
    if result.get("status") == "success":
        description = result.get("description", "No description available")
        print("\nScreen Description:")
        print("------------------")
        print(description)
        print("------------------\n")
        return description
    else:
        print(f"Failed to get screen description: {result.get('message')}")
        return ""

def get_test_suggestions(server_url: str) -> List[Dict[str, Any]]:
    """
    Get AI-generated test suggestions for the current screen.
    
    Args:
        server_url: URL of the MCP server
    
    Returns:
        A list of test suggestions
    """
    print("Getting AI test suggestions for the current screen...")
    result = call_mcp_tool(server_url, "suggest_test_actions")
    
    if result.get("status") == "success":
        suggestions = result.get("suggestions", [])
        print("\nTest Suggestions:")
        print("-----------------")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion.get('description')}")
        print("-----------------\n")
        return suggestions
    else:
        print(f"Failed to get test suggestions: {result.get('message')}")
        return []

def interpret_natural_language_command(server_url: str, command: str) -> Dict[str, Any]:
    """
    Interpret a natural language command using AI.
    
    Args:
        server_url: URL of the MCP server
        command: Natural language command
    
    Returns:
        The interpreted command as a structured action
    """
    print(f"Interpreting command: '{command}'...")
    result = call_mcp_tool(server_url, "interpret_command", {"command": command})
    
    if result.get("status") == "success":
        action = result.get("action")
        parameters = result.get("parameters", {})
        
        print("\nInterpreted Command:")
        print("--------------------")
        print(f"Action: {action}")
        print("Parameters:")
        for key, value in parameters.items():
            print(f"  {key}: {value}")
        print("--------------------\n")
        
        return {
            "action": action,
            "parameters": parameters
        }
    else:
        print(f"Failed to interpret command: {result.get('message')}")
        return {}

def generate_test_script(server_url: str, test_goal: str, language: str = "python") -> str:
    """
    Generate a test script using AI.
    
    Args:
        server_url: URL of the MCP server
        test_goal: Description of what to test
        language: Programming language for the script
    
    Returns:
        The generated test script
    """
    print(f"Generating {language} test script for goal: '{test_goal}'...")
    result = call_mcp_tool(
        server_url,
        "generate_test_script",
        {"test_goal": test_goal, "language": language}
    )
    
    if result.get("status") == "success":
        script = result.get("script", "")
        
        # Save the script to a file
        file_extension = {
            "python": "py",
            "java": "java",
            "javascript": "js",
            "csharp": "cs",
            "ruby": "rb"
        }.get(language, "txt")
        
        filename = f"generated_test_{int(time.time())}.{file_extension}"
        with open(filename, "w") as f:
            f.write(script)
        
        print(f"\nGenerated test script saved to {filename}")
        return script
    else:
        print(f"Failed to generate test script: {result.get('message')}")
        return ""

def execute_tap(server_url: str, by: str, value: str) -> bool:
    """
    Tap an element on the screen.
    
    Args:
        server_url: URL of the MCP server
        by: The locator strategy
        value: The locator value
    
    Returns:
        True if successful, False otherwise
    """
    print(f"Tapping element: {by}={value}...")
    result = call_mcp_tool(server_url, "tap_element", {"by": by, "value": value})
    
    if result.get("status") == "success":
        print("Tap successful!")
        return True
    else:
        print(f"Failed to tap element: {result.get('message')}")
        return False

def input_text_to_element(server_url: str, by: str, value: str, text: str) -> bool:
    """
    Input text into an element.
    
    Args:
        server_url: URL of the MCP server
        by: The locator strategy
        value: The locator value
        text: The text to input
    
    Returns:
        True if successful, False otherwise
    """
    print(f"Inputting text into element: {by}={value}...")
    result = call_mcp_tool(
        server_url,
        "input_text", 
        {"by": by, "value": value, "text": text}
    )
    
    if result.get("status") == "success":
        print("Text input successful!")
        return True
    else:
        print(f"Failed to input text: {result.get('message')}")
        return False

def execute_action(server_url: str, action: Dict[str, Any]) -> bool:
    """
    Execute an action based on the AI interpretation.
    
    Args:
        server_url: URL of the MCP server
        action: The action to execute
    
    Returns:
        True if successful, False otherwise
    """
    action_type = action.get("action")
    params = action.get("parameters", {})
    
    if action_type == "tap":
        return execute_tap(server_url, params.get("by"), params.get("value"))
    elif action_type == "input":
        return input_text_to_element(
            server_url, 
            params.get("by"), 
            params.get("value"), 
            params.get("text")
        )
    elif action_type == "swipe":
        print("Swiping on screen...")
        result = call_mcp_tool(
            server_url,
            "swipe",
            {
                "start_x": params.get("start_x"),
                "start_y": params.get("start_y"),
                "end_x": params.get("end_x"),
                "end_y": params.get("end_y"),
                "duration": params.get("duration", 500)
            }
        )
        return result.get("status") == "success"
    elif action_type == "back":
        print("Pressing back button...")
        result = call_mcp_tool(server_url, "press_back")
        return result.get("status") == "success"
    else:
        print(f"Unknown action type: {action_type}")
        return False

def run_demo(server_url: str, capabilities: Dict[str, Any]):
    """
    Run a demonstration of the MCP Appium features.
    
    Args:
        server_url: URL of the MCP server
        capabilities: Appium capabilities
    """
    # Step 1: Connect to the device
    result = connect_to_device(server_url, capabilities)
    if result.get("status") != "success":
        print("Failed to connect to device. Exiting.")
        return
    
    # Step 2: Wait for app to load
    print("Waiting for app to load...")
    time.sleep(5)
    
    # Step 3: Take a screenshot
    take_and_save_screenshot(server_url)
    
    # Step 4: Get a description of the current screen
    describe_current_screen(server_url)
    
    # Step 5: Get test suggestions
    get_test_suggestions(server_url)
    
    # Step 6: Demonstrate natural language command interpretation
    if capabilities["platformName"].lower() == "android":
        # For Sauce Labs Demo app on Android
        command = "Tap on the first product in the list"
        interpreted = interpret_natural_language_command(server_url, command)
        if interpreted:
            execute_action(server_url, interpreted)
            # Allow time for navigation
            time.sleep(2)
            # Take another screenshot to show the result
            take_and_save_screenshot(server_url, "after_tap.png")
            # Get a description of the new screen
            describe_current_screen(server_url)
    
    # Step 7: Generate a test script
    if capabilities["platformName"].lower() == "android":
        # For Sauce Labs Demo app on Android
        test_goal = "Test the product details page functionality"
        generate_test_script(server_url, test_goal)

def main():
    """Run the MCP Appium MCP Protocol example."""
    args = parse_args()
    capabilities = get_capabilities(args)
    
    # Print the configuration
    print("\nMCP Appium MCP Protocol Example")
    print("================================")
    print(f"Server URL: {args.server_url}")
    print(f"Platform: {args.platform}")
    print(f"App: {capabilities.get('app')}")
    print("================================\n")
    
    # Run the demo
    run_demo(args.server_url, capabilities)

if __name__ == "__main__":
    main()