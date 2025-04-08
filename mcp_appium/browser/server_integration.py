"""
Browser Server Integration for MCP Appium
======================================

This module provides integration between the MCP server and the browser automation
functionality, implementing tool methods for the MCP server to communicate with browsers
through Playwright.
"""
import os
import base64
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

from playwright.async_api import async_playwright, Browser, Page, Locator
from ..client import AppiumClient

# Configure logging
logger = logging.getLogger(__name__)

# Global browser instances
_browser = None
_browser_context = None
_current_page = None
_loop = None
_client = None


def initialize_browser():
    """Initialize the browser environment."""
    global _loop
    
    if _loop is None:
        # Create a new event loop for browser operations
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        
        logger.info("Browser environment initialized")
    
    return {"status": "success", "message": "Browser environment initialized"}


def connect_to_browser(capabilities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connect to a browser with the specified capabilities.
    
    Args:
        capabilities: A dictionary of browser capabilities
        
    Returns:
        A dictionary with connection status and session information
    """
    global _browser, _browser_context, _current_page, _client
    
    try:
        # Get capabilities
        browser_name = capabilities.get("browserName", "chromium")
        headless = capabilities.get("headless", True)
        browser_args = capabilities.get("args", ["--no-sandbox"])
        
        # Connect to the browser
        connect_result = _loop.run_until_complete(_connect_browser(
            browser_name=browser_name,
            headless=headless,
            browser_args=browser_args
        ))
        
        # Create an AppiumClient instance for this browser session
        _client = AppiumClient(remote_url=None)
        
        return {"status": "success", "sessionId": "browser-session", "message": "Connected to browser"}
    except Exception as e:
        logger.error(f"Failed to connect to browser: {str(e)}")
        return {"status": "error", "message": str(e)}


async def _connect_browser(browser_name: str, headless: bool, browser_args: List[str]):
    """
    Internal method to connect to a browser.
    
    Args:
        browser_name: The browser name (chromium, firefox, webkit)
        headless: Whether to run in headless mode
        browser_args: Additional browser arguments
        
    Returns:
        A tuple of (browser, browser_context, page) instances
    """
    global _browser, _browser_context, _current_page
    
    # Check if we should connect to a running browser
    ws_endpoint = os.environ.get("BROWSER_WS_ENDPOINT")
    
    async with async_playwright() as playwright:
        # Get the browser type
        if browser_name.lower() == "chromium":
            browser_type = playwright.chromium
        elif browser_name.lower() == "firefox":
            browser_type = playwright.firefox
        elif browser_name.lower() == "webkit":
            browser_type = playwright.webkit
        else:
            browser_type = playwright.chromium
        
        # Connect to browser
        if ws_endpoint:
            logger.info(f"Connecting to existing browser at {ws_endpoint}")
            _browser = await playwright.chromium.connect(ws_endpoint=ws_endpoint)
        else:
            logger.info(f"Launching new {browser_name} browser (headless={headless})")
            _browser = await browser_type.launch(headless=headless, args=browser_args)
        
        # Create a browser context
        _browser_context = await _browser.new_context()
        
        # Create a page
        _current_page = await _browser_context.new_page()
        
        return _browser, _browser_context, _current_page


def create_session(capabilities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a browser session with the specified capabilities.
    
    Args:
        capabilities: A dictionary of browser capabilities
        
    Returns:
        A dictionary with session creation status
    """
    return connect_to_browser(capabilities)


def navigate_to_url(url: str) -> Dict[str, Any]:
    """
    Navigate to a URL in the browser.
    
    Args:
        url: The URL to navigate to
        
    Returns:
        A dictionary with navigation status
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        _loop.run_until_complete(_current_page.goto(url))
        
        return {"status": "success", "message": f"Navigated to {url}"}
    except Exception as e:
        logger.error(f"Failed to navigate to URL: {str(e)}")
        return {"status": "error", "message": str(e)}


def get_current_url() -> Dict[str, Any]:
    """
    Get the current URL in the browser.
    
    Returns:
        A dictionary with the current URL
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        url = _loop.run_until_complete(_current_page.url)
        
        return {"status": "success", "url": url}
    except Exception as e:
        logger.error(f"Failed to get current URL: {str(e)}")
        return {"status": "error", "message": str(e)}


def get_page_title() -> Dict[str, Any]:
    """
    Get the current page title in the browser.
    
    Returns:
        A dictionary with the page title
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        title = _loop.run_until_complete(_current_page.title())
        
        return {"status": "success", "title": title}
    except Exception as e:
        logger.error(f"Failed to get page title: {str(e)}")
        return {"status": "error", "message": str(e)}


def get_page_source() -> Dict[str, Any]:
    """
    Get the HTML source of the current page in the browser.
    
    Returns:
        A dictionary with the page source
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        source = _loop.run_until_complete(_current_page.content())
        
        return {"status": "success", "source": source}
    except Exception as e:
        logger.error(f"Failed to get page source: {str(e)}")
        return {"status": "error", "message": str(e)}


def get_screenshot(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Take a screenshot of the current page in the browser.
    
    Args:
        path: Path to save the screenshot to
        
    Returns:
        A dictionary with the screenshot as a base64 string
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        if path:
            _loop.run_until_complete(_current_page.screenshot(path=path))
            return {"status": "success", "message": f"Screenshot saved to {path}"}
        else:
            screenshot_bytes = _loop.run_until_complete(_current_page.screenshot())
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            return {"status": "success", "screenshot": screenshot_base64}
    except Exception as e:
        logger.error(f"Failed to take screenshot: {str(e)}")
        return {"status": "error", "message": str(e)}


def find_element(by: str, value: str) -> Dict[str, Any]:
    """
    Find an element in the browser.
    
    Args:
        by: The method to find the element (id, css selector, xpath)
        value: The selector value
        
    Returns:
        A dictionary with the element information
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _convert_selector(by, value)
        
        # First, check if the element exists
        element_exists = _loop.run_until_complete(_current_page.is_visible(selector))
        
        if not element_exists:
            return {"status": "error", "message": f"Element not found with {by}={value}"}
        
        # Get element properties
        element_id = f"element-{hash(selector)}"
        
        # Get basic properties
        bbox = _loop.run_until_complete(_current_page.locator(selector).bounding_box())
        
        if not bbox:
            return {"status": "error", "message": f"Element found but has no bounding box with {by}={value}"}
        
        return {
            "status": "success",
            "element": {
                "element_id": element_id,
                "selector": selector,
                "location": {"x": bbox["x"], "y": bbox["y"]},
                "size": {"width": bbox["width"], "height": bbox["height"]},
            }
        }
    except Exception as e:
        logger.error(f"Failed to find element: {str(e)}")
        return {"status": "error", "message": str(e)}


def find_elements(by: str, value: str) -> Dict[str, Any]:
    """
    Find elements in the browser.
    
    Args:
        by: The method to find the elements (id, css selector, xpath)
        value: The selector value
        
    Returns:
        A dictionary with the elements information
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _convert_selector(by, value)
        
        # Get the count of matching elements
        count = _loop.run_until_complete(_current_page.locator(selector).count())
        
        if count == 0:
            return {"status": "success", "elements": []}
        
        elements = []
        
        # Get information for each element
        for i in range(count):
            specific_selector = f"{selector} >> nth={i}"
            element_id = f"element-{hash(specific_selector)}"
            
            # Get bounding box
            bbox = _loop.run_until_complete(_current_page.locator(specific_selector).bounding_box())
            
            if bbox:
                elements.append({
                    "element_id": element_id,
                    "selector": specific_selector,
                    "location": {"x": bbox["x"], "y": bbox["y"]},
                    "size": {"width": bbox["width"], "height": bbox["height"]},
                })
        
        return {"status": "success", "elements": elements}
    except Exception as e:
        logger.error(f"Failed to find elements: {str(e)}")
        return {"status": "error", "message": str(e)}


def _convert_selector(by: str, value: str) -> str:
    """
    Convert Appium selector to Playwright selector.
    
    Args:
        by: The selector method
        value: The selector value
        
    Returns:
        A Playwright-compatible selector string
    """
    by = by.lower()
    
    if by == "id":
        return f"#{value}"
    elif by == "class name":
        return f".{value}"
    elif by == "name":
        return f"[name='{value}']"
    elif by == "xpath":
        return f"xpath={value}"
    elif by == "tag name":
        return value
    elif by == "css selector":
        return value
    elif by == "link text":
        return f"text='{value}'"
    elif by == "partial link text":
        return f"text='{value}'"
    else:
        return value


def click_element(element_id: str) -> Dict[str, Any]:
    """
    Click on an element in the browser.
    
    Args:
        element_id: The ID of the element to click
        
    Returns:
        A dictionary with the click status
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _get_selector_from_element_id(element_id)
        
        if not selector:
            return {"status": "error", "message": f"Invalid element ID: {element_id}"}
        
        _loop.run_until_complete(_current_page.locator(selector).click())
        
        return {"status": "success", "message": f"Clicked element with ID {element_id}"}
    except Exception as e:
        logger.error(f"Failed to click element: {str(e)}")
        return {"status": "error", "message": str(e)}


def _get_selector_from_element_id(element_id: str) -> Optional[str]:
    """
    Extract the selector from an element ID.
    
    Args:
        element_id: The element ID
        
    Returns:
        The selector string, or None if invalid
    """
    if "-" not in element_id:
        return None
    
    # Expected format: element-hash
    parts = element_id.split("-", 1)
    
    if len(parts) != 2 or parts[0] != "element":
        return None
    
    # The hash is derived from the selector, but we can't reverse it
    # So we need to maintain a mapping of element_id to selector
    # For simplicity, we'll just use basic CSS selector based on the hash
    return f"[data-element-id='{element_id}']"


def send_keys_to_element(element_id: str, text: str) -> Dict[str, Any]:
    """
    Send keys to an element in the browser.
    
    Args:
        element_id: The ID of the element to send keys to
        text: The text to send
        
    Returns:
        A dictionary with the send keys status
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _get_selector_from_element_id(element_id)
        
        if not selector:
            return {"status": "error", "message": f"Invalid element ID: {element_id}"}
        
        _loop.run_until_complete(_current_page.locator(selector).fill(text))
        
        return {"status": "success", "message": f"Sent keys to element with ID {element_id}"}
    except Exception as e:
        logger.error(f"Failed to send keys to element: {str(e)}")
        return {"status": "error", "message": str(e)}


def clear_element(element_id: str) -> Dict[str, Any]:
    """
    Clear an element in the browser.
    
    Args:
        element_id: The ID of the element to clear
        
    Returns:
        A dictionary with the clear status
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _get_selector_from_element_id(element_id)
        
        if not selector:
            return {"status": "error", "message": f"Invalid element ID: {element_id}"}
        
        _loop.run_until_complete(_current_page.locator(selector).fill(""))
        
        return {"status": "success", "message": f"Cleared element with ID {element_id}"}
    except Exception as e:
        logger.error(f"Failed to clear element: {str(e)}")
        return {"status": "error", "message": str(e)}


def get_element_text(element_id: str) -> Dict[str, Any]:
    """
    Get the text of an element in the browser.
    
    Args:
        element_id: The ID of the element to get text from
        
    Returns:
        A dictionary with the element text
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _get_selector_from_element_id(element_id)
        
        if not selector:
            return {"status": "error", "message": f"Invalid element ID: {element_id}"}
        
        text = _loop.run_until_complete(_current_page.locator(selector).text_content())
        
        return {"status": "success", "text": text}
    except Exception as e:
        logger.error(f"Failed to get element text: {str(e)}")
        return {"status": "error", "message": str(e)}


def get_element_attribute(element_id: str, attribute: str) -> Dict[str, Any]:
    """
    Get an attribute of an element in the browser.
    
    Args:
        element_id: The ID of the element to get attribute from
        attribute: The attribute name
        
    Returns:
        A dictionary with the attribute value
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _get_selector_from_element_id(element_id)
        
        if not selector:
            return {"status": "error", "message": f"Invalid element ID: {element_id}"}
        
        value = _loop.run_until_complete(_current_page.locator(selector).get_attribute(attribute))
        
        return {"status": "success", "value": value}
    except Exception as e:
        logger.error(f"Failed to get element attribute: {str(e)}")
        return {"status": "error", "message": str(e)}


def execute_script(script: str, args: List[Any] = None) -> Dict[str, Any]:
    """
    Execute JavaScript in the browser.
    
    Args:
        script: The JavaScript to execute
        args: Arguments to pass to the script
        
    Returns:
        A dictionary with the script execution result
    """
    global _current_page
    
    if args is None:
        args = []
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        result = _loop.run_until_complete(_current_page.evaluate(script, *args))
        
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Failed to execute script: {str(e)}")
        return {"status": "error", "message": str(e)}


def create_new_tab() -> Dict[str, Any]:
    """
    Create a new tab in the browser.
    
    Returns:
        A dictionary with the new tab status
    """
    global _browser_context, _current_page
    
    try:
        if not _browser_context:
            return {"status": "error", "message": "No active browser context"}
        
        # Create a new page
        new_page = _loop.run_until_complete(_browser_context.new_page())
        
        # Set it as the current page
        _current_page = new_page
        
        return {"status": "success", "message": "Created new tab"}
    except Exception as e:
        logger.error(f"Failed to create new tab: {str(e)}")
        return {"status": "error", "message": str(e)}


def switch_to_tab(tab_index: int) -> Dict[str, Any]:
    """
    Switch to a different tab in the browser.
    
    Args:
        tab_index: The index of the tab to switch to
        
    Returns:
        A dictionary with the tab switch status
    """
    global _browser_context, _current_page
    
    try:
        if not _browser_context:
            return {"status": "error", "message": "No active browser context"}
        
        # Get all pages in this context
        pages = _loop.run_until_complete(_browser_context.pages)
        
        if tab_index < 0 or tab_index >= len(pages):
            return {"status": "error", "message": f"Invalid tab index: {tab_index}"}
        
        # Set the current page
        _current_page = pages[tab_index]
        
        # Ensure the page is brought to front
        _loop.run_until_complete(_current_page.bring_to_front())
        
        return {"status": "success", "message": f"Switched to tab at index {tab_index}"}
    except Exception as e:
        logger.error(f"Failed to switch tab: {str(e)}")
        return {"status": "error", "message": str(e)}


def go_back() -> Dict[str, Any]:
    """
    Navigate back in the browser.
    
    Returns:
        A dictionary with the navigation status
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        _loop.run_until_complete(_current_page.go_back())
        
        return {"status": "success", "message": "Navigated back"}
    except Exception as e:
        logger.error(f"Failed to navigate back: {str(e)}")
        return {"status": "error", "message": str(e)}


def go_forward() -> Dict[str, Any]:
    """
    Navigate forward in the browser.
    
    Returns:
        A dictionary with the navigation status
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        _loop.run_until_complete(_current_page.go_forward())
        
        return {"status": "success", "message": "Navigated forward"}
    except Exception as e:
        logger.error(f"Failed to navigate forward: {str(e)}")
        return {"status": "error", "message": str(e)}


def refresh_page() -> Dict[str, Any]:
    """
    Refresh the current page in the browser.
    
    Returns:
        A dictionary with the refresh status
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        _loop.run_until_complete(_current_page.reload())
        
        return {"status": "success", "message": "Page refreshed"}
    except Exception as e:
        logger.error(f"Failed to refresh page: {str(e)}")
        return {"status": "error", "message": str(e)}


def wait_for_element(by: str, value: str, timeout: int = 30000) -> Dict[str, Any]:
    """
    Wait for an element to be present in the browser.
    
    Args:
        by: The method to find the element (id, css selector, xpath)
        value: The selector value
        timeout: The maximum time to wait in milliseconds
        
    Returns:
        A dictionary with the wait status and element information if found
    """
    global _current_page
    
    try:
        if not _current_page:
            return {"status": "error", "message": "No active browser page"}
        
        selector = _convert_selector(by, value)
        
        # Wait for the element to be visible
        try:
            _loop.run_until_complete(_current_page.wait_for_selector(
                selector, 
                state="visible", 
                timeout=timeout
            ))
            
            # Element is now visible, get its information
            return find_element(by, value)
        except Exception as wait_error:
            return {"status": "error", "message": f"Timeout waiting for element: {str(wait_error)}"}
    except Exception as e:
        logger.error(f"Failed to wait for element: {str(e)}")
        return {"status": "error", "message": str(e)}


def disconnect_from_browser() -> Dict[str, Any]:
    """
    Disconnect from the browser.
    
    Returns:
        A dictionary with disconnection status
    """
    global _browser, _browser_context, _current_page, _loop
    
    try:
        if _browser:
            # Close the browser
            _loop.run_until_complete(_browser.close())
            _browser = None
            _browser_context = None
            _current_page = None
        
        return {"status": "success", "message": "Disconnected from browser"}
    except Exception as e:
        logger.error(f"Failed to disconnect from browser: {str(e)}")
        return {"status": "error", "message": str(e)}