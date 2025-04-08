"""
MCP Appium Server and Web Interface Main Script
==============================================

This script is the entry point for running both:
1. The MCP Appium web interface (Flask app)
2. The MCP Appium server (when started with appropriate command-line arguments)

By default, this script runs the web interface. To run the MCP server instead,
provide the --server flag.
"""

import argparse
import logging
import os
import sys
import subprocess
from pathlib import Path

# Import the Flask app
from app import app

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

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MCP Appium Server and Web Interface")
    
    # Main mode selection
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run as MCP Appium server (default: run web interface)"
    )
    
    # Server-specific arguments
    parser.add_argument(
        "--host", 
        default=os.environ.get("MCP_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.environ.get("MCP_PORT", "5000")),
        help="Port to listen on (default: 5000)"
    )
    parser.add_argument(
        "--appium-url", 
        default=os.environ.get("APPIUM_URL", "http://localhost:4723"),
        help="URL of the Appium server (default: http://localhost:4723)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("MCP_LOG_LEVEL", "INFO"),
        help="Log level (default: INFO, can be set with MCP_LOG_LEVEL env var)"
    )
    
    # Web interface arguments
    parser.add_argument(
        "--web-port", 
        type=int, 
        default=int(os.environ.get("WEB_PORT", "8501")),
        help="Port for the web interface (default: 8501, Streamlit default)"
    )
    
    return parser.parse_args()

def run_server(args):
    """Run the MCP Appium server."""
    import os
    import uvicorn
    
    # Set environment variables for the MCP server
    os.environ["APPIUM_URL"] = args.appium_url
    os.environ["MCP_LOG_LEVEL"] = args.log_level
    
    # Configure logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting MCP Appium server on {args.host}:{args.port}")
    logger.info(f"Using Appium server at {args.appium_url}")
    
    try:
        # Import and run the MCP server
        from mcp_server import app
        
        # Run the server using Uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Stopping server due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)

def run_web_interface(args):
    """Run the MCP Appium web interface using Flask."""
    # Configure logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Flask web interface on {args.host}:{args.port}")
    
    try:
        # Run the Flask app
        app.run(host=args.host, port=args.port, debug=True)
    except KeyboardInterrupt:
        logger.info("Stopping web interface due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running web interface: {str(e)}")
        sys.exit(1)

def main():
    """Run either the server or the web interface based on command-line arguments."""
    args = parse_args()
    
    if args.server:
        run_server(args)
    else:
        run_web_interface(args)

if __name__ == "__main__":
    main()
