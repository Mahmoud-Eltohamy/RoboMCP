"""
Comprehensive API Example for MCP Appium
=======================================

This module demonstrates all major Appium API methods implemented in the MCP Appium package.
It provides examples of session methods, element interactions, and advanced features.
"""

import base64
import logging
import os
import sys
import time
from typing import Dict, List, Any

# Add the parent directory to the path so we can import the mcp_appium package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_appium.client import AppiumClient
from mcp_appium.errors import AppiumMCPError, ElementNotFoundError
from mcp_appium.config import configure_logging
from mcp_appium.element import Element
from mcp_appium.models import Session

# Configure logging
configure_logging("DEBUG")
logger = logging.getLogger(__name__)

def save_screenshot(screenshot_base64: str, filename: str) -> None:
    """
    Save a base64-encoded screenshot to a file.
    
    Args:
        screenshot_base64: Base64-encoded screenshot
        filename: Name of the file to save
    """
    # Create screenshots directory if it doesn't exist
    os.makedirs("data/screenshots", exist_ok=True)
    
    # Save the screenshot
    filepath = f"data/screenshots/{filename}"
    try:
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(screenshot_base64))
        logger.info(f"Screenshot saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")

def demonstrate_session_methods(session: Session) -> None:
    """
    Demonstrate session-level methods.
    
    Args:
        session: The Appium session
    """
    logger.info("=== Demonstrating Session Methods ===")
    
    # Get page source
    page_source = session.get_page_source()
    logger.info(f"Page source length: {len(page_source)} characters")
    
    # Get current activity and package (Android only)
    try:
        current_activity = session.get_current_activity()
        current_package = session.get_current_package()
        logger.info(f"Current activity: {current_activity}")
        logger.info(f"Current package: {current_package}")
    except AppiumMCPError as e:
        logger.warning(f"Could not get current activity/package: {e}")
    
    # Get device time
    device_time = session.get_device_time()
    logger.info(f"Device time: {device_time}")
    
    # Get window size
    window_size = session.get_window_size()
    logger.info(f"Window size: {window_size}")
    
    # Get orientation
    orientation = session.get_orientation()
    logger.info(f"Orientation: {orientation}")
    
    # Take a screenshot
    screenshot = session.get_screenshot()
    logger.info("Took a screenshot")
    save_screenshot(screenshot, "session_screenshot.png")
    
    # Set timeouts
    session.set_timeouts(implicit=10000, page_load=20000, script=30000)
    logger.info("Set session timeouts")
    
    # Get session capabilities
    capabilities = session.get_session_capabilities()
    logger.info(f"Session capabilities: {capabilities}")
    
    # Get all sessions (if available)
    try:
        all_sessions = session.get_all_sessions()
        logger.info(f"Found {len(all_sessions)} active sessions")
    except AppiumMCPError as e:
        logger.warning(f"Could not get all sessions: {e}")
    
    # Execute script (if in web context)
    try:
        result = session.execute_script("return navigator.userAgent;")
        logger.info(f"User agent: {result}")
    except AppiumMCPError as e:
        logger.warning(f"Could not execute script: {e}")

def demonstrate_touch_actions(session: Session) -> None:
    """
    Demonstrate touch action methods.
    
    Args:
        session: The Appium session
    """
    logger.info("=== Demonstrating Touch Actions ===")
    
    # Get window size for calculating coordinates
    window_size = session.get_window_size()
    width = window_size.get("width", 0)
    height = window_size.get("height", 0)
    
    # Tap at the center of the screen
    center_x = width // 2
    center_y = height // 2
    session.tap(center_x, center_y)
    logger.info(f"Tapped at center of screen ({center_x}, {center_y})")
    
    # Swipe from bottom to top (scroll up)
    start_x = width // 2
    start_y = height * 3 // 4
    end_x = width // 2
    end_y = height // 4
    session.swipe(start_x, start_y, end_x, end_y, duration=800)
    logger.info(f"Swiped up from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    
    time.sleep(1)  # Wait for the swipe to complete
    
    # Swipe from top to bottom (scroll down)
    session.swipe(end_x, end_y, start_x, start_y, duration=800)
    logger.info(f"Swiped down from ({end_x}, {end_y}) to ({start_x}, {start_y})")
    
    time.sleep(1)  # Wait for the swipe to complete
    
    # Try to perform more complex touch actions if available
    try:
        # Example of multi-touch perform (pinch)
        actions = [
            {
                "action": "press",
                "options": {"x": width//2 - 100, "y": height//2}
            },
            {
                "action": "moveTo",
                "options": {"x": width//2 - 50, "y": height//2}
            },
            {
                "action": "release"
            },
            {
                "action": "press",
                "options": {"x": width//2 + 100, "y": height//2}
            },
            {
                "action": "moveTo",
                "options": {"x": width//2 + 50, "y": height//2}
            },
            {
                "action": "release"
            }
        ]
        session.multi_touch_perform(actions)
        logger.info("Performed multi-touch actions (pinch)")
    except AppiumMCPError as e:
        logger.warning(f"Could not perform multi-touch actions: {e}")
    
    # Take a screenshot after touch actions
    screenshot = session.get_screenshot()
    save_screenshot(screenshot, "after_touch_actions.png")
    logger.info("Took a screenshot after touch actions")

def demonstrate_element_methods(session: Session) -> None:
    """
    Demonstrate element methods.
    
    Args:
        session: The Appium session
    """
    logger.info("=== Demonstrating Element Methods ===")
    
    try:
        # Find elements using different strategies
        try:
            # First try to find by accessibility id (most reliable cross-platform)
            logger.info("Trying to find elements by accessibility id...")
            elements = session.find_elements("accessibility id", "button1")
            if not elements:
                raise ElementNotFoundError("No elements found by accessibility id")
        except (AppiumMCPError, ElementNotFoundError):
            # Then try by class name
            logger.info("Trying to find elements by class name...")
            elements = session.find_elements("class name", "android.widget.Button")
            if not elements and "platformName" in session.capabilities and session.capabilities["platformName"].lower() == "ios":
                elements = session.find_elements("class name", "XCUIElementTypeButton")
            if not elements:
                # For web contexts
                elements = session.find_elements("tag name", "button")
            if not elements:
                raise ElementNotFoundError("No button elements found")
        
        logger.info(f"Found {len(elements)} button elements")
        
        if elements:
            # Get the first element
            element = elements[0]
            logger.info(f"Working with element: {element}")
            
            # Get element attributes
            try:
                text = element.get_text()
                logger.info(f"Element text: {text}")
            except AppiumMCPError as e:
                logger.warning(f"Could not get element text: {e}")
            
            try:
                location = element.get_location()
                logger.info(f"Element location: {location}")
                
                size = element.get_size()
                logger.info(f"Element size: {size}")
                
                rect = element.get_rect()
                logger.info(f"Element rectangle: {rect}")
                
                is_displayed = element.is_displayed()
                logger.info(f"Element is displayed: {is_displayed}")
                
                is_enabled = element.is_enabled()
                logger.info(f"Element is enabled: {is_enabled}")
                
                is_selected = element.is_selected()
                logger.info(f"Element is selected: {is_selected}")
                
                attributes = element.get_all_attributes()
                logger.info(f"Element attributes: {attributes}")
            except AppiumMCPError as e:
                logger.warning(f"Could not get element properties: {e}")
            
            # Take a screenshot of the element if supported
            try:
                element_screenshot = element.take_screenshot()
                save_screenshot(element_screenshot, "element_screenshot.png")
                logger.info("Took a screenshot of the element")
            except AppiumMCPError as e:
                logger.warning(f"Could not take element screenshot: {e}")
            
            # Click the element
            try:
                element.click()
                logger.info("Clicked the element")
                
                # Wait for any transitions
                time.sleep(2)
                
                # Go back if needed
                session.back()
                logger.info("Navigated back")
                
                # Wait for any transitions
                time.sleep(2)
            except AppiumMCPError as e:
                logger.warning(f"Could not click element or navigate back: {e}")
            
            # Find input fields for text operations
            try:
                input_elements = session.find_elements("class name", "android.widget.EditText")
                if not input_elements and "platformName" in session.capabilities and session.capabilities["platformName"].lower() == "ios":
                    input_elements = session.find_elements("class name", "XCUIElementTypeTextField")
                if not input_elements:
                    # For web contexts
                    input_elements = session.find_elements("tag name", "input")
                
                if input_elements:
                    input_element = input_elements[0]
                    logger.info(f"Found input element: {input_element}")
                    
                    # Clear and send keys
                    input_element.clear()
                    logger.info("Cleared input element")
                    
                    input_element.send_keys("MCP Appium Test")
                    logger.info("Sent keys to input element")
                    
                    # Check if keyboard is shown
                    try:
                        is_keyboard_shown = session.is_keyboard_shown()
                        logger.info(f"Keyboard is shown: {is_keyboard_shown}")
                        
                        if is_keyboard_shown:
                            session.hide_keyboard()
                            logger.info("Keyboard hidden")
                    except AppiumMCPError as e:
                        logger.warning(f"Could not check keyboard status: {e}")
            except (AppiumMCPError, ElementNotFoundError, IndexError) as e:
                logger.warning(f"Could not find or interact with input elements: {e}")
    except (AppiumMCPError, ElementNotFoundError) as e:
        logger.error(f"Failed to find elements: {e}")

def demonstrate_context_handling(session: Session) -> None:
    """
    Demonstrate context handling methods.
    
    Args:
        session: The Appium session
    """
    logger.info("=== Demonstrating Context Handling ===")
    
    try:
        # Get current context
        current_context = session.get_current_context()
        logger.info(f"Current context: {current_context}")
        
        # Get all available contexts
        contexts = session.get_contexts()
        logger.info(f"Available contexts: {contexts}")
        
        # Try to switch context if more than one is available
        if len(contexts) > 1:
            # Save the original context
            original_context = current_context
            
            # Find a different context to switch to
            for context in contexts:
                if context != current_context:
                    logger.info(f"Switching to context: {context}")
                    session.switch_to_context(context)
                    
                    # Verify the switch
                    new_context = session.get_current_context()
                    logger.info(f"New context: {new_context}")
                    
                    # Wait a moment
                    time.sleep(2)
                    
                    # Take a screenshot in the new context
                    screenshot = session.get_screenshot()
                    save_screenshot(screenshot, f"context_{context.replace(':', '_')}.png")
                    logger.info(f"Took a screenshot in context: {context}")
                    
                    # Switch back to the original context
                    logger.info(f"Switching back to original context: {original_context}")
                    session.switch_to_context(original_context)
                    break
    except AppiumMCPError as e:
        logger.warning(f"Could not handle contexts: {e}")

def main():
    """Run the comprehensive API example."""
    # Create a client
    client = AppiumClient()
    
    try:
        # Connect to the Appium server (use environment variable for Docker)
        appium_url = os.environ.get("APPIUM_URL", "http://localhost:4723")
        client.connect(appium_url)
        logger.info(f"Connected to Appium server at {appium_url}")
        
        # Set up desired capabilities for Android
        # Use the Settings app for testing if no app is provided
        app_path = os.environ.get("ANDROID_APP_PATH")
        
        if app_path:
            capabilities = {
                "platformName": "Android",
                "appium:automationName": "UiAutomator2",
                "appium:deviceName": "Android Emulator",
                "appium:app": app_path
            }
        else:
            # Using Android Settings app for testing (available on all Android devices)
            capabilities = {
                "platformName": "Android",
                "appium:automationName": "UiAutomator2",
                "appium:deviceName": "Android Emulator",
                "appium:appPackage": "com.android.settings",
                "appium:appActivity": ".Settings",
                "appium:newCommandTimeout": 120
            }
        
        # Create a session
        session = client.create_session(capabilities)
        logger.info(f"Created session with ID: {session.id}")
        
        # Wait for the app to load
        time.sleep(3)
        
        # Run the demonstrations
        demonstrate_session_methods(session)
        demonstrate_touch_actions(session)
        demonstrate_element_methods(session)
        demonstrate_context_handling(session)
        
        # Additional advanced methods
        logger.info("=== Demonstrating Advanced Methods ===")
        
        # Geolocation methods
        try:
            # Set a geolocation (San Francisco)
            session.set_geolocation(37.7749, -122.4194)
            logger.info("Set geolocation to San Francisco")
            
            # Get the current geolocation
            geolocation = session.get_geolocation()
            logger.info(f"Current geolocation: {geolocation}")
        except AppiumMCPError as e:
            logger.warning(f"Could not set/get geolocation: {e}")
        
        # App management methods
        try:
            # For demonstration purposes, restart the app
            logger.info("Closing the app...")
            session.close_app()
            time.sleep(2)
            
            logger.info("Launching the app...")
            session.launch_app()
            time.sleep(3)
            
            # Take a screenshot after relaunch
            screenshot = session.get_screenshot()
            save_screenshot(screenshot, "after_relaunch.png")
            logger.info("Took a screenshot after relaunching app")
        except AppiumMCPError as e:
            logger.warning(f"Could not manage app state: {e}")
        
        logger.info("Comprehensive API demonstration completed successfully")
        
    except AppiumMCPError as e:
        logger.error(f"Error in Appium MCP client: {e}")
    finally:
        # Quit the session
        if client.session_id:
            client.quit()
            logger.info("Session quit")

if __name__ == "__main__":
    main()