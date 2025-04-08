"""
MCP Appium Web Interface
========================

This module provides a web interface to interact with the MCP Appium implementation.
It allows users to view information about the project and examples.
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

@app.route('/')
def index():
    """Render the home page."""
    # Get a list of example files for the home page
    examples_folder = os.path.join(os.path.dirname(__file__), 'examples')
    example_files = []
    
    if os.path.exists(examples_folder):
        example_files = [f for f in os.listdir(examples_folder) if f.endswith('.py')]
    
    # Sort examples to put key ones at the top
    featured_examples = ['mock_example.py', 'android_example.py', 'comprehensive_api_example.py', 
                         'code_generation_example.py', 'ollama_example.py', 'openai_example.py']
    # Move featured examples to the top of the list
    for example in reversed(featured_examples):
        if example in example_files:
            example_files.remove(example)
            example_files.insert(0, example)
    
    return render_template('index.html', title="MCP Appium - Home", examples=example_files)

@app.route('/getting-started')
def getting_started():
    """Render the getting started page."""
    return render_template('getting_started.html', title="MCP Appium - Getting Started")

@app.route('/examples')
def examples():
    """Render the examples page."""
    examples_folder = os.path.join(os.path.dirname(__file__), 'examples')
    example_files = []
    
    if os.path.exists(examples_folder):
        example_files = [f for f in os.listdir(examples_folder) if f.endswith('.py')]
    
    return render_template('examples.html', title="MCP Appium - Examples", examples=example_files)

@app.route('/examples/<filename>')
def show_example(filename):
    """Show the content of an example file."""
    example_path = os.path.join(os.path.dirname(__file__), 'examples', filename)
    
    if not os.path.exists(example_path) or not filename.endswith('.py'):
        return redirect(url_for('examples'))
    
    with open(example_path, 'r') as f:
        content = f.read()
    
    return render_template('simple.html', title=f"Example: {filename}", content=content)

@app.route('/documentation')
def documentation():
    """Render the documentation page."""
    docs_folder = os.path.join(os.path.dirname(__file__), 'docs')
    docs_files = []
    
    if os.path.exists(docs_folder):
        docs_files = [f for f in os.listdir(docs_folder) if f.endswith('.md')]
    
    return render_template('documentation.html', title="MCP Appium - Documentation", docs=docs_files)

@app.route('/api')
def api():
    """Render the API reference page."""
    return render_template('api.html', title="MCP Appium - API Reference", api_docs=generate_api_docs())

@app.route('/ai-integration')
def ai_integration():
    """Render the AI integration page."""
    return render_template('ai_integration.html', title="MCP Appium - AI Integration")

@app.route('/comprehensive-example')
def comprehensive_example():
    """Render the comprehensive API example page."""
    example_path = os.path.join(os.path.dirname(__file__), 'examples', 'comprehensive_api_example.py')
    
    if os.path.exists(example_path):
        with open(example_path, 'r') as f:
            content = f.read()
        return render_template('simple.html', title="Comprehensive API Example", 
                              content=content, 
                              description="This example demonstrates all major Appium API methods implemented in the MCP Appium package.")

@app.route('/streamlit')
def streamlit_redirect():
    """Redirect to the Streamlit interface."""
    streamlit_url = "http://localhost:8501"
    return redirect(streamlit_url)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

def generate_api_docs():
    """Generate API documentation from the mcp_appium package."""
    docs = {}
    
    try:
        import mcp_appium
        
        # Get a list of modules in the package
        modules = dir(mcp_appium)
        
        for module_name in modules:
            if module_name.startswith('__'):
                continue
                
            try:
                module = getattr(mcp_appium, module_name)
                
                if not hasattr(module, '__file__'):
                    continue
                    
                classes = {}
                
                for item_name in dir(module):
                    if item_name.startswith('__'):
                        continue
                        
                    item = getattr(module, item_name)
                    
                    if isinstance(item, type):
                        methods = {}
                        
                        for method_name in dir(item):
                            if method_name.startswith('__'):
                                continue
                                
                            method = getattr(item, method_name)
                            
                            if callable(method):
                                methods[method_name] = str(method.__doc__ or "No documentation available.")
                        
                        classes[item_name] = methods
                
                docs[module_name] = classes
                
            except Exception as e:
                logger.error(f"Error processing module {module_name}: {str(e)}")
        
    except ImportError:
        logger.error("Could not import mcp_appium package")
        
    return docs

def create_required_directories():
    """Create required directories for the application."""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create other required directories
    required_dirs = ["logs", "screenshots", "generated_scripts"]
    for dirname in required_dirs:
        os.makedirs(os.path.join("data", dirname), exist_ok=True)

# Create required directories
create_required_directories()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)