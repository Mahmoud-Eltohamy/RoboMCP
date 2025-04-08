"""
AI Integration page for the MCP Appium Streamlit web interface.
"""

import streamlit as st

def render(version):
    """Render the AI integration page."""
    st.title("AI Integration")
    
    st.markdown("""
    MCP Appium provides integration with various AI providers to enable natural language
    processing of commands, AI-assisted test generation, and other advanced capabilities.
    """)
    
    # AI Provider Overview
    st.subheader("Supported AI Providers")
    
    providers = [
        {
            "name": "OpenAI",
            "description": "Integration with OpenAI models like GPT-4o for advanced language understanding.",
            "setup": """
# Set environment variables
export OPENAI_API_KEY=your_api_key
export OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o
            """
        },
        {
            "name": "Google Gemini",
            "description": "Integration with Google's Gemini models for language processing.",
            "setup": """
# Set environment variables
export GEMINI_API_KEY=your_api_key
export GEMINI_MODEL=gemini-pro  # Optional, defaults to gemini-pro
            """
        },
        {
            "name": "Ollama",
            "description": "Integration with Ollama for local, self-hosted language models.",
            "setup": """
# Set environment variables
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=mistral:7b-instruct  # Optional, defaults to mistral:7b-instruct
            """
        }
    ]
    
    for provider in providers:
        with st.expander(provider["name"], expanded=False):
            st.markdown(f"### {provider['name']}")
            st.markdown(provider["description"])
            st.markdown("#### Setup")
            st.code(provider["setup"], language="bash")
    
    # Example usage
    st.subheader("Example Usage")
    
    st.code("""
from mcp_appium.ai_integration import MCPAIIntegration, AIProvider

# Initialize AI integration with OpenAI
ai = MCPAIIntegration(provider=AIProvider.OPENAI)

# Describe a screen
screen_description = ai.describe_screen(page_source)
print(f"Screen description: {screen_description}")

# Interpret a natural language command
command = "Click the login button"
action = ai.interpret_command(command, {"page_source": page_source})
print(f"Interpreted command: {action}")

# Generate a test script
test_goal = "Test the login functionality"
script = ai.generate_test_script(
    {"page_source": page_source, "platform": "Android"},
    test_goal
)
print(f"Generated test script: {script}")
    """, language="python")
    
    # AI Capabilities
    st.subheader("AI Capabilities")
    
    capabilities = [
        ("Screen Description", "Analyze and describe the current screen"),
        ("Command Interpretation", "Convert natural language commands to structured actions"),
        ("Test Suggestion", "Generate testing suggestions for the current screen"),
        ("Script Generation", "Create test scripts in multiple programming languages"),
        ("App Structure Analysis", "Analyze the structure of a mobile application")
    ]
    
    for title, desc in capabilities:
        st.markdown(f"**{title}**: {desc}")