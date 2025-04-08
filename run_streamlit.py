"""
MCP Appium Streamlit Launcher
=============================

This script starts the Streamlit web interface for MCP Appium.
"""

import subprocess
import sys
import logging
from pathlib import Path

def main():
    """Run the Streamlit app."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    streamlit_app_path = Path("web/app.py")
    
    if not streamlit_app_path.exists():
        logger.error(f"Error: Streamlit app file not found at {streamlit_app_path}")
        sys.exit(1)
    
    logger.info("Starting Streamlit web interface...")
    
    try:
        # Run Streamlit using the app in web/app.py
        streamlit_cmd = [
            "streamlit", "run", str(streamlit_app_path),
            "--server.port", "5000",  # Using port 5000 for consistency with Replit's port binding
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.serverAddress", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ]
        
        # Execute streamlit command
        logger.info(f"Executing: {' '.join(streamlit_cmd)}")
        subprocess.run(streamlit_cmd)
        
    except KeyboardInterrupt:
        logger.info("Stopping web interface due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running web interface: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()