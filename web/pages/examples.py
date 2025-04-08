"""
Examples page for the MCP Appium Streamlit web interface.
"""

import streamlit as st
import os
import importlib.util
from pathlib import Path

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

def render(version):
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