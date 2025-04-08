"""
MCP Appium Streamlit Web Interface
==================================

This script serves as the main entry point for the Streamlit web interface.
It loads and manages the structure of the application.
"""

import streamlit as st
import importlib
import sys
import os
from pathlib import Path

# Add the parent directory to the path so modules can be imported properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import pages modules
from web.pages import home, examples, documentation, api_reference, ai_integration

# Project version
MCP_APPIUM_VERSION = "0.1.0"

# Set page configuration
st.set_page_config(
    page_title="MCP Appium",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open(os.path.join("web", "static", "css", "style.css"), "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit app."""
    try:
        load_css()
    except Exception as e:
        # If CSS file doesn't exist yet, use inline CSS
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
    
    # Sidebar navigation
    st.sidebar.title("MCP Appium")
    st.sidebar.markdown(f"Version: {MCP_APPIUM_VERSION}")
    
    pages = {
        "Home": home.render,
        "Examples": examples.render,
        "Documentation": documentation.render,
        "API Reference": api_reference.render,
        "AI Integration": ai_integration.render
    }
    
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    
    # Render the selected page
    pages[selection](MCP_APPIUM_VERSION)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 MCP Appium Project")

if __name__ == "__main__":
    main()