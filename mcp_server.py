#!/usr/bin/env python3
"""
MCP Appium Server
================

This module implements an MCP (Model Context Protocol) server for Appium mobile testing
and web browser automation using Playwright.

It provides tools for:
1. Connecting to and controlling mobile devices
2. Automating web browsers
3. Capturing screenshots and page sources
4. Analyzing UI layouts with AI
5. Generating test scripts based on app/web exploration
6. Executing natural language commands against mobile devices and browsers
"""

import os
import logging
import json
import base64
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_appium.client import AppiumClient
from mcp_appium.errors import AppiumMCPError
from mcp_appium.ai_integration import (
    MCPAIIntegration, AIProvider, AIModelConfig, AIProviderError
)
from mcp_appium.browser import server_integration as browser_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
app = FastMCP(
    name="MCP Appium",
    instructions="""
    This is an MCP server that provides tools for mobile app testing with Appium
    and web browser automation with Playwright.
    
    You can use these tools to:
    - Connect to and control mobile devices
    - Automate web browsers
    - Take screenshots and capture page/screen sources
    - Find and interact with elements
    - Analyze app/web screens with AI
    - Generate test scripts based on app/web exploration
    """
)

# Initialize Appium client and browser
client = None
ai_integration = None

def initialize_appium():
    """Initialize the Appium client."""
    global client
    appium_url = os.environ.get("APPIUM_URL", "http://localhost:4723")
    
    try:
        client = AppiumClient(base_url=appium_url)
        logger.info("Initialized Appium client with URL: %s", appium_url)
        return True
    except Exception as e:
        logger.error("Failed to initialize Appium client: %s", str(e))
        return False

def initialize_ai():
    """Initialize the AI integration."""
    global ai_integration
    
    # Determine which AI provider to use based on available credentials
    if os.environ.get("OPENAI_API_KEY"):
        provider = AIProvider.OPENAI
        api_key = os.environ.get("OPENAI_API_KEY")
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    elif os.environ.get("GEMINI_API_KEY"):
        provider = AIProvider.GEMINI
        api_key = os.environ.get("GEMINI_API_KEY")
        model = os.environ.get("GEMINI_MODEL", "gemini-pro")
    elif os.environ.get("OLLAMA_BASE_URL"):
        provider = AIProvider.OLLAMA
        api_key = os.environ.get("OLLAMA_BASE_URL")
        model = os.environ.get("OLLAMA_MODEL", "mistral:7b-instruct")
    else:
        # Default to OpenAI, but will fail if no API key
        provider = AIProvider.OPENAI
        api_key = None
        model = "gpt-4o"
    
    # Configure the AI model
    config = AIModelConfig(
        temperature=0.7,
        max_tokens=1024,
        timeout=30,
        max_retries=2
    )
    
    try:
        ai_integration = MCPAIIntegration(
            provider=provider,
            api_key=api_key,
            model=model,
            config=config
        )
        logger.info("Initialized AI integration with provider: %s", provider.value)
        return True
    except AIProviderError as e:
        logger.error("Failed to initialize AI integration: %s", str(e))
        return False


# ====== MCP Tools for Appium Actions ======

@app.tool()
def connect_to_device(capabilities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connect to a mobile device with the specified capabilities.
    
    Args:
        capabilities: A dictionary of Appium capabilities
        
    Returns:
        A dictionary with connection status and session information
    """
    if not client:
        if not initialize_appium():
            return {"status": "error", "message": "Failed to initialize Appium client"}
    
    try:
        session = client.create_session(capabilities)
        return {
            "status": "success", 
            "session_id": session.session_id,
            "capabilities": session.capabilities
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def take_screenshot() -> Dict[str, Any]:
    """
    Take a screenshot of the current screen.
    
    Returns:
        A dictionary with status and base64-encoded screenshot
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    try:
        screenshot = client.session.get_screenshot()
        return {
            "status": "success",
            "screenshot": screenshot
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def get_page_source() -> Dict[str, Any]:
    """
    Get the XML page source of the current screen.
    
    Returns:
        A dictionary with status and page source
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    try:
        source = client.session.get_page_source()
        return {
            "status": "success",
            "source": source
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def find_element(by: str, value: str) -> Dict[str, Any]:
    """
    Find an element on the screen.
    
    Args:
        by: The locator strategy (id, xpath, accessibility id, etc.)
        value: The locator value
        
    Returns:
        A dictionary with element information
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    try:
        element = client.session.find_element(by, value)
        return {
            "status": "success",
            "element_id": element.element_id,
            "text": element.text,
            "location": element.location,
            "size": element.size,
            "attributes": element.get_attributes()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def tap_element(by: str, value: str) -> Dict[str, Any]:
    """
    Tap an element on the screen.
    
    Args:
        by: The locator strategy (id, xpath, accessibility id, etc.)
        value: The locator value
        
    Returns:
        A dictionary with status information
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    try:
        element = client.session.find_element(by, value)
        element.click()
        return {"status": "success", "message": f"Tapped element: {by}={value}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def input_text(by: str, value: str, text: str) -> Dict[str, Any]:
    """
    Input text into an element.
    
    Args:
        by: The locator strategy (id, xpath, accessibility id, etc.)
        value: The locator value
        text: The text to input
        
    Returns:
        A dictionary with status information
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    try:
        element = client.session.find_element(by, value)
        element.clear()
        element.send_keys(text)
        return {"status": "success", "message": f"Input text into element: {by}={value}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def swipe(
    start_x: int, 
    start_y: int, 
    end_x: int, 
    end_y: int,
    duration: int = 500
) -> Dict[str, Any]:
    """
    Perform a swipe gesture.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        duration: Duration of swipe in milliseconds
        
    Returns:
        A dictionary with status information
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    try:
        client.session.swipe(start_x, start_y, end_x, end_y, duration)
        return {"status": "success", "message": "Swipe performed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def press_back() -> Dict[str, Any]:
    """
    Press the back button.
    
    Returns:
        A dictionary with status information
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    try:
        client.session.back()
        return {"status": "success", "message": "Back button pressed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ====== MCP Tools for AI Integration ======

@app.tool()
def describe_screen() -> Dict[str, Any]:
    """
    Describe the current screen using AI.
    
    Returns:
        A dictionary with the screen description
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    if not ai_integration:
        if not initialize_ai():
            return {"status": "error", "message": "Failed to initialize AI integration"}
    
    try:
        source = client.session.get_page_source()
        description = ai_integration.describe_screen(source)
        return {
            "status": "success",
            "description": description
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def suggest_test_actions() -> Dict[str, Any]:
    """
    Suggest test actions for the current screen using AI.
    
    Returns:
        A dictionary with suggested test actions
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    if not ai_integration:
        if not initialize_ai():
            return {"status": "error", "message": "Failed to initialize AI integration"}
    
    try:
        source = client.session.get_page_source()
        suggestions = ai_integration.suggest_test_actions(source)
        return {
            "status": "success",
            "suggestions": suggestions
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def interpret_command(command: str) -> Dict[str, Any]:
    """
    Interpret a natural language command using AI.
    
    Args:
        command: Natural language command
        
    Returns:
        A dictionary with the interpreted command
    """
    if not ai_integration:
        if not initialize_ai():
            return {"status": "error", "message": "Failed to initialize AI integration"}
    
    try:
        context = None
        if client and client.session:
            # Add context if available
            source = client.session.get_page_source()
            context = {"page_source": source}
        
        result = ai_integration.interpret_command(command, context)
        return {
            "status": "success",
            "action": result.get("action"),
            "parameters": result.get("parameters", {})
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.tool()
def generate_test_script(test_goal: str, language: str = "python") -> Dict[str, Any]:
    """
    Generate a test script based on a testing goal.
    
    Args:
        test_goal: Description of what to test
        language: Programming language for the script (python, java, javascript, csharp, ruby, robot)
        
    Returns:
        A dictionary with the generated test script
    """
    if not client or not client.session:
        return {"status": "error", "message": "No active session"}
    
    if not ai_integration:
        if not initialize_ai():
            return {"status": "error", "message": "Failed to initialize AI integration"}
    
    try:
        # Collect information about the app
        source = client.session.get_page_source()
        app_info = {
            "page_source": source,
            "platform": client.session.capabilities.get("platformName", "unknown")
        }
        
        script = ai_integration.generate_test_script_with_interface(
            app_info, test_goal, language
        )
        
        return {
            "status": "success",
            "language": language,
            "script": script
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ====== MCP Tools for Browser Automation ======

@app.tool()
def connect_to_browser(capabilities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connect to a browser with the specified capabilities.
    
    Args:
        capabilities: A dictionary of browser capabilities (browserName, headless, etc.)
        
    Returns:
        A dictionary with connection status and session information
    """
    # Initialize browser
    browser_server.initialize_browser()
    
    # Connect to browser with the provided capabilities
    return browser_server.connect_to_browser(capabilities)


@app.tool()
def navigate_to_url(url: str) -> Dict[str, Any]:
    """
    Navigate to a URL in the browser.
    
    Args:
        url: The URL to navigate to
        
    Returns:
        A dictionary with navigation status
    """
    return browser_server.navigate_to_url(url)


@app.tool()
def get_current_url() -> Dict[str, Any]:
    """
    Get the current URL in the browser.
    
    Returns:
        A dictionary with the current URL
    """
    return browser_server.get_current_url()


@app.tool()
def get_page_title() -> Dict[str, Any]:
    """
    Get the current page title in the browser.
    
    Returns:
        A dictionary with the page title
    """
    return browser_server.get_page_title()


@app.tool()
def get_browser_screenshot() -> Dict[str, Any]:
    """
    Take a screenshot of the current page in the browser.
    
    Returns:
        A dictionary with the screenshot as a base64 string
    """
    return browser_server.get_screenshot()


@app.tool()
def get_browser_page_source() -> Dict[str, Any]:
    """
    Get the HTML source of the current page in the browser.
    
    Returns:
        A dictionary with the page source
    """
    return browser_server.get_page_source()


@app.tool()
def find_browser_element(by: str, value: str) -> Dict[str, Any]:
    """
    Find an element in the browser.
    
    Args:
        by: The method to find the element (id, css selector, xpath)
        value: The selector value
        
    Returns:
        A dictionary with the element information
    """
    return browser_server.find_element(by, value)


@app.tool()
def find_browser_elements(by: str, value: str) -> Dict[str, Any]:
    """
    Find elements in the browser.
    
    Args:
        by: The method to find the elements (id, css selector, xpath)
        value: The selector value
        
    Returns:
        A dictionary with the elements information
    """
    return browser_server.find_elements(by, value)


@app.tool()
def click_browser_element(element_id: str) -> Dict[str, Any]:
    """
    Click on an element in the browser.
    
    Args:
        element_id: The ID of the element to click
        
    Returns:
        A dictionary with the click status
    """
    return browser_server.click_element(element_id)


@app.tool()
def send_keys_to_browser_element(element_id: str, text: str) -> Dict[str, Any]:
    """
    Send keys to an element in the browser.
    
    Args:
        element_id: The ID of the element to send keys to
        text: The text to send
        
    Returns:
        A dictionary with the send keys status
    """
    return browser_server.send_keys_to_element(element_id, text)


@app.tool()
def clear_browser_element(element_id: str) -> Dict[str, Any]:
    """
    Clear an element in the browser.
    
    Args:
        element_id: The ID of the element to clear
        
    Returns:
        A dictionary with the clear status
    """
    return browser_server.clear_element(element_id)


@app.tool()
def get_browser_element_text(element_id: str) -> Dict[str, Any]:
    """
    Get the text of an element in the browser.
    
    Args:
        element_id: The ID of the element to get text from
        
    Returns:
        A dictionary with the element text
    """
    return browser_server.get_element_text(element_id)


@app.tool()
def get_browser_element_attribute(element_id: str, attribute: str) -> Dict[str, Any]:
    """
    Get an attribute of an element in the browser.
    
    Args:
        element_id: The ID of the element to get attribute from
        attribute: The attribute name
        
    Returns:
        A dictionary with the attribute value
    """
    return browser_server.get_element_attribute(element_id, attribute)


@app.tool()
def execute_browser_script(script: str, args: List[Any] = None) -> Dict[str, Any]:
    """
    Execute JavaScript in the browser.
    
    Args:
        script: The JavaScript to execute
        args: Arguments to pass to the script
        
    Returns:
        A dictionary with the script execution result
    """
    return browser_server.execute_script(script, args)


@app.tool()
def browser_back() -> Dict[str, Any]:
    """
    Navigate back in the browser.
    
    Returns:
        A dictionary with the navigation status
    """
    return browser_server.go_back()


@app.tool()
def browser_forward() -> Dict[str, Any]:
    """
    Navigate forward in the browser.
    
    Returns:
        A dictionary with the navigation status
    """
    return browser_server.go_forward()


@app.tool()
def browser_refresh() -> Dict[str, Any]:
    """
    Refresh the current page in the browser.
    
    Returns:
        A dictionary with the refresh status
    """
    return browser_server.refresh_page()


@app.tool()
def create_browser_tab() -> Dict[str, Any]:
    """
    Create a new tab in the browser.
    
    Returns:
        A dictionary with the new tab status
    """
    return browser_server.create_new_tab()


@app.tool()
def switch_browser_tab(tab_index: int) -> Dict[str, Any]:
    """
    Switch to a different tab in the browser.
    
    Args:
        tab_index: The index of the tab to switch to
        
    Returns:
        A dictionary with the tab switch status
    """
    return browser_server.switch_to_tab(tab_index)


@app.tool()
def wait_for_browser_element(by: str, value: str, timeout: int = 30000) -> Dict[str, Any]:
    """
    Wait for an element to be present in the browser.
    
    Args:
        by: The method to find the element (id, css selector, xpath)
        value: The selector value
        timeout: The maximum time to wait in milliseconds
        
    Returns:
        A dictionary with the wait status and element information if found
    """
    return browser_server.wait_for_element(by, value, timeout)


@app.tool()
def disconnect_from_browser() -> Dict[str, Any]:
    """
    Disconnect from the browser.
    
    Returns:
        A dictionary with disconnection status
    """
    return browser_server.disconnect_from_browser()


# ====== Main Entry Point ======

def main():
    """Run the MCP server."""
    import uvicorn
    
    # Initialize services
    initialize_appium()
    initialize_ai()
    
    # Initialize browser
    browser_server.initialize_browser()
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()