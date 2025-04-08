"""
WSGI Entry Point for MCP Appium Flask App
========================================

This file provides the entry point for WSGI servers like Gunicorn to run the Flask app.
"""

from app import app

# This enables the application to be run with a WSGI server like Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)