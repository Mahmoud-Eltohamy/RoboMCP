"""
MCP Appium - Browser Module
==========================

This module extends the MCP Appium framework to include web browser automation
capabilities using Playwright.

It provides:
1. Browser session management
2. Page interaction methods
3. Element finding and manipulation
4. Integration with the MCP protocol

This allows the MCP Appium framework to automate both mobile applications and web
applications in a unified manner.
"""

from .browser import Browser
from .page import Page
from .context import BrowserContext
from .element import WebElement

# Export classes
__all__ = ["Browser", "Page", "BrowserContext", "WebElement"]