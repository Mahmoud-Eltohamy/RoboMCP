"""
Comprehensive Appium API Example for MCP Appium
===============================================

This module demonstrates a comprehensive set of Appium API methods available
in the MCP Appium implementation. It covers all major functionality including:

1. Session management
2. Element finding and interaction
3. Touch actions and gestures
4. Device manipulation
5. App management
6. Context switching
7. Alert handling
8. Screenshot and page source
9. Keyboard handling
10. Device orientation and geolocation

This example is designed to be a reference for using the MCP Appium client.
"""

import base64
import logging
import os
import sys
import time
from typing import Dict, List, Any, Optional

# Add the parent directory to the path so we can import the mcp_appium package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_appium.client import AppiumClient
from mcp_appium.errors import AppiumMCPError, ElementNotFoundError
from mcp_appium.config import configure_logging
from mcp_appium.models import Session
from mcp_appium.element import Element

# Configure logging
configure_logging("DEBUG")
logger = logging.getLogger(__name__)

# Save screenshots to the data/screenshots directory
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def save_screenshot(screenshot_base64: str, filename: str) -> str:
    """
    Save a base64-encoded screenshot to a file.
    
    Args:
        screenshot_base64: Base64-encoded screenshot
        filename: Name of the file to save
        
    Returns:
        str: Path to the saved file
    """
    if not screenshot_base64:
        logger.warning(f"Empty screenshot provided, not saving {filename}")
        return ""
        
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    try:
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(screenshot_base64))
        logger.info(f"Screenshot saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save screenshot: {str(e)}")
        return ""

def demo_session_management(client: AppiumClient) -> Optional[Session]:
    """
    Demonstrate session management capabilities.
    
    Args:
        client: AppiumClient instance
        
    Returns:
        Optional[Session]: The created session, or None if creation failed
    """
    logger.info("\n===== DEMO: Session Management =====")
    
    try:
        # Connect to the Appium server
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
                "appium:newCommandTimeout": 60
            }
        
        # Create a session
        session = client.create_session(capabilities)
        logger.info(f"Created session with ID: {session.id}")
        
        # Get session capabilities
        caps = session.get_session_capabilities()
        logger.info(f"Session capabilities: {caps}")
        
        # Get all sessions (should include our newly created session)
        all_sessions = session.get_all_sessions()
        logger.info(f"All active sessions: {all_sessions}")
        
        # Return the session for use in other demos
        return session
        
    except AppiumMCPError as e:
        logger.error(f"Error in session management demo: {str(e)}")
        return None

def demo_element_interaction(session: Session) -> None:
    """
    Demonstrate element finding and interaction capabilities.
    
    Args:
        session: Session instance
    """
    logger.info("\n===== DEMO: Element Interaction =====")
    
    if not session:
        logger.error("No active session, skipping element interaction demo")
        return
        
    try:
        # Take a screenshot of the initial screen
        screenshot = session.get_screenshot()
        save_screenshot(screenshot, "initial_screen.png")
        
        # Find element by xpath (common Settings entries)
        try:
            # Try to find elements by text that commonly appears in Settings apps
            elements = session.find_elements(
                "xpath", 
                "//android.widget.TextView"
            )
            logger.info(f"Found {len(elements)} TextView elements")
            
            # Print text of first few elements
            for i, element in enumerate(elements[:5]):
                try:
                    text = element.get_text()
                    logger.info(f"Element {i}: Text = '{text}'")
                    
                    # Check if element is displayed, enabled, and selected
                    displayed = element.is_displayed()
                    enabled = element.is_enabled()
                    selected = element.is_selected()
                    logger.info(f"Element {i}: Displayed = {displayed}, Enabled = {enabled}, Selected = {selected}")
                    
                    # Get element location and size
                    location = element.get_location()
                    size = element.get_size()
                    logger.info(f"Element {i}: Location = {location}, Size = {size}")
                    
                    # Get element attributes
                    try:
                        resource_id = element.get_attribute("resource-id")
                        content_desc = element.get_attribute("content-desc")
                        logger.info(f"Element {i}: Resource ID = '{resource_id}', Content Desc = '{content_desc}'")
                    except Exception as e:
                        logger.warning(f"Could not get attributes for element {i}: {str(e)}")
                        
                except Exception as e:
                    logger.warning(f"Could not process element {i}: {str(e)}")
            
            # If we found elements, interact with the first one
            if elements:
                try:
                    # Click the first element that is displayed and enabled
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            text = element.get_text()
                            logger.info(f"Clicking on element with text: '{text}'")
                            element.click()
                            
                            # Wait for the next screen to load
                            time.sleep(2)
                            
                            # Take a screenshot of the next screen
                            screenshot = session.get_screenshot()
                            save_screenshot(screenshot, "after_click.png")
                            
                            # Try to find child elements
                            try:
                                child_elements = session.find_elements("xpath", "//android.widget.TextView")
                                logger.info(f"Found {len(child_elements)} elements on the next screen")
                                
                                # Go back to the previous screen
                                session.back()
                                logger.info("Navigated back to the previous screen")
                                time.sleep(1)
                            except Exception as e:
                                logger.warning(f"Error finding elements on the next screen: {str(e)}")
                                session.back()
                                
                            break
                except Exception as e:
                    logger.warning(f"Error interacting with elements: {str(e)}")
                
        except ElementNotFoundError:
            logger.warning("Could not find expected elements")
            
    except AppiumMCPError as e:
        logger.error(f"Error in element interaction demo: {str(e)}")

def demo_touch_actions(session: Session) -> None:
    """
    Demonstrate touch actions and gestures.
    
    Args:
        session: Session instance
    """
    logger.info("\n===== DEMO: Touch Actions and Gestures =====")
    
    if not session:
        logger.error("No active session, skipping touch actions demo")
        return
        
    try:
        # Get window size
        window_size = session.get_window_size()
        logger.info(f"Window size: {window_size}")
        
        width = window_size.get("width", 0)
        height = window_size.get("height", 0)
        
        if width == 0 or height == 0:
            logger.warning("Invalid window size, skipping touch actions demo")
            return
            
        # Take a screenshot before touch actions
        screenshot = session.get_screenshot()
        save_screenshot(screenshot, "before_touch.png")
        
        # Perform a tap in the center of the screen
        center_x = width // 2
        center_y = height // 2
        session.tap(center_x, center_y)
        logger.info(f"Tapped at center of screen ({center_x}, {center_y})")
        time.sleep(1)
        
        # Perform a swipe from bottom to top (scroll up)
        start_x = width // 2
        start_y = int(height * 0.7)
        end_x = width // 2
        end_y = int(height * 0.3)
        session.swipe(start_x, start_y, end_x, end_y, 800)
        logger.info(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        time.sleep(1)
        
        # Take a screenshot after swipe
        screenshot = session.get_screenshot()
        save_screenshot(screenshot, "after_swipe.png")
        
        # Perform scrolling in different directions
        directions = ["up", "down", "left", "right"]
        for direction in directions:
            try:
                session.scroll(direction, 0.3)
                logger.info(f"Scrolled {direction}")
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Error scrolling {direction}: {str(e)}")
                
        # Perform a long press in the center
        try:
            session.long_press(center_x, center_y, 1500)
            logger.info(f"Long pressed at ({center_x}, {center_y})")
            time.sleep(1)
            
            # Take a screenshot after long press
            screenshot = session.get_screenshot()
            save_screenshot(screenshot, "after_long_press.png")
            
            # Press back to dismiss any dialogs that may have appeared
            session.back()
            
        except Exception as e:
            logger.warning(f"Error performing long press: {str(e)}")
            
        # Demonstrate complex touch actions using touch_perform API
        try:
            actions = [
                {"action": "press", "options": {"x": width // 4, "y": height // 2}},
                {"action": "wait", "options": {"ms": 500}},
                {"action": "moveTo", "options": {"x": width * 3 // 4, "y": height // 2}},
                {"action": "release", "options": {}}
            ]
            session.touch_perform(actions)
            logger.info("Performed custom touch action (horizontal drag)")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Error performing custom touch action: {str(e)}")
            
    except AppiumMCPError as e:
        logger.error(f"Error in touch actions demo: {str(e)}")

def demo_device_manipulation(session: Session) -> None:
    """
    Demonstrate device manipulation capabilities.
    
    Args:
        session: Session instance
    """
    logger.info("\n===== DEMO: Device Manipulation =====")
    
    if not session:
        logger.error("No active session, skipping device manipulation demo")
        return
        
    try:
        # Get device time
        device_time = session.get_device_time()
        logger.info(f"Device time: {device_time}")
        
        # Get and set device orientation
        try:
            current_orientation = session.get_orientation()
            logger.info(f"Current orientation: {current_orientation}")
            
            # Toggle orientation
            new_orientation = "LANDSCAPE" if current_orientation == "PORTRAIT" else "PORTRAIT"
            session.set_orientation(new_orientation)
            logger.info(f"Set orientation to {new_orientation}")
            time.sleep(1)
            
            # Take a screenshot in the new orientation
            screenshot = session.get_screenshot()
            save_screenshot(screenshot, f"{new_orientation.lower()}_orientation.png")
            
            # Set orientation back
            session.set_orientation(current_orientation)
            logger.info(f"Restored orientation to {current_orientation}")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Error manipulating orientation: {str(e)}")
            
        # Set geolocation (may require permissions)
        try:
            # San Francisco coordinates
            session.set_geolocation(37.7749, -122.4194)
            logger.info("Set geolocation to San Francisco")
            
            # Get current geolocation
            geolocation = session.get_geolocation()
            logger.info(f"Current geolocation: {geolocation}")
        except Exception as e:
            logger.warning(f"Error manipulating geolocation: {str(e)}")
            
        # Manipulate clipboard
        try:
            test_text = "MCP Appium Test Text"
            session.set_clipboard(test_text)
            logger.info(f"Set clipboard content to: '{test_text}'")
            
            clipboard_content = session.get_clipboard()
            logger.info(f"Retrieved clipboard content: '{clipboard_content}'")
        except Exception as e:
            logger.warning(f"Error manipulating clipboard: {str(e)}")
            
    except AppiumMCPError as e:
        logger.error(f"Error in device manipulation demo: {str(e)}")

def demo_app_management(session: Session) -> None:
    """
    Demonstrate app management capabilities.
    
    Args:
        session: Session instance
    """
    logger.info("\n===== DEMO: App Management =====")
    
    if not session:
        logger.error("No active session, skipping app management demo")
        return
        
    try:
        # Get current activity and package
        try:
            activity = session.get_current_activity()
            package = session.get_current_package()
            logger.info(f"Current activity: {activity}")
            logger.info(f"Current package: {package}")
        except Exception as e:
            logger.warning(f"Error getting current activity/package: {str(e)}")
            
        # Check if Settings app is installed (should always be true)
        try:
            is_installed = session.is_app_installed("com.android.settings")
            logger.info(f"Is Settings app installed: {is_installed}")
        except Exception as e:
            logger.warning(f"Error checking if app is installed: {str(e)}")
            
        # Start an activity directly (Android only)
        try:
            session.start_activity("com.android.settings", ".Settings")
            logger.info("Started Settings activity directly")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Error starting activity: {str(e)}")
            
        # Close and launch app
        try:
            session.close_app()
            logger.info("Closed app")
            time.sleep(1)
            
            session.launch_app()
            logger.info("Launched app")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Error closing/launching app: {str(e)}")
            
        # Reset app
        try:
            session.reset_app()
            logger.info("Reset app")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Error resetting app: {str(e)}")
            
    except AppiumMCPError as e:
        logger.error(f"Error in app management demo: {str(e)}")

def demo_context_switching(session: Session) -> None:
    """
    Demonstrate context switching capabilities.
    
    Args:
        session: Session instance
    """
    logger.info("\n===== DEMO: Context Switching =====")
    
    if not session:
        logger.error("No active session, skipping context switching demo")
        return
        
    try:
        # Get available contexts
        contexts = session.get_contexts()
        logger.info(f"Available contexts: {contexts}")
        
        # Get current context
        current_context = session.get_current_context()
        logger.info(f"Current context: {current_context}")
        
        # Switch to each available context
        for context in contexts:
            try:
                session.switch_to_context(context)
                logger.info(f"Switched to context: {context}")
                
                # Take a screenshot in this context
                screenshot = session.get_screenshot()
                save_screenshot(screenshot, f"context_{context.replace(':', '_')}.png")
                
                # Get the page source in this context
                page_source = session.get_page_source()
                if page_source:
                    logger.info(f"Page source length in context {context}: {len(page_source)} characters")
                else:
                    logger.warning(f"No page source available in context {context}")
                    
            except Exception as e:
                logger.warning(f"Error switching to context {context}: {str(e)}")
                
        # Switch back to the original context
        if current_context:
            try:
                session.switch_to_context(current_context)
                logger.info(f"Switched back to original context: {current_context}")
            except Exception as e:
                logger.warning(f"Error switching back to original context: {str(e)}")
                
    except AppiumMCPError as e:
        logger.error(f"Error in context switching demo: {str(e)}")

def demo_execute_script(session: Session) -> None:
    """
    Demonstrate script execution capabilities.
    
    Args:
        session: Session instance
    """
    logger.info("\n===== DEMO: Script Execution =====")
    
    if not session:
        logger.error("No active session, skipping script execution demo")
        return
        
    try:
        # Execute a simple JavaScript script to get the document title
        # (only works in webview context)
        contexts = session.get_contexts()
        has_webview = any("WEBVIEW" in context for context in contexts)
        
        if has_webview:
            try:
                # Find and switch to the first webview context
                webview_context = next(context for context in contexts if "WEBVIEW" in context)
                session.switch_to_context(webview_context)
                logger.info(f"Switched to webview context: {webview_context}")
                
                # Execute script to get the document title
                title = session.execute_script("return document.title;")
                logger.info(f"Document title: {title}")
                
                # Execute script to get some information about the page
                page_info = session.execute_script("""
                    return {
                        url: window.location.href,
                        userAgent: navigator.userAgent,
                        viewportHeight: window.innerHeight,
                        viewportWidth: window.innerWidth
                    };
                """)
                logger.info(f"Page information: {page_info}")
                
                # Execute async script to wait for a timeout
                result = session.execute_async_script("""
                    var callback = arguments[arguments.length - 1];
                    setTimeout(function() {
                        callback('Async script completed');
                    }, 1000);
                """)
                logger.info(f"Async script result: {result}")
                
                # Switch back to native context
                session.switch_to_context("NATIVE_APP")
                logger.info("Switched back to native context")
                
            except Exception as e:
                logger.warning(f"Error executing script in webview: {str(e)}")
                # Make sure we're back in native context
                try:
                    session.switch_to_context("NATIVE_APP")
                except:
                    pass
        else:
            # Execute mobile-specific scripts instead (Android only)
            try:
                # Get device information
                device_info = session.execute_script(
                    "mobile: deviceInfo", 
                    []
                )
                logger.info(f"Device info: {device_info}")
                
                # Execute other mobile commands for Android
                try:
                    session.execute_script(
                        "mobile: execEmuConsoleCommand", 
                        [{"command": "network status"}]
                    )
                    logger.info("Executed emulator console command")
                except Exception as e:
                    logger.warning(f"Error executing emulator command: {str(e)}")
                    
            except Exception as e:
                logger.warning(f"Error executing mobile script: {str(e)}")
    
    except AppiumMCPError as e:
        logger.error(f"Error in script execution demo: {str(e)}")

def main():
    """Run the comprehensive Appium API example."""
    logger.info("Starting Comprehensive Appium API Example")
    
    # Create a client
    client = AppiumClient()
    
    try:
        # Demo 1: Session Management
        session = demo_session_management(client)
        
        if session:
            # Wait for the app to load
            time.sleep(3)
            
            # Demo 2: Element Interaction
            demo_element_interaction(session)
            
            # Demo 3: Touch Actions and Gestures
            demo_touch_actions(session)
            
            # Demo 4: Device Manipulation
            demo_device_manipulation(session)
            
            # Demo 5: App Management
            demo_app_management(session)
            
            # Demo 6: Context Switching
            demo_context_switching(session)
            
            # Demo 7: Execute Script
            demo_execute_script(session)
            
        else:
            logger.error("Session creation failed, cannot proceed with demos")
            
    except AppiumMCPError as e:
        logger.error(f"Error in Appium MCP client: {str(e)}")
    finally:
        # Quit the session
        if client.session_id:
            client.quit()
            logger.info("Session quit")
            
    logger.info("Comprehensive Appium API Example completed")

if __name__ == "__main__":
    main()