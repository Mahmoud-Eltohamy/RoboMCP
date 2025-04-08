# Streamlit Interface for MCP Appium

## Overview

MCP Appium includes a Streamlit-based web interface for interacting with the framework. This interface provides a graphical way to:

- Run automation examples
- View documentation
- Generate test scripts
- Analyze app screens
- Visualize results

## Setup

To start the Streamlit interface, run:

```bash
python run_streamlit.py
```

Or in Docker:

```bash
docker-compose up -d mcp-appium-streamlit
```

The interface will be available at http://localhost:8501.

## Features

### Home Page

The home page provides an overview of the MCP Appium framework and quick links to:

- Documentation
- Examples
- API Reference
- AI Integration tools

### Examples

The Examples page lets you run various demonstration examples directly from the interface:

- Basic Appium example
- Comprehensive API example
- AI integration example
- Android example
- iOS example
- Browser automation example
- Multi-provider example

Each example includes a description, code display, and execution button.

### API Reference

The API Reference page displays auto-generated documentation for:

- AppiumClient
- Session
- Element
- Commands
- AI Integration
- Browser automation components

### AI Integration

The AI Integration page provides interactive tools for:

- Analyzing app screens
- Generating test scripts in multiple languages
- Interpreting natural language commands
- Testing AI capabilities with different providers

You can upload screenshots, specify configurations, and see results in real-time.

### Documentation

The Documentation page provides comprehensive guides on:

- Getting started with MCP Appium
- Using the Docker environment
- Working with AI providers
- Browser automation basics
- Advanced usage examples

## Browser Example Interface

The browser example interface provides a way to:

1. Connect to a web browser
2. Navigate to URLs
3. Interact with elements
4. Execute JavaScript
5. Take screenshots
6. View the DOM structure

This makes it easy to test and demonstrate the browser automation capabilities without writing code.

## Configuration

The Streamlit interface can be configured through `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#f63366"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#1a1a1a"
textColor = "#fafafa"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

## Extending the Interface

To add new components or pages:

1. Create a new Python file in the `web/pages/` directory
2. Import Streamlit and define your page
3. The page will appear automatically in the sidebar

Example:

```python
import streamlit as st

def show():
    st.title("New Feature")
    st.write("This is a new feature page")
    
    # Your Streamlit components here
    
if __name__ == "__main__":
    show()
```
