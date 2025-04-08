"""
OpenAI Integration Example for MCP Appium
=========================================

This module demonstrates how to use the MCP Appium implementation with OpenAI integration.
It shows how to interpret natural language commands and execute them on a mobile device.
"""

import argparse
import logging
import os
import sys
import time
from typing import Dict, Any

# Add the parent directory to the path so we can import the mcp_appium package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_appium.openai_integration import MCPOpenAIIntegration


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='MCP Appium OpenAI Integration Example')
    
    parser.add_argument(
        '--url',
        help='URL of the Appium server',
        default='http://localhost:4723'
    )
    
    parser.add_argument(
        '--platform',
        help='Mobile platform (android or ios)',
        choices=['android', 'ios'],
        default='android'
    )
    
    parser.add_argument(
        '--app',
        help='Path to the mobile app (.apk or .ipa)'
    )
    
    return parser.parse_args()


def get_capabilities(args) -> Dict[str, Any]:
    """
    Get the desired capabilities based on the platform and app.
    
    Args:
        args: Command line arguments
    
    Returns:
        Dict: Desired capabilities
    """
    if args.platform == 'android':
        caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "Android",
        }
        
        if args.app:
            caps["appium:app"] = args.app
        else:
            # Use a built-in app for demonstration
            caps["appium:appPackage"] = "com.android.settings"
            caps["appium:appActivity"] = ".Settings"
    else:
        caps = {
            "platformName": "iOS",
            "appium:automationName": "XCUITest",
            "appium:deviceName": "iPhone",
        }
        
        if args.app:
            caps["appium:app"] = args.app
        else:
            # Use a built-in app for demonstration
            caps["appium:bundleId"] = "com.apple.Preferences"
    
    return caps


def run_natural_language_commands(mcp: MCPOpenAIIntegration):
    """
    Run a series of natural language commands.
    
    Args:
        mcp: The MCPOpenAIIntegration instance
    """
    # Let OpenAI describe what's on the screen
    print("\n=== Current Screen Description ===")
    description = mcp.describe_current_screen()
    print(description)
    
    # Get suggestions for testing
    print("\n=== Suggested Test Actions ===")
    suggestions = mcp.suggest_test_actions()
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    
    # Execute some natural language commands
    commands = [
        "Find and click on the Display settings option",
        "Go back to the main settings screen",
        "Find any toggle switch and turn it on",
        "Take a screenshot of the current screen"
    ]
    
    for command in commands:
        print(f"\n=== Executing: '{command}' ===")
        result = mcp.execute_command(command)
        print(f"Result: {result['status']}")
        print(f"Message: {result.get('message', 'No message')}")
        
        # Brief pause to allow the UI to update
        time.sleep(1)


def main():
    """Run the MCP Appium OpenAI integration example."""
    try:
        args = parse_args()
        
        # Initialize the MCP OpenAI integration
        mcp = MCPOpenAIIntegration()
        
        # Connect to the Appium server
        logger.info(f"Connecting to Appium server at {args.url}")
        mcp.connect_to_appium(args.url)
        
        # Get capabilities
        capabilities = get_capabilities(args)
        logger.info(f"Using capabilities: {capabilities}")
        
        # Create a session
        logger.info("Creating session...")
        if not mcp.create_session(capabilities):
            logger.error("Failed to create session")
            return 1
        
        # Run natural language commands
        run_natural_language_commands(mcp)
        
        # Quit the session
        logger.info("Quitting session...")
        mcp.quit()
        
        logger.info("Example completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in MCP OpenAI integration example: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())