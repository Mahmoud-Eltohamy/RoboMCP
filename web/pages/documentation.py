"""
Documentation page for the MCP Appium Streamlit web interface.
"""

import streamlit as st
from pathlib import Path

def get_md_file_content(file_path):
    """Read the content of a markdown file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading markdown file: {str(e)}"

def render(version):
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