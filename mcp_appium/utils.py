"""
Utilities module for MCP Appium
===============================

This module provides utility functions and classes for the MCP Appium implementation.
"""

import base64
import logging
import os
import time
from typing import Callable, Any, Optional, List, Dict, Union, Tuple

from .errors import TimeoutError

logger = logging.getLogger(__name__)

def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to a base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Base64-encoded string
        
    Raises:
        FileNotFoundError: If the image file is not found
        IOError: If there is an error reading the file
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode("utf-8")
    except IOError as e:
        logger.error(f"Error reading image file: {str(e)}")
        raise

def decode_base64_to_image(base64_string: str, output_path: str) -> str:
    """
    Decode a base64 string to an image file.
    
    Args:
        base64_string: Base64-encoded string
        output_path: Path to save the image file
        
    Returns:
        str: Path to the saved image file
        
    Raises:
        IOError: If there is an error writing the file
    """
    try:
        image_data = base64.b64decode(base64_string)
        with open(output_path, "wb") as f:
            f.write(image_data)
        return output_path
    except IOError as e:
        logger.error(f"Error writing image file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error decoding base64 string: {str(e)}")
        raise

def wait_for(condition: Callable[[], bool], timeout: int = 30, 
            poll_frequency: float = 0.5, error_message: str = "Timeout waiting for condition") -> bool:
    """
    Wait for a condition to be true.
    
    Args:
        condition: A function that returns a boolean
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check the condition in seconds
        error_message: Error message to use if timeout occurs
        
    Returns:
        bool: True if the condition was met, False otherwise
        
    Raises:
        TimeoutError: If the condition is not met within the timeout
    """
    start_time = time.time()
    end_time = start_time + timeout
    
    while time.time() < end_time:
        if condition():
            return True
        time.sleep(poll_frequency)
    
    # Timeout
    raise TimeoutError(error_message)

def format_locator(by: str, value: str) -> str:
    """
    Format a locator for logging purposes.
    
    Args:
        by: The locator strategy
        value: The locator value
        
    Returns:
        str: Formatted locator string
    """
    return f"{by}={value}"

def parse_desired_capabilities(capabilities_str: str) -> Dict[str, Any]:
    """
    Parse a string of desired capabilities into a dictionary.
    
    Args:
        capabilities_str: String of capabilities in the format "key1=value1,key2=value2"
        
    Returns:
        Dict[str, Any]: Dictionary of capabilities
    """
    if not capabilities_str:
        return {}
    
    capabilities = {}
    
    for item in capabilities_str.split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            # Try to convert values to appropriate types
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                value = float(value)
            
            # Handle Appium-specific capabilities
            if key.startswith("appium:"):
                capabilities[key] = value
            else:
                capabilities[key] = value
    
    return capabilities
