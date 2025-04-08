"""
Configuration module for MCP Appium
==================================

This module contains configuration constants and settings for the MCP Appium implementation.
"""

import logging
import os
from typing import Dict, Any

# Default settings
DEFAULT_APPIUM_URL = os.environ.get("APPIUM_URL", "http://localhost:4723")
DEFAULT_PORT = int(os.environ.get("MCP_PORT", "5000"))
DEFAULT_TIMEOUT = int(os.environ.get("APPIUM_TIMEOUT", "30"))
DEFAULT_POLL_FREQUENCY = float(os.environ.get("APPIUM_POLL_FREQUENCY", "0.5"))
DEFAULT_LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "INFO")

# Logging setup
def configure_logging(level: str = DEFAULT_LOG_LEVEL) -> None:
    """
    Configure logging for the MCP Appium implementation.
    
    Args:
        level: The log level (default: INFO)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# Default capabilities templates
DEFAULT_ANDROID_CAPABILITIES: Dict[str, Any] = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android",
    "appium:newCommandTimeout": DEFAULT_TIMEOUT
}

DEFAULT_IOS_CAPABILITIES: Dict[str, Any] = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:deviceName": "iPhone",
    "appium:newCommandTimeout": DEFAULT_TIMEOUT
}

# Locator strategies
LOCATOR_STRATEGIES = {
    "id": "id",
    "xpath": "xpath",
    "name": "name",
    "class_name": "className",
    "accessibility_id": "accessibility id",
    "ios_predicate": "-ios predicate string",
    "ios_class_chain": "-ios class chain",
    "android_uiautomator": "-android uiautomator",
    "android_viewtag": "-android viewtag",
    "android_datamatcher": "-android datamatcher"
}

# Context types
CONTEXT_NATIVE = "NATIVE_APP"
CONTEXT_WEBVIEW_PREFIX = "WEBVIEW_"
