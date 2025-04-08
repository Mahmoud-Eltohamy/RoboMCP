"""
API Reference page for the MCP Appium Streamlit web interface.
"""

import streamlit as st
import importlib
import inspect

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

def render(version):
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