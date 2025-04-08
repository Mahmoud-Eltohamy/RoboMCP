"""
OpenAI Integration for MCP Appium
==================================

This module implements the Model Context Protocol using OpenAI.
It provides functionality to interpret natural language commands
and convert them into Appium actions.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from mcp_appium.client import AppiumClient
from mcp_appium.errors import AppiumMCPError, InvalidArgumentError
from mcp_appium.models import Session

# Configure logging
logger = logging.getLogger(__name__)

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
DEFAULT_MODEL = "gpt-4o"

class MCPOpenAIIntegration:
    """
    Implements the Model Context Protocol using OpenAI.
    
    This class provides methods to:
    1. Interpret natural language commands for mobile testing
    2. Convert them to Appium actions
    3. Execute those actions through the AppiumClient
    """
    
    def __init__(self, appium_client: Optional[AppiumClient] = None):
        """
        Initialize the OpenAI Integration for MCP.
        
        Args:
            appium_client: An optional existing AppiumClient instance.
                           If not provided, a new one will be created.
                           
        Raises:
            AppiumMCPError: If the OpenAI API key is not set
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise AppiumMCPError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            
        self.openai_client = OpenAI(api_key=api_key)
        self.appium_client = appium_client or AppiumClient()
        self.session = None
        self.context = {}  # Store context for conversation
        
    def connect_to_appium(self, url: Optional[str] = None) -> bool:
        """
        Connect to the Appium server.
        
        Args:
            url: Optional URL to connect to
            
        Returns:
            bool: True if connection was successful
            
        Raises:
            ConnectionError: If connection to Appium server fails
        """
        return self.appium_client.connect(url)
    
    def create_session(self, capabilities: Dict[str, Any]) -> bool:
        """
        Create a new Appium session.
        
        Args:
            capabilities: Dictionary containing the desired capabilities
            
        Returns:
            bool: True if session was created successfully
            
        Raises:
            SessionNotCreatedError: If session creation fails
        """
        try:
            self.session = self.appium_client.create_session(capabilities)
            return True
        except AppiumMCPError as e:
            logger.error(f"Failed to create session: {str(e)}")
            return False
    
    def execute_command(self, natural_language_command: str) -> Dict[str, Any]:
        """
        Execute a command expressed in natural language.
        
        Args:
            natural_language_command: A natural language description of the action to perform
            
        Returns:
            Dict: Results of the command execution
            
        Raises:
            InvalidArgumentError: If the command cannot be interpreted
            AppiumMCPError: If command execution fails
        """
        if not natural_language_command:
            raise InvalidArgumentError("Command cannot be empty")
        
        if not self.session:
            raise AppiumMCPError("No active session. Call create_session() first.")
        
        # Update context with the current state
        self._update_context()
        
        # Interpret the natural language command
        interpreted_command = self._interpret_command(natural_language_command)
        
        # Execute the interpreted command
        return self._execute_interpreted_command(interpreted_command)
    
    def _update_context(self):
        """
        Update the context with the current state of the app.
        This provides more context for the OpenAI model to understand the current state.
        """
        if not self.session:
            logger.warning("Cannot update context: No active session")
            return
            
        try:
            # Get page source for context
            self.context["page_source"] = self.session.get_page_source()
            
            # Take a screenshot for visual context (store as a reference)
            self.context["has_screenshot"] = True
            
            # Get current activity/view information
            current_context = self.session.get_current_context()
            self.context["current_context"] = current_context
            
            logger.debug("Updated context information for OpenAI")
        except AppiumMCPError as e:
            logger.warning(f"Could not fully update context: {str(e)}")
    
    def _interpret_command(self, natural_language_command: str) -> Dict[str, Any]:
        """
        Use OpenAI to interpret a natural language command into a structured command.
        
        Args:
            natural_language_command: The natural language command to interpret
            
        Returns:
            Dict: A structured command with action and parameters
            
        Raises:
            InvalidArgumentError: If the command cannot be interpreted
        """
        try:
            # Prepare the prompt with app context
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
            if self.context.get("page_source"):
                # Include a summarized version to avoid token limits
                context_info += "\nCurrent page source (summarized):\n"
                context_info += self.context["page_source"][:500] + "...\n"
            
            if self.context.get("current_context"):
                context_info += f"\nCurrent context: {self.context['current_context']}\n"
            
            if self.context.get("has_screenshot"):
                context_info += "\nA screenshot is available for reference.\n"
            
            user_prompt = f"App state context:{context_info}\n\nCommand to interpret: {natural_language_command}"
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
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
                raise InvalidArgumentError(
                    "OpenAI did not return a properly formatted command. Expected 'action' and 'parameters' fields."
                )
            
            logger.info(f"Interpreted command '{natural_language_command}' as action '{result['action']}' with parameters {result['parameters']}")
            return result
            
        except Exception as e:
            logger.error(f"Error interpreting command: {str(e)}")
            raise InvalidArgumentError(f"Could not interpret command: {str(e)}")
    
    def _execute_interpreted_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the interpreted command.
        
        Args:
            command: A structured command with action and parameters
            
        Returns:
            Dict: Results of the command execution
            
        Raises:
            AppiumMCPError: If command execution fails
        """
        if not self.session:
            return {"status": "error", "message": "No active session. Call create_session() first."}
            
        action = command.get("action")
        parameters = command.get("parameters", {})
        
        try:
            # Check if required parameters are present
            if action == "find_element" or action == "find_elements":
                if "by" not in parameters or "value" not in parameters:
                    return {"status": "error", "message": f"Action {action} requires 'by' and 'value' parameters"}
                    
            elif action in ["click_element", "send_keys", "get_text"]:
                if "element_id" not in parameters:
                    return {"status": "error", "message": f"Action {action} requires 'element_id' parameter"}
                if action == "send_keys" and "text" not in parameters:
                    return {"status": "error", "message": "send_keys action requires 'text' parameter"}
                    
            elif action == "switch_to_context":
                if "context_name" not in parameters:
                    return {"status": "error", "message": "switch_to_context action requires 'context_name' parameter"}
                    
            elif action == "execute_script":
                if "script" not in parameters:
                    return {"status": "error", "message": "execute_script action requires 'script' parameter"}
            
            # Execute the command based on the action type
            if action == "find_element":
                element = self.session.find_element(parameters["by"], parameters["value"])
                return {"status": "success", "element_id": element.id, "message": f"Found element with {parameters['by']}={parameters['value']}"}
                
            elif action == "find_elements":
                elements = self.session.find_elements(parameters["by"], parameters["value"])
                element_ids = [el.id for el in elements]
                return {"status": "success", "element_ids": element_ids, "count": len(elements), "message": f"Found {len(elements)} elements with {parameters['by']}={parameters['value']}"}
                
            elif action == "click_element":
                element_id = parameters["element_id"]
                # Use xpath to find the element by ID
                element = self.session.find_element("xpath", f"//*[@id='{element_id}']")
                element.click()
                return {"status": "success", "message": f"Clicked element with ID {element_id}"}
                
            elif action == "send_keys":
                element_id = parameters["element_id"]
                text = parameters["text"]
                # Use xpath to find the element by ID
                element = self.session.find_element("xpath", f"//*[@id='{element_id}']")
                element.send_keys(text)
                return {"status": "success", "message": f"Sent text '{text}' to element with ID {element_id}"}
                
            elif action == "get_text":
                element_id = parameters["element_id"]
                # Use xpath to find the element by ID
                element = self.session.find_element("xpath", f"//*[@id='{element_id}']")
                text = element.get_text()
                return {"status": "success", "text": text, "message": f"Got text from element with ID {element_id}"}
                
            elif action == "back":
                self.session.back()
                return {"status": "success", "message": "Navigated back"}
                
            elif action == "screenshot":
                screenshot = self.session.get_screenshot()
                return {"status": "success", "screenshot": screenshot, "message": "Took screenshot"}
                
            elif action == "get_contexts":
                contexts = self.session.get_contexts()
                return {"status": "success", "contexts": contexts, "message": f"Found {len(contexts)} contexts"}
                
            elif action == "switch_to_context":
                context_name = parameters["context_name"]
                self.session.switch_to_context(context_name)
                return {"status": "success", "message": f"Switched to context {context_name}"}
                
            elif action == "execute_script":
                script = parameters["script"]
                args = parameters.get("args", [])
                result = self.session.execute_script(script, args)
                return {"status": "success", "result": result, "message": "Executed script"}
                
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def describe_current_screen(self) -> str:
        """
        Use OpenAI to describe the current screen based on page source and screenshot.
        
        Returns:
            str: A description of the current screen
            
        Raises:
            AppiumMCPError: If the description cannot be generated
        """
        if not self.session:
            raise AppiumMCPError("No active session. Call create_session() first.")
        
        try:
            # Update context with latest information
            self._update_context()
            
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
            user_prompt = f"Here is the page source of the current screen:\n\n{self.context.get('page_source', 'No page source available')}"
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
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
            raise AppiumMCPError(f"Could not generate screen description: {str(e)}")
    
    def suggest_test_actions(self) -> List[str]:
        """
        Use OpenAI to suggest possible test actions based on the current screen.
        
        Returns:
            List[str]: A list of suggested test actions
            
        Raises:
            AppiumMCPError: If suggestions cannot be generated
        """
        if not self.session:
            raise AppiumMCPError("No active session. Call create_session() first.")
        
        try:
            # Update context with latest information
            self._update_context()
            
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
            user_prompt = f"Current page source:\n\n{self.context.get('page_source', 'No page source available')}"
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
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
            raise AppiumMCPError(f"Could not generate test suggestions: {str(e)}")
    
    def quit(self):
        """
        Quit the session and clean up resources.
        """
        if self.appium_client and self.appium_client.session_id:
            self.appium_client.quit()
            self.session = None
            logger.info("Session quit and resources cleaned up")