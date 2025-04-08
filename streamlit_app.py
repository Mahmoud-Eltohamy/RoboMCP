"""
MCP Appium Streamlit Web Interface
==================================

This script provides a modern web interface for the MCP Appium implementation
using Streamlit. It allows users to view documentation, examples, and interact
with the MCP Appium server.
"""

import os
import sys
import importlib
import inspect
import streamlit as st
import base64
from pathlib import Path

# Project version
MCP_APPIUM_VERSION = "0.1.0"

# Set page configuration
st.set_page_config(
    page_title="MCP Appium",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .code-block {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
        white-space: pre-wrap;
        overflow-x: auto;
    }
    .info-box {
        background-color: #e1f5fe;
        border-left: 5px solid #039be5;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .version-badge {
        background-color: #039be5;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

def get_example_files():
    """Get a list of example Python files."""
    example_files = []
    example_dir = Path("examples")
    if example_dir.exists():
        example_files = [f.name for f in example_dir.glob("*.py")]
    return sorted(example_files)

def read_file_content(file_path):
    """Read the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_md_file_content(file_path):
    """Read the content of a markdown file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading markdown file: {str(e)}"

def generate_api_docs():
    """Generate API documentation from the mcp_appium package."""
    modules = []
    
    try:
        import mcp_appium
        
        # Define the modules to document
        module_names = [
            'client', 'commands', 'element', 'context',
            'models', 'server', 'errors', 'utils', 'ai_integration'
        ]
        
        for module_name in module_names:
            try:
                module_path = f'mcp_appium.{module_name}'
                module = importlib.import_module(module_path)
                
                module_info = {
                    'name': module_name,
                    'description': module.__doc__.strip() if module.__doc__ else 'No description available',
                    'classes': []
                }
                
                # Get all classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_path:
                        class_info = {
                            'name': name,
                            'description': obj.__doc__.strip() if obj.__doc__ else 'No description available',
                            'methods': []
                        }
                        
                        # Get all methods in the class
                        for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                            if not method_name.startswith('_'):
                                method_info = {
                                    'name': method_name,
                                    'description': method.__doc__.strip() if method.__doc__ else 'No description available',
                                    'signature': str(inspect.signature(method))
                                }
                                class_info['methods'].append(method_info)
                        
                        module_info['classes'].append(class_info)
                
                modules.append(module_info)
            except ImportError:
                st.warning(f"Module {module_name} could not be imported")
    except ImportError:
        st.warning("mcp_appium package not found in the Python path")
    
    return modules

def home_page():
    """Render the home page."""
    st.markdown("""
    <div class="header-container">
        <h1>MCP Appium</h1>
        <span class="version-badge">v{}</span>
    </div>
    """.format(MCP_APPIUM_VERSION), unsafe_allow_html=True)
    
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

def examples_page():
    """Render the examples page."""
    st.title("Examples")
    
    st.markdown("""
    This page provides example scripts demonstrating how to use MCP Appium for various use cases.
    Select an example from the dropdown to view its code.
    """)
    
    example_files = get_example_files()
    
    if not example_files:
        st.warning("No example files found in the 'examples' directory.")
        return
    
    selected_example = st.selectbox("Select an example:", example_files)
    
    if selected_example:
        st.subheader(selected_example)
        
        example_path = os.path.join("examples", selected_example)
        example_content = read_file_content(example_path)
        
        with st.expander("View Code", expanded=True):
            st.code(example_content, language="python")
        
        # Extract docstring for description
        try:
            spec = importlib.util.spec_from_file_location("example_module", example_path)
            example_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(example_module)
            
            if example_module.__doc__:
                st.markdown("### Description")
                st.markdown(example_module.__doc__)
        except Exception:
            pass
        
        # Run example button (simulated)
        if st.button(f"Run {selected_example}"):
            st.info("⚠️ This is a simulation. In a real environment, this would run the example.")
            st.code(f"python examples/{selected_example}", language="bash")
            
            # Show a mock output
            with st.expander("Example Output"):
                st.code(f"""
Running {selected_example}...
Initializing Appium client...
Connecting to Appium server at http://localhost:4723...
Creating session with capabilities:
    platformName: Android
    appium:automationName: UiAutomator2
    appium:deviceName: Android Emulator
[Simulated output - actual execution would connect to a real device/emulator]
                """)

def documentation_page():
    """Render the documentation page."""
    st.title("Documentation")
    
    # Check if we have markdown docs
    docs = []
    docs_dir = Path("docs")
    if docs_dir.exists():
        docs = [f for f in docs_dir.glob("*.md")]
    
    if docs:
        doc_names = [doc.stem for doc in docs]
        selected_doc = st.selectbox("Select Documentation:", doc_names)
        
        if selected_doc:
            doc_path = docs_dir / f"{selected_doc}.md"
            doc_content = get_md_file_content(str(doc_path))
            st.markdown(doc_content)
    else:
        st.markdown("""
        ## MCP Appium Documentation
        
        MCP Appium is a framework that implements the Model Context Protocol (MCP) for mobile testing
        with Appium. It provides a bridge between AI models and the Appium mobile testing framework.
        
        ### Key Concepts
        
        1. **MCP Server**: The core server that exposes MCP tools for mobile testing.
        2. **AI Integration**: Integration with AI providers for natural language processing.
        3. **Appium Client**: A client for communicating with the Appium server.
        4. **Docker Integration**: Running the entire stack in Docker containers.
        
        ### Getting Started
        
        To get started with MCP Appium, follow these steps:
        
        1. Install dependencies: `pip install -e .`
        2. Set up environment variables for AI integration
        3. Start the MCP server: `python main.py --server`
        4. Connect to the server using the client API
        
        ### Configuration
        
        MCP Appium can be configured through environment variables:
        
        - `APPIUM_URL`: URL of the Appium server (default: http://localhost:4723)
        - `OPENAI_API_KEY`: API key for OpenAI integration
        - `GEMINI_API_KEY`: API key for Google Gemini integration
        - `OLLAMA_BASE_URL`: Base URL for Ollama integration
        """)

def api_reference_page():
    """Render the API reference page."""
    st.title("API Reference")
    
    st.markdown("""
    This page provides reference documentation for the MCP Appium API.
    """)
    
    modules = generate_api_docs()
    
    if not modules:
        st.warning("Could not generate API documentation. Make sure the mcp_appium package is installed.")
        return
    
    for module in modules:
        with st.expander(f"Module: {module['name']}", expanded=False):
            st.markdown(f"### {module['name']}")
            st.markdown(module['description'])
            
            for class_info in module['classes']:
                st.markdown(f"#### Class: {class_info['name']}")
                st.markdown(class_info['description'])
                
                if class_info['methods']:
                    for method in class_info['methods']:
                        st.markdown(f"##### `{method['name']}{method['signature']}`")
                        st.markdown(method['description'])
                else:
                    st.markdown("No public methods found.")

def ai_integration_page():
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

def main():
    """Main function to run the Streamlit app."""
    # Sidebar navigation
    st.sidebar.title("MCP Appium")
    st.sidebar.markdown(f"Version: {MCP_APPIUM_VERSION}")
    
    pages = {
        "Home": home_page,
        "Examples": examples_page,
        "Documentation": documentation_page,
        "API Reference": api_reference_page,
        "AI Integration": ai_integration_page
    }
    
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    
    # Render the selected page
    pages[selection]()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 MCP Appium Project")

if __name__ == "__main__":
    main()