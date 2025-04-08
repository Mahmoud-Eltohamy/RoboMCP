# Browser Automation with MCP Appium

## Overview

MCP Appium provides a unified interface for browser automation using Playwright. This allows you to write tests that target both mobile applications and web browsers using the same API patterns.

## Key Features

- **Cross-Browser Support**: Chrome, Firefox, WebKit
- **Multi-Tab Management**: Create, switch, and close tabs
- **Element Interaction**: Find, click, type, and extract information from elements
- **JavaScript Execution**: Run custom JavaScript in the browser
- **Screenshot Capture**: Take screenshots of the page or elements
- **Headless Mode**: Run browsers without a visible UI
- **Simulation Mode**: Simulate browser actions in environments where browsers can't run

## Getting Started

### Basic Usage

```python
from mcp_appium.client import AppiumClient
from mcp_appium.models import BrowserCapabilities

# Create a client
client = AppiumClient()

# Connect to a browser with capabilities
capabilities = BrowserCapabilities(
    browser_name="chromium",
    headless=True,
    viewport={"width": 1280, "height": 800}
)
session = client.start_browser_session(capabilities)

# Navigate to a URL
session.navigate_to("https://www.example.com")

# Find and interact with elements
element = session.find_element("css selector", "h1")
print(element.text)

# Take a screenshot
screenshot = session.get_screenshot()

# Execute JavaScript
result = session.execute_script("return document.title;")
print(f"Page title: {result}")

# Close the session
session.quit()
```

### Async API

```python
import asyncio
from mcp_appium.browser.browser import Browser
from mcp_appium.browser.context import BrowserContext
from mcp_appium.browser.page import Page

async def run_browser_test():
    # Create a browser instance
    browser = Browser()
    
    # Launch the browser
    await browser.launch(headless=True)
    
    # Create a context with custom viewport and user agent
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.212"
    )
    
    # Create a page
    page = await context.new_page()
    
    # Navigate to a URL
    await page.goto("https://www.example.com")
    
    # Find an element
    element = await page.find_element("css selector", "h1")
    
    # Get element text
    text = await element.get_text()
    print(f"Heading: {text}")
    
    # Close the browser
    await browser.close()

# Run the async function
asyncio.run(run_browser_test())
```

## Simulation Mode

For environments where real browsers can't run (like Replit or CI systems without displays), you can use simulation mode:

```python
import os
from mcp_appium.browser.server_integration import (
    initialize_browser,
    connect_to_browser,
    navigate_to_url,
    find_element,
    get_element_text
)

# Detect if we need simulation mode
simulate = "REPL_ID" in os.environ or "CI" in os.environ

# Initialize browser simulation
initialize_browser(simulate=simulate)

# Connect with capabilities
capabilities = {
    "browserName": "chromium",
    "headless": True,
    "args": ["--no-sandbox"]
}
connect_to_browser(capabilities, simulate=simulate)

# Navigate and interact
navigate_to_url("https://www.example.com", simulate=simulate)
element = find_element("css selector", "h1", simulate=simulate)
text = get_element_text(element["element"]["element_id"], simulate=simulate)
print(f"Heading: {text['text']}")
```

## Element Locators

MCP Appium supports these locator strategies:

- `css selector`: CSS selectors like `div.class`, `#id`, etc.
- `xpath`: XPath expressions like `//div[@class='container']`
- `tag name`: HTML tag names like `h1`, `button`, etc.
- `link text`: Full text of links
- `partial link text`: Partial text of links
- `id`: Element ID attribute

Example:

```python
# Find by CSS selector
element = session.find_element("css selector", ".container button")

# Find by XPath
element = session.find_element("xpath", "//button[@id='submit']")

# Find by tag name
elements = session.find_elements("tag name", "a")

# Find by link text
element = session.find_element("link text", "Click Here")
```

## Multi-Tab Browsing

```python
# Create a new tab
session.create_new_tab()

# Get all tabs
tabs = session.get_window_handles()

# Switch to a specific tab
session.switch_to_window(tabs[1])

# Navigate in the new tab
session.navigate_to("https://www.example.org")

# Switch back to the first tab
session.switch_to_window(tabs[0])
```

## JavaScript Execution

```python
# Execute script with no arguments
title = session.execute_script("return document.title;")

# Execute script with arguments
result = session.execute_script(
    "return arguments[0].innerText;", 
    [element]  # Pass elements as arguments
)

# Modify the page
session.execute_script("""
    const div = document.createElement('div');
    div.innerHTML = 'Added by JavaScript';
    document.body.appendChild(div);
"""
```

## Screenshots

```python
# Capture full page
screenshot = session.get_screenshot()
with open("screenshot.png", "wb") as f:
    f.write(screenshot)

# Capture specific element
element_screenshot = element.get_screenshot()
with open("element.png", "wb") as f:
    f.write(element_screenshot)
```

## Browser Navigation

```python
# Navigate to URL
session.navigate_to("https://www.example.com")

# Refresh the page
session.refresh()

# Go back
session.back()

# Go forward
session.forward()

# Get current URL
url = session.get_current_url()

# Get page title
title = session.get_title()
```

## Examples

See the `examples/` directory for complete examples:

- `web_browser_example.py`: Basic browser automation
- `browser_capabilities_example.py`: Testing browser capabilities
- `comprehensive_api_example.py`: Complete API usage for both mobile and web

## Best Practices

1. **Use Headless Mode**: For CI/CD pipelines and servers, use headless mode for better performance
2. **Clean Up Resources**: Always close browser sessions when done
3. **Handle Timeouts**: Set appropriate timeouts for element finding and page loading
4. **Use Explicit Waits**: Wait for elements to be visible/interactive before interacting
5. **Cross-Browser Testing**: Test on multiple browsers (Chrome, Firefox, Safari)
6. **Responsive Testing**: Test with different viewport sizes
7. **Error Handling**: Implement proper try/except blocks to handle failures
8. **Simulation Support**: Add simulation mode support for environments like Replit
