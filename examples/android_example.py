"""
Android Example for MCP Appium
==============================

This module demonstrates how to use the MCP Appium implementation with an Android device.
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
    """Run the Android example."""
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
                "appium:newCommandTimeout": 60
            }
        
        # Create a session
        session = client.create_session(capabilities)
        logger.info(f"Created session with ID: {session.id}")
        
        # Wait for the app to load
        time.sleep(3)
        
        # Determine which app we're testing and interact accordingly
        try:
            app_package = capabilities.get("appium:appPackage", "")
            
            if app_package == "com.android.settings":
                # Testing with the Settings app
                logger.info("Testing with Android Settings app")
                
                # Take a screenshot of the Settings main screen
                screenshot = session.get_screenshot()
                logger.info("Took a screenshot of Settings main screen")
                
                # Try to find and click on "Network & Internet" (common in Settings)
                try:
                    # Try by text
                    network_element = session.find_element(
                        "xpath", 
                        "//android.widget.TextView[@text='Network & Internet' or @text='Wi-Fi' or @text='Network']"
                    )
                    logger.info(f"Found settings element: {network_element}")
                    
                    # Click the element
                    network_element.click()
                    logger.info("Clicked on a settings category")
                    
                    # Wait for the subcategory to load
                    time.sleep(2)
                    
                    # Take another screenshot
                    screenshot = session.get_screenshot()
                    logger.info("Took a screenshot of the subcategory")
                    
                    # Go back
                    session.back()
                    logger.info("Navigated back to main Settings")
                    
                    # Find all setting entries
                    entries = session.find_elements("class name", "android.widget.TextView")
                    logger.info(f"Found {len(entries)} text entries in Settings")
                    
                    # Display first few entries
                    for i, entry in enumerate(entries[:5]):
                        try:
                            text = entry.get_text()
                            logger.info(f"Entry {i}: {text}")
                        except Exception as e:
                            logger.warning(f"Could not get text for entry {i}: {str(e)}")
                    
                except AppiumMCPError as e:
                    logger.warning(f"Could not find network settings: {str(e)}")
                
            else:
                # Testing with a custom app
                logger.info("Testing with custom app")
                
                try:
                    # Generic approach to find clickable elements
                    elements = session.find_elements("xpath", "//android.widget.Button | //android.widget.TextView")
                    logger.info(f"Found {len(elements)} clickable elements")
                    
                    if elements:
                        # Click on the first element
                        elements[0].click()
                        logger.info(f"Clicked on element: {elements[0]}")
                        
                        # Wait for the next screen
                        time.sleep(2)
                        
                        # Take a screenshot
                        screenshot = session.get_screenshot()
                        logger.info("Took a screenshot after clicking")
                        
                        # Go back
                        session.back()
                        logger.info("Navigated back")
                    else:
                        logger.warning("No clickable elements found")
                
                    # Try to find input fields
                    input_fields = session.find_elements("class name", "android.widget.EditText")
                    logger.info(f"Found {len(input_fields)} input fields")
                    
                    # If we found input fields, try to enter text
                    if len(input_fields) >= 2:
                        input_fields[0].send_keys("testuser")
                        input_fields[1].send_keys("password123")
                        logger.info("Entered test data into input fields")
                    
                except AppiumMCPError as e:
                    logger.error(f"Error interacting with app elements: {str(e)}")
            
            # Take a final screenshot
            screenshot = session.get_screenshot()
            logger.info("Took a final screenshot")
            
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
