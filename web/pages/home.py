"""
Home page for the MCP Appium Streamlit web interface.
"""

import streamlit as st

def render(version):
    """Render the home page."""
    st.markdown(f"""
    <div class="header-container">
        <h1>MCP Appium</h1>
        <span class="version-badge">v{version}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>Model Context Protocol for Mobile Testing</h3>
        <p>MCP Appium implements the Model Context Protocol (MCP) to create a bridge between 
        AI-powered tools and the Appium mobile testing framework. It enables natural language 
        processing of commands, AI-assisted test generation, and other advanced capabilities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Features
    st.subheader("Key Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("- **AI-Powered Testing**: Natural language processing of test commands")
        st.markdown("- **Cross-Platform**: Works with both Android and iOS")
        st.markdown("- **Test Script Generation**: Generate test scripts in multiple languages")
    
    with col2:
        st.markdown("- **Multi-Provider AI Support**: OpenAI, Gemini, Ollama, and more")
        st.markdown("- **Docker Integration**: Run the entire stack in Docker")
        st.markdown("- **MCP Protocol**: Compatible with the Model Context Protocol")
    
    # Quick Start
    st.subheader("Quick Start")
    
    st.code("""
# Install MCP Appium
pip install -e .

# Set environment variable for AI integration
export OPENAI_API_KEY=your_api_key

# Start the MCP server
python main.py --server
    """, language="bash")
    
    # Example Usage
    st.subheader("Example Usage")
    
    st.code("""
from mcp_appium.client import AppiumClient
from mcp_appium.ai_integration import MCPAIIntegration, AIProvider

# Create a client
client = AppiumClient()
client.connect("http://localhost:4723")

# Create a session
session = client.create_session({
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android Emulator",
    "appium:appPackage": "com.example.app",
    "appium:appActivity": ".MainActivity"
})

# Use AI integration
ai = MCPAIIntegration(provider=AIProvider.OPENAI)
description = ai.describe_screen(session.get_page_source())
print(f"Screen description: {description}")
    """, language="python")