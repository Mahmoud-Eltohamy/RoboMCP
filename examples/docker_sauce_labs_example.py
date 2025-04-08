"""
Docker-based Sauce Labs Demo App Example with AI Integration for MCP Appium
===========================================================================

This module demonstrates how to use the MCP Appium implementation with AI integration
to test the Sauce Labs Demo App for Android running in a Docker environment.
This example is designed to be used with the Docker setup defined in the project.
"""

import argparse
import logging
import os
import sys
import time
from typing import Dict, Any, List, Optional

# Add the parent directory to the path so we can import the mcp_appium package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_appium.ai_integration import MCPAIIntegration, AIProvider
from mcp_appium.client import AppiumClient
from mcp_appium.errors import AppiumMCPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Docker-based Sauce Labs Demo App Example with AI Integration')
    
    parser.add_argument(
        '--url',
        help='URL of the Appium server in Docker',
        default='http://appium:4723'  # Docker service name as hostname
    )
    
    parser.add_argument(
        '--provider',
        help='AI provider to use',
        choices=['openai', 'gemini', 'huggingface', 'multi'],
        default='openai'
    )
    
    return parser.parse_args()


def get_capabilities() -> Dict[str, Any]:
    """
    Get the desired capabilities for the Sauce Labs Demo App in Docker.
    
    Returns:
        Dict: Desired capabilities
    """
    # App path inside the Docker container
    app_path = '/app/app_tests/sauce_labs_demo/sauce_labs_demo.apk'
    
    caps = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": "Android Emulator",
        "appium:app": app_path,
        "appium:newCommandTimeout": 90
    }
    
    logger.info(f"Using app at: {app_path} (Docker container path)")
    
    return caps


def create_ai_integration(provider: str) -> MCPAIIntegration:
    """
    Create and initialize an MCPAIIntegration instance.
    
    Args:
        provider: Name of the AI provider
    
    Returns:
        MCPAIIntegration: The configured AI integration instance
    """
    if provider == 'openai':
        return MCPAIIntegration(provider=AIProvider.OPENAI)
    elif provider == 'gemini':
        return MCPAIIntegration(provider=AIProvider.GEMINI)
    elif provider == 'huggingface':
        return MCPAIIntegration(provider=AIProvider.HUGGING_FACE)
    else:
        # Multi-provider setup with fallbacks
        return MCPAIIntegration(provider="multi")


def run_sauce_labs_demo_tests(mcp_ai: MCPAIIntegration, client: AppiumClient):
    """
    Run tests on the Sauce Labs Demo App.
    
    Args:
        mcp_ai: The MCPAIIntegration instance
        client: The AppiumClient instance
    """
    session = client.session
    
    # First, let's get a description of the initial screen
    logger.info("Getting current screen description...")
    page_source = session.get_page_source()
    screen_description = mcp_ai.describe_screen(page_source)
    logger.info(f"Screen Description: {screen_description}")
    
    # Get suggested test actions
    logger.info("Getting suggested test actions...")
    suggestions = mcp_ai.suggest_test_actions(page_source)
    for i, suggestion in enumerate(suggestions[:5], 1):
        logger.info(f"Suggested Action {i}: {suggestion}")
    
    # Execute a series of natural language commands
    test_commands = [
        "Browse the products",
        "Sort products by price",
        "Add the first product to the cart",
        "Go to the shopping cart",
        "Proceed to checkout",
        "Fill out shipping information with test data",
        "Complete the purchase"
    ]
    
    context = {
        "app_name": "Sauce Labs Demo App",
        "app_type": "e-commerce",
        "test_environment": {
            "platform": "Android",
            "device": "Emulator"
        }
    }
    
    for command in test_commands:
        logger.info(f"\nExecuting command: '{command}'")
        
        try:
            # Use AI to interpret the command
            command_result = mcp_ai.interpret_command(command, context)
            logger.info(f"Interpreted command: {command_result}")
            
            # Execute the command actions based on the AI interpretation
            execute_actions(client, command_result.get("actions", []))
            
            # Take a screenshot after each command
            screenshot = session.get_screenshot()
            logger.info(f"Screenshot taken after command: '{command}'")
            
            # Brief pause to allow the UI to update
            time.sleep(2)
            
            # Update the context with the new screen information
            page_source = session.get_page_source()
            context["current_screen"] = mcp_ai.describe_screen(page_source)
            
        except Exception as e:
            logger.error(f"Error executing command '{command}': {str(e)}")
    
    # At the end, analyze the app structure using AI
    logger.info("\nAnalyzing app structure...")
    try:
        app_structure = mcp_ai.analyze_app_structure(page_source, context)
        logger.info(f"App Structure Analysis: {app_structure}")
    except Exception as e:
        logger.error(f"Error analyzing app structure: {str(e)}")


def execute_actions(client: AppiumClient, actions: List[Dict[str, Any]]):
    """
    Execute a series of actions on the app.
    
    Args:
        client: The AppiumClient instance
        actions: List of actions to perform
    """
    session = client.session
    
    for action in actions:
        action_type = action.get("type", "").lower()
        
        try:
            if action_type == "click":
                # Handle element clicks
                locator = action.get("locator", {})
                strategy = locator.get("using", "xpath")
                value = locator.get("value", "")
                
                if strategy and value:
                    element = session.find_element(strategy, value)
                    element.click()
                    logger.info(f"Clicked element: {value}")
                
            elif action_type == "input":
                # Handle text input
                locator = action.get("locator", {})
                strategy = locator.get("using", "xpath")
                value = locator.get("value", "")
                text = action.get("text", "")
                
                if strategy and value and text:
                    element = session.find_element(strategy, value)
                    element.send_keys(text)
                    logger.info(f"Entered text '{text}' into element: {value}")
                
            elif action_type == "swipe" or action_type == "scroll":
                # Handle swipe/scroll gestures
                direction = action.get("direction", "down")
                distance = action.get("distance", 0.5)  # Default to 50% of screen
                
                # Get screen dimensions
                width = session.get_window_size()["width"]
                height = session.get_window_size()["height"]
                
                start_x = width // 2
                start_y = height // 2
                end_x = start_x
                end_y = start_y
                
                if direction == "down":
                    end_y = int(start_y + (height * distance))
                elif direction == "up":
                    end_y = int(start_y - (height * distance))
                elif direction == "right":
                    end_x = int(start_x + (width * distance))
                elif direction == "left":
                    end_x = int(start_x - (width * distance))
                
                session.swipe(start_x, start_y, end_x, end_y)
                logger.info(f"Performed {direction} swipe")
                
            elif action_type == "wait":
                # Handle wait actions
                duration = action.get("duration", 1)
                time.sleep(duration)
                logger.info(f"Waited for {duration} seconds")
                
            elif action_type == "back":
                # Handle back button press
                session.back()
                logger.info("Pressed back button")
                
            else:
                logger.warning(f"Unknown action type: {action_type}")
                
        except AppiumMCPError as e:
            logger.error(f"Error executing action {action_type}: {str(e)}")
            # Continue with next action instead of failing completely
            continue


def main():
    """Run the Docker-based Sauce Labs Demo App example."""
    try:
        args = parse_args()
        
        # Initialize the client
        client = AppiumClient()
        
        # Connect to the Appium server in Docker
        logger.info(f"Connecting to Appium server at {args.url} (Docker container)")
        client.connect(args.url)
        
        # Create AI integration
        logger.info(f"Creating AI integration with provider: {args.provider}")
        mcp_ai = create_ai_integration(args.provider)
        
        # Get capabilities
        capabilities = get_capabilities()
        logger.info(f"Using capabilities: {capabilities}")
        
        # Create a session
        logger.info("Creating session...")
        session = client.create_session(capabilities)
        logger.info(f"Session created with ID: {session.id}")
        
        # Wait for the app to load completely
        time.sleep(5)
        
        # Run the demo app tests
        run_sauce_labs_demo_tests(mcp_ai, client)
        
        # Quit the session
        logger.info("Quitting session...")
        client.quit()
        
        logger.info("Example completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in Sauce Labs Demo App example: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())