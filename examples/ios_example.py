"""
iOS Example for MCP Appium
=========================

This module demonstrates how to use the MCP Appium implementation with an iOS device.
"""

import logging
import os
import sys
import time

# Add the parent directory to the path so we can import the mcp_appium package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_appium.client import AppiumClient
from mcp_appium.errors import AppiumMCPError
from mcp_appium.config import configure_logging

# Configure logging
configure_logging("DEBUG")
logger = logging.getLogger(__name__)

def main():
    """Run the iOS example."""
    # Create a client
    client = AppiumClient()
    
    try:
        # Connect to the Appium server (use environment variable for Docker)
        appium_url = os.environ.get("APPIUM_URL", "http://localhost:4723")
        client.connect(appium_url)
        logger.info(f"Connected to Appium server at {appium_url}")
        
        # Set up desired capabilities for iOS
        capabilities = {
            "platformName": "iOS",
            "appium:automationName": "XCUITest",
            "appium:deviceName": "iPhone Simulator",
            "appium:platformVersion": "14.5",  # Adjust based on your simulator
            "appium:app": os.environ.get("IOS_APP_PATH", "/path/to/your/app.app")
        }
        
        # Create a session
        session = client.create_session(capabilities)
        logger.info(f"Created session with ID: {session.id}")
        
        # Wait for the app to load
        time.sleep(3)
        
        # Find an element by accessibility ID
        try:
            element = session.find_element("accessibility id", "login_button")
            logger.info(f"Found element: {element}")
            
            # Check if the element is displayed
            if element.is_displayed():
                logger.info("Element is displayed")
                
                # Click the element
                element.click()
                logger.info("Clicked the element")
                
                # Wait for the next screen to load
                time.sleep(2)
                
                # Find input fields
                username_field = session.find_element("accessibility id", "username_field")
                password_field = session.find_element("accessibility id", "password_field")
                
                # Enter text
                username_field.send_keys("testuser")
                password_field.send_keys("password123")
                logger.info("Entered username and password")
                
                # Find and click the submit button
                submit_button = session.find_element("accessibility id", "submit_button")
                submit_button.click()
                logger.info("Clicked the submit button")
                
                # Wait for the home screen to load
                time.sleep(2)
                
                # Take a screenshot
                screenshot = session.get_screenshot()
                logger.info("Took a screenshot")
                
                # Go back
                session.back()
                logger.info("Navigated back")
                
                # Try using a different locator strategy
                element_by_predicate = session.find_element(
                    "ios predicate string", 
                    "name == 'Login'"
                )
                logger.info(f"Found element by predicate: {element_by_predicate}")
                
                # Find multiple elements
                buttons = session.find_elements("class name", "XCUIElementTypeButton")
                logger.info(f"Found {len(buttons)} buttons")
                
                # Check for WebView contexts
                contexts = session.get_contexts()
                logger.info(f"Available contexts: {contexts}")
                
                # If there's a webview, switch to it
                webview_contexts = [c for c in contexts if c.startswith("WEBVIEW_")]
                if webview_contexts:
                    # Switch to the first webview context
                    session.switch_to_context(webview_contexts[0])
                    logger.info(f"Switched to context: {webview_contexts[0]}")
                    
                    # Now we can interact with web elements
                    web_element = session.find_element("css selector", "button")
                    web_element.click()
                    logger.info("Clicked a web element")
                    
                    # Switch back to native context
                    session.switch_to_context("NATIVE_APP")
                    logger.info("Switched back to native context")
                
            else:
                logger.warning("Element is not displayed")
                
        except AppiumMCPError as e:
            logger.error(f"Error interacting with the app: {str(e)}")
        
    except AppiumMCPError as e:
        logger.error(f"Error in Appium MCP client: {str(e)}")
    finally:
        # Quit the session
        if client.session_id:
            client.quit()
            logger.info("Session quit")

if __name__ == "__main__":
    main()
