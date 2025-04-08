"""
MCP Appium Implementation
=========================

This package provides a Python implementation of the Model Context Protocol (MCP) for Appium,
enabling structured mobile automation testing.

The Model Context Protocol (MCP) is a communication protocol that defines a way for testing tools
to interact with applications. This implementation focuses on mobile testing with Appium.

Main components:
- Client: Manages the connection to the Appium server
- Element: Represents elements within the mobile application
- Commands: Implements various commands for app interaction
- Models: Data models for the MCP protocol
- AI Integration: Supports multiple AI providers (OpenAI, Gemini, Hugging Face) to interpret 
  natural language commands and execute them

Example usage:
```python
from mcp_appium.client import AppiumClient

# Initialize the client
client = AppiumClient()

# Connect to an Appium server
client.connect("http://localhost:4723")

# Create a session
caps = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android",
    "appium:app": "/path/to/app.apk"
}
session = client.create_session(caps)

# Find an element
element = session.find_element("id", "login_button")

# Interact with the element
element.click()

# Close the session
session.quit()
```

OpenAI Integration example:
```python
from mcp_appium.openai_integration import MCPOpenAIIntegration

# Initialize the OpenAI integration
mcp = MCPOpenAIIntegration()

# Connect to an Appium server
mcp.connect_to_appium("http://localhost:4723")

# Create a session with desired capabilities
caps = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android",
    "appium:app": "/path/to/app.apk"
}
mcp.create_session(caps)

# Execute a natural language command
result = mcp.execute_command("Find the login button and click it")

# Get a description of the current screen
screen_description = mcp.describe_current_screen()

# Get suggestions for test actions
suggestions = mcp.suggest_test_actions()

# Close the session
mcp.quit()
```

Multi-Provider AI Integration example:
```python
from mcp_appium.ai_integration import AIProvider, MCPAIIntegration

# Initialize the AI integration with a specific provider
mcp_ai = MCPAIIntegration(provider=AIProvider.GEMINI)

# Or use a string to specify the provider
mcp_ai = MCPAIIntegration(provider="huggingface", model="meta-llama/Llama-2-70b-chat-hf")

# Get a description of the screen
screen_description = mcp_ai.describe_screen(page_source)

# Get suggestions for test actions
suggestions = mcp_ai.suggest_test_actions(page_source)

# Interpret a natural language command
result = mcp_ai.interpret_command("Click the login button", context)
```
"""

# Import integrations for easier access
from mcp_appium.openai_integration import MCPOpenAIIntegration
from mcp_appium.ai_integration import AIProvider, MCPAIIntegration
