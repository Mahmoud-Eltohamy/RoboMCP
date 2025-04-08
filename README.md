# MCP Appium - Model Context Protocol for Appium

A Python implementation of Model Context Protocol (MCP) for Appium to enable mobile automation testing.

## Overview

MCP Appium provides a clean API for mobile test automation using the [Model Context Protocol](https://github.com/modelcontextprotocol) with [Appium](https://appium.io). This implementation follows similar patterns to the [MCP-Selenium](https://github.com/angiejones/mcp-selenium) project.

The Model Context Protocol (MCP) is a communication protocol that defines a way for testing tools to interact with applications through a consistent interface. This implementation focuses on mobile testing with Appium.

## Features

- Python-based implementation of the Model Context Protocol
 - **NEW:** Web browser automation with Playwright integration
- Support for both Android and iOS applications
- Clean API similar to Selenium's WebDriver
- Comprehensive error handling and logging
- Extensive documentation and examples
- Docker support for easy setup of Appium and Android emulator
- **NEW:** Web browser automation with Playwright integration
- **NEW:** Multi-provider AI integration with OpenAI, Google Gemini, and Hugging Face
- **NEW:** Advanced error handling with specialized error types for AI integrations
- **NEW:** Configurable retry mechanisms with exponential backoff for API calls
- **NEW:** App structure analysis and test script generation capabilities

## Installation

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-appium.git
cd mcp-appium

# Install dependencies
pip install -e .
```

### Docker Installation

We provide a Docker-based setup for easy development and testing:

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-appium.git
cd mcp-appium

# Start the Docker environment
./scripts/docker-run.sh

# Or with additional options
./scripts/docker-run.sh --build   # Build the images first
./scripts/docker-run.sh -d        # Run in detached mode
```

This will set up:
1. An Appium server
2. An Android emulator with VNC access
3. The MCP Appium application

For more details on the Docker setup, see [DOCKER.md](DOCKER.md)

## AI Integration

MCP Appium provides integration with multiple AI providers to enable natural language interactions with mobile applications.

### Supported AI Providers

- **OpenAI** - Uses OpenAI's GPT models (default: gpt-4o)
- **Google Gemini** - Uses Google's Gemini models
- **Hugging Face** - Connects to Hugging Face's model API (default: Llama-2-70b-chat-hf)

### AI Features

- Natural language command interpretation
- Screen description and analysis
- Test action suggestions based on screen content
- Application structure analysis
- Test script generation
- **NEW:** Multi-language test code generation (Python, Java, JavaScript, C#, Ruby, Robot Framework)

### Example Usage

```python
from mcp_appium.ai_integration import MCPAIIntegration, AIProvider, AIModelConfig

# Create a custom configuration
config = AIModelConfig(
    timeout=30,                 # 30 second timeout
    max_retries=3,              # Retry up to 3 times
    retry_delay=1,              # Start with 1 second delay
    retry_backoff_factor=2.0,   # Double delay with each retry
    temperature=0.5,            # Lower temperature for deterministic responses
    max_tokens=1024             # Maximum tokens to generate
)

# Initialize with OpenAI
mcp_ai = MCPAIIntegration(provider=AIProvider.OPENAI, config=config)

# Or with Google Gemini
# mcp_ai = MCPAIIntegration(provider=AIProvider.GEMINI, config=config)

# Or with Hugging Face
# mcp_ai = MCPAIIntegration(provider=AIProvider.HUGGINGFACE, config=config)

# Interpret a natural language command
result = mcp_ai.interpret_command("Find the login button and click it")

# Get a description of a screen
description = mcp_ai.describe_screen(page_source)

# Get suggestions for test actions
suggestions = mcp_ai.suggest_test_actions(page_source)

# Analyze the structure of an app
app_analysis = mcp_ai.analyze_app_structure([login_screen, home_screen])

# Generate a test script in Python (default)
test_script_py = mcp_ai.generate_test_script(app_analysis, "Test the login functionality")

# Generate test scripts in different programming languages
test_script_java = mcp_ai.generate_test_script_with_interface(
    app_analysis, "Test the login functionality", "java"
)

test_script_js = mcp_ai.generate_test_script_with_interface(
    app_analysis, "Test the login functionality", "javascript"
)

test_script_csharp = mcp_ai.generate_test_script_with_interface(
    app_analysis, "Test the login functionality", "csharp"
)
test_script_ruby = mcp_ai.generate_test_script_with_interface(
    app_analysis, "Test the login functionality", "ruby"
)

test_script_robot = mcp_ai.generate_test_script_with_interface(
    app_analysis, "Test the login functionality", "robot"
)
```

See the `examples` directory for complete examples, including `code_generation_example.py` for multi-language code generation.

### Sauce Labs Demo App Example

We've included an example that demonstrates testing the Sauce Labs Demo App (a real-world mobile e-commerce application) using our AI integration:

```bash
# Run the Sauce Labs Demo App example with Docker
./scripts/run_sauce_labs_docker.sh
```

This example:
1. Sets up the Docker environment with Appium, Android emulator, and MCP Appium
2. Downloads and installs the Sauce Labs Demo App
3. Executes a series of test commands using natural language
4. Demonstrates AI-powered analysis of the app structure

You can find the full example code in `examples/docker_sauce_labs_example.py`.

## Core Appium Usage

For directly using the Appium client without AI integration:

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

## Error Handling

The library includes specialized error types for better error handling:

```python
from mcp_appium.errors import (
    AppiumMCPError,            # Base error class
    AIProviderError,           # Base AI provider error
    AIConnectionError,         # Connection issues
    AIAuthenticationError,     # Authentication problems
    AIQuotaExceededError       # Rate limits exceeded
)

try:
    result = mcp_ai.interpret_command("Find the login button and click it")
except AIConnectionError:
    print("Could not connect to AI provider")
except AIAuthenticationError:
    print("Authentication failed - check your API key")
except AIQuotaExceededError:
    print("API rate limit exceeded")
except AIProviderError as e:
    print(f"Other AI provider error: {e}")
except AppiumMCPError as e:
    print(f"General MCP error: {e}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
## Browser Automation

MCP Appium now includes web browser automation capabilities using Playwright integration. This allows you to test both mobile apps and web applications with the same framework.

### Browser Features

- Cross-browser testing support (Chrome, Firefox, Safari)
- Multi-tab management
- Full DOM element interactions
- Screenshot capture
- JavaScript execution
- Wait mechanisms for dynamic content
- AI integration for web page analysis

### Browser Example

```python
from mcp_appium.browser import server_integration as browser_server

# Initialize browser environment
browser_server.initialize_browser()

# Connect to a browser
capabilities = {
    "browserName": "chromium",
    "headless": True,
    "args": ["--no-sandbox"]
}
browser_server.connect_to_browser(capabilities)

# Navigate to a URL
browser_server.navigate_to_url("https://www.example.com")

# Find an element and click it
element_result = browser_server.find_element("css selector", "h1")
element_id = element_result["element"]["element_id"]
browser_server.click_element(element_id)

# Take a screenshot
browser_server.get_screenshot("/path/to/screenshot.png")

# Close the browser
browser_server.disconnect_from_browser()
```

For more details, see the [Browser Automation Documentation](docs/BROWSER_AUTOMATION.md) and the example at `examples/web_browser_example.py`.
