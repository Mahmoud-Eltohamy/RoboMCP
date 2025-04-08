"""
OpenAI Standalone Example for MCP Appium
=======================================

This module demonstrates how to use only the OpenAI aspects of the MCP Appium integration.
This is useful for testing the natural language processing without an Appium server.
"""

import os
import json
import logging
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import the mcp_appium package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import OpenAI directly
from openai import OpenAI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.error("OpenAI API key not found in environment variables")
    sys.exit(1)

# Initialize OpenAI client
openai_client = OpenAI(api_key=api_key)

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
DEFAULT_MODEL = "gpt-4o"


def process_command(command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process a natural language command using OpenAI.
    
    Args:
        command: The natural language command to process
        context: Optional context information
        
    Returns:
        Dict: The processed command as a structured action
    """
    if not command:
        return {"status": "error", "message": "Command cannot be empty"}
    
    # Default context if none provided
    if context is None:
        context = {
            "page_source": """
            <android.widget.FrameLayout>
                <android.widget.LinearLayout>
                    <android.widget.TextView text="Welcome to MCP Appium Demo" />
                    <android.widget.Button text="Login" content-desc="login_button" />
                    <android.widget.EditText hint="Username" content-desc="username_field" />
                    <android.widget.EditText hint="Password" content-desc="password_field" />
                    <android.widget.CheckBox text="Remember me" checked="false" />
                </android.widget.LinearLayout>
            </android.widget.FrameLayout>
            """
        }
    
    try:
        # Prepare the prompt
        system_prompt = """
        You are an expert in mobile app testing with Appium.
        Your job is to interpret natural language commands and convert them into structured Appium commands.
        
        Return a JSON object with the following structure:
        {
            "action": "<appium_action>",
            "parameters": {
                "<param_name>": "<param_value>",
                ...
            }
        }
        
        Available actions and their parameters:
        1. find_element: {"by": "<locator_strategy>", "value": "<locator_value>"}
        2. find_elements: {"by": "<locator_strategy>", "value": "<locator_value>"}
        3. click_element: {"element_id": "<element_id>"}
        4. send_keys: {"element_id": "<element_id>", "text": "<text_to_send>"}
        5. get_text: {"element_id": "<element_id>"}
        6. back: {}
        7. screenshot: {}
        8. get_contexts: {}
        9. switch_to_context: {"context_name": "<context_name>"}
        10. execute_script: {"script": "<javascript_code>", "args": [<arg1>, <arg2>, ...]}
        
        Locator strategies include: "id", "accessibility id", "class name", "xpath", "css selector" (for web contexts),
        "ios predicate string" (for iOS), "android uiautomator" (for Android).
        
        Before responding, analyze the current app state from the provided context (if available).
        """
        
        # Add context information to the user prompt
        context_info = ""
        if context.get("page_source"):
            context_info += "\nCurrent page source:\n"
            context_info += context["page_source"]
        
        user_prompt = f"App state context:{context_info}\n\nCommand to interpret: {command}"
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract and parse the response
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        # Validate the response format
        if "action" not in result or "parameters" not in result:
            return {
                "status": "error", 
                "message": "OpenAI did not return a properly formatted command. Expected 'action' and 'parameters' fields."
            }
        
        logger.info(f"Interpreted command '{command}' as action '{result['action']}' with parameters {result['parameters']}")
        
        # Return with success status
        return {
            "status": "success",
            "action": result["action"],
            "parameters": result["parameters"],
            "message": f"Successfully interpreted command as {result['action']}"
        }
        
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        return {"status": "error", "message": str(e)}


def describe_screen(page_source: str) -> str:
    """
    Use OpenAI to describe a screen from page source.
    
    Args:
        page_source: XML/HTML representation of the screen
        
    Returns:
        str: A detailed description of the screen
    """
    try:
        # Prepare the prompt
        system_prompt = """
        You are an expert in mobile app testing and analysis.
        Your task is to provide a detailed description of the current screen in the mobile app.
        Focus on:
        1. The main UI elements visible (buttons, text fields, labels, etc.)
        2. The purpose of the screen (login, settings, dashboard, etc.)
        3. The possible actions a user could take on this screen
        4. Any notable features or issues with the UI
        
        Be concise but comprehensive.
        """
        
        user_prompt = f"Here is the page source of the current screen:\n\n{page_source}"
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract the description
        description = response.choices[0].message.content
        logger.info("Generated screen description using OpenAI")
        
        return description
        
    except Exception as e:
        logger.error(f"Error generating screen description: {str(e)}")
        return f"Error generating description: {str(e)}"


def suggest_test_actions(page_source: str) -> list:
    """
    Use OpenAI to suggest test actions based on screen content.
    
    Args:
        page_source: XML/HTML representation of the screen
        
    Returns:
        list: A list of suggested test actions
    """
    try:
        # Prepare the prompt
        system_prompt = """
        You are an expert in mobile app testing.
        Based on the current screen, suggest a list of test actions that would be appropriate.
        Return a JSON array of strings, each containing a natural language test action.
        Focus on:
        1. Functional testing (buttons, inputs, navigation)
        2. Edge cases
        3. User experience testing
        4. Possible regression tests
        
        Limit your suggestions to 5-7 specific actions.
        """
        
        user_prompt = f"Current page source:\n\n{page_source}"
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract and parse the response
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        if isinstance(result, list):
            suggestions = result
        elif isinstance(result, dict) and "suggestions" in result:
            suggestions = result["suggestions"]
        else:
            suggestions = []
            for key, value in result.items():
                if isinstance(value, str):
                    suggestions.append(value)
        
        logger.info(f"Generated {len(suggestions)} test action suggestions using OpenAI")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating test suggestions: {str(e)}")
        return [f"Error generating suggestions: {str(e)}"]


def main():
    """
    Run the standalone OpenAI example.
    """
    try:
        # Sample page source for demonstration
        page_source = """
        <android.widget.FrameLayout>
            <android.widget.LinearLayout>
                <android.widget.TextView text="Welcome to MCP Appium Demo" />
                <android.widget.Button text="Login" content-desc="login_button" />
                <android.widget.EditText hint="Username" content-desc="username_field" />
                <android.widget.EditText hint="Password" content-desc="password_field" />
                <android.widget.CheckBox text="Remember me" checked="false" />
            </android.widget.LinearLayout>
        </android.widget.FrameLayout>
        """
        
        print("\n=== Describing Current Screen ===")
        description = describe_screen(page_source)
        print(description)
        
        print("\n=== Suggesting Test Actions ===")
        suggestions = suggest_test_actions(page_source)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        # Test some natural language commands
        test_commands = [
            "Click the login button",
            "Enter 'testuser' in the username field",
            "Input 'password123' in the password field",
            "Check the 'Remember me' checkbox",
            "Take a screenshot of the login screen"
        ]
        
        print("\n=== Processing Natural Language Commands ===")
        for command in test_commands:
            print(f"\nCommand: '{command}'")
            result = process_command(command, {"page_source": page_source})
            print(f"Status: {result['status']}")
            if result['status'] == 'success':
                print(f"Action: {result['action']}")
                print(f"Parameters: {json.dumps(result['parameters'], indent=2)}")
            else:
                print(f"Error: {result['message']}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in standalone OpenAI example: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())