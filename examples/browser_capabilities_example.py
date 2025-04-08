#!/usr/bin/env python3
"""
Browser Capabilities Example using MCP Appium
============================================

This example demonstrates how to use the browser automation capabilities of MCP Appium
to perform web testing and automation. It shows how to connect to a browser,
navigate to websites, interact with elements, and extract information.

Note: This example uses a simulation mode when run directly for demonstration purposes.
For actual browser automation, use with Docker or with the MCP server.
"""

import os
import sys
import time
import logging
import base64
import json
from typing import Dict, Any, List
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MCP Appium modules
from mcp_appium.browser import server_integration as browser_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock response data for simulation mode
MOCK_RESPONSES = {
    "initialize_browser": {
        "status": "success",
        "message": "Browser environment initialized"
    },
    "connect_to_browser": {
        "status": "success",
        "sessionId": "browser-session",
        "message": "Connected to browser"
    },
    "navigate_to_url": {
        "status": "success",
        "message": "Navigated to https://www.example.com"
    },
    "get_current_url": {
        "status": "success",
        "url": "https://www.example.com"
    },
    "get_page_title": {
        "status": "success",
        "title": "Example Domain"
    },
    "get_screenshot": {
        "status": "success",
        "screenshot": "base64encodedscreenshot..."
    },
    "get_page_source": {
        "status": "success",
        "source": "<!DOCTYPE html><html><head><title>Example Domain</title></head><body><h1>Example Domain</h1><p>This domain is for use in illustrative examples in documents.</p></body></html>"
    },
    "find_element": {
        "status": "success",
        "element": {
            "element_id": "element-12345",
            "selector": "h1",
            "location": {"x": 100, "y": 100},
            "size": {"width": 200, "height": 50}
        }
    },
    "find_elements": {
        "status": "success",
        "elements": [
            {
                "element_id": "element-12345",
                "selector": "h1",
                "location": {"x": 100, "y": 100},
                "size": {"width": 200, "height": 50}
            },
            {
                "element_id": "element-67890",
                "selector": "p",
                "location": {"x": 100, "y": 150},
                "size": {"width": 400, "height": 30}
            }
        ]
    }
}


def simulate_response(method_name, **kwargs):
    """Simulate a response for demonstration purposes."""
    logger.info(f"Simulating response for {method_name}")
    
    # Get the mock response
    response = MOCK_RESPONSES.get(method_name, {"status": "success", "message": f"Simulated response for {method_name}"})
    
    # Customize the response based on the method and arguments
    if method_name == "navigate_to_url" and kwargs.get("url"):
        response["message"] = f"Navigated to {kwargs['url']}"
    elif method_name == "click_element" and kwargs.get("element_id"):
        response = {"status": "success", "message": f"Clicked element with ID {kwargs['element_id']}"}
    elif method_name == "send_keys_to_element" and kwargs.get("element_id") and kwargs.get("text"):
        response = {"status": "success", "message": f"Sent text '{kwargs['text']}' to element with ID {kwargs['element_id']}"}
    
    return response


def get_browser_function(method_name):
    """Get the appropriate browser function based on the method name."""
    # Map method names to browser server functions
    method_map = {
        "initialize_browser": browser_server.initialize_browser,
        "connect_to_browser": browser_server.connect_to_browser,
        "navigate_to_url": browser_server.navigate_to_url,
        "get_current_url": browser_server.get_current_url,
        "get_page_title": browser_server.get_page_title,
        "get_screenshot": browser_server.get_screenshot,
        "get_page_source": browser_server.get_page_source,
        "find_element": browser_server.find_element,
        "find_elements": browser_server.find_elements,
        "click_element": browser_server.click_element,
        "send_keys_to_element": browser_server.send_keys_to_element,
        "clear_element": browser_server.clear_element,
        "get_element_text": browser_server.get_element_text,
        "get_element_attribute": browser_server.get_element_attribute,
        "execute_script": browser_server.execute_script,
        "create_new_tab": browser_server.create_new_tab,
        "switch_to_tab": browser_server.switch_to_tab,
        "go_back": browser_server.go_back,
        "go_forward": browser_server.go_forward,
        "refresh_page": browser_server.refresh_page,
        "wait_for_element": browser_server.wait_for_element,
        "disconnect_from_browser": browser_server.disconnect_from_browser
    }
    
    return method_map.get(method_name)


def call_browser_function(method_name, simulate=True, **kwargs):
    """Call a browser function directly or simulate it."""
    if simulate:
        return simulate_response(method_name, **kwargs)
    else:
        # Get the function
        func = get_browser_function(method_name)
        if not func:
            return {"status": "error", "message": f"Unknown method: {method_name}"}
        
        # Call the function with the provided arguments
        return func(**kwargs)


def browser_demo():
    """Run a demonstration of browser capabilities."""
    logger.info("Starting browser capabilities demonstration")
    
    # Use simulation mode by default
    simulate = True
    
    try:
        # Check if we should use real browser connections
        if os.environ.get("USE_REAL_BROWSER") == "1":
            simulate = False
        
        # For Replit, always use simulation mode to avoid browser startup issues
        if "REPL_ID" in os.environ or "REPLIT_WORKSPACE" in os.environ:
            logger.info("Running in Replit environment - forcing simulation mode")
            simulate = True
    except Exception:
        # Fall back to simulation
        simulate = True
    
    # Step 1: Initialize browser environment
    logger.info("Step 1: Initialize browser environment")
    response = call_browser_function("initialize_browser", simulate=simulate)
    logger.info(f"Response: {response}")
    
    # Step 2: Connect to browser
    logger.info("Step 2: Connect to browser")
    capabilities = {
        "browserName": "chromium",
        "headless": True,
        "args": ["--no-sandbox"]
    }
    response = call_browser_function("connect_to_browser", simulate=simulate, capabilities=capabilities)
    logger.info(f"Response: {response}")
    
    # Step 3: Navigate to a URL
    logger.info("Step 3: Navigate to a URL")
    response = call_browser_function("navigate_to_url", simulate=simulate, url="https://www.example.com")
    logger.info(f"Response: {response}")
    
    # Step 4: Get current URL
    logger.info("Step 4: Get current URL")
    response = call_browser_function("get_current_url", simulate=simulate)
    logger.info(f"Response: {response}")
    
    # Step 5: Get page title
    logger.info("Step 5: Get page title")
    response = call_browser_function("get_page_title", simulate=simulate)
    logger.info(f"Response: {response}")
    
    # Step 6: Take screenshot
    logger.info("Step 6: Take screenshot")
    response = call_browser_function("get_screenshot", simulate=simulate)
    logger.info(f"Response status: {response['status']}")
    
    # Step 7: Get page source
    logger.info("Step 7: Get page source")
    response = call_browser_function("get_page_source", simulate=simulate)
    logger.info(f"Response status: {response['status']}")
    
    # Step 8: Find an element
    logger.info("Step 8: Find an element")
    response = call_browser_function("find_element", simulate=simulate, by="tag name", value="h1")
    logger.info(f"Response: {response}")
    
    if response["status"] == "success" and "element" in response:
        element_id = response["element"].get("element_id")
        
        # Step 9: Click on the element
        logger.info("Step 9: Click on the element")
        response = call_browser_function("click_element", simulate=simulate, element_id=element_id)
        logger.info(f"Response: {response}")
        
        # Step 10: Get element text
        logger.info("Step 10: Get element text")
        response = call_browser_function("get_element_text", simulate=simulate, element_id=element_id)
        logger.info(f"Response: {response}")
    
    # Step 11: Find multiple elements
    logger.info("Step 11: Find multiple elements")
    response = call_browser_function("find_elements", simulate=simulate, by="css selector", value="p")
    logger.info(f"Response: {response}")
    
    # Step 12: Execute JavaScript
    logger.info("Step 12: Execute JavaScript")
    script = "return document.title;"
    response = call_browser_function("execute_script", simulate=simulate, script=script)
    logger.info(f"Response: {response}")
    
    # Step 13: Create a new tab
    logger.info("Step 13: Create a new tab")
    response = call_browser_function("create_new_tab", simulate=simulate)
    logger.info(f"Response: {response}")
    
    # Step 14: Navigate to a different URL in the new tab
    logger.info("Step 14: Navigate to a different URL in the new tab")
    response = call_browser_function("navigate_to_url", simulate=simulate, url="https://www.example.org")
    logger.info(f"Response: {response}")
    
    # Step 15: Switch back to the first tab
    logger.info("Step 15: Switch back to the first tab")
    response = call_browser_function("switch_to_tab", simulate=simulate, tab_index=0)
    logger.info(f"Response: {response}")
    
    # Step 16: Go back in history
    logger.info("Step 16: Go back in history")
    response = call_browser_function("go_back", simulate=simulate)
    logger.info(f"Response: {response}")
    
    # Step 17: Go forward in history
    logger.info("Step 17: Go forward in history")
    response = call_browser_function("go_forward", simulate=simulate)
    logger.info(f"Response: {response}")
    
    # Step 18: Refresh the page
    logger.info("Step 18: Refresh the page")
    response = call_browser_function("refresh_page", simulate=simulate)
    logger.info(f"Response: {response}")
    
    # Step 19: Wait for an element
    logger.info("Step 19: Wait for an element")
    response = call_browser_function("wait_for_element", simulate=simulate, by="css selector", value="h1", timeout=5000)
    logger.info(f"Response: {response}")
    
    # Step 20: Disconnect from the browser
    logger.info("Step 20: Disconnect from the browser")
    response = call_browser_function("disconnect_from_browser", simulate=simulate)
    logger.info(f"Response: {response}")
    
    logger.info("Browser capabilities demonstration completed")


if __name__ == "__main__":
    browser_demo()