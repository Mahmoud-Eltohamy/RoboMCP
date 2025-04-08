#!/usr/bin/env python3
"""
Multi-Language Test Script Generation Example for MCP Appium
===========================================================

This module demonstrates how to use the enhanced code generation capabilities
of MCP Appium to create test scripts in different programming languages.

Supported languages:
- Python (using Appium Python Client)
- Java (using Java-Client)
- JavaScript (using WebdriverIO)
- C# (using Appium.WebDriver)
- Ruby (using appium_lib)
- Robot Framework (using AppiumLibrary)
"""

import os
import logging
import json
import argparse
from typing import Dict, Any, List, Optional

from mcp_appium.ai_integration import (
    AIProvider, MCPAIIntegration, AIModelConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define a sample app structure for demonstration
SAMPLE_APP_INFO = {
    "app_name": "SauceLabsDemo",
    "platform": "Android",
    "screens": [
        {
            "name": "LoginScreen",
            "elements": [
                {"id": "test-Username", "type": "EditText", "label": "Username input field"},
                {"id": "test-Password", "type": "EditText", "label": "Password input field"},
                {"id": "test-LOGIN", "type": "Button", "label": "Login button"}
            ]
        },
        {
            "name": "ProductsScreen",
            "elements": [
                {"id": "test-PRODUCTS", "type": "TextView", "label": "Products title"},
                {"id": "test-Item", "type": "RecyclerView", "label": "Product list"},
                {"id": "test-Cart", "type": "Button", "label": "Shopping cart"},
                {"id": "test-Menu", "type": "Button", "label": "Menu button"}
            ]
        },
        {
            "name": "ProductDetailsScreen",
            "elements": [
                {"id": "test-Description", "type": "TextView", "label": "Product description"},
                {"id": "test-BACK TO PRODUCTS", "type": "Button", "label": "Back button"},
                {"id": "test-ADD TO CART", "type": "Button", "label": "Add to cart button"},
                {"id": "test-Price", "type": "TextView", "label": "Product price"}
            ]
        }
    ],
    "navigation": [
        {"from": "LoginScreen", "to": "ProductsScreen", "action": "login"},
        {"from": "ProductsScreen", "to": "ProductDetailsScreen", "action": "click_product"},
        {"from": "ProductDetailsScreen", "to": "ProductsScreen", "action": "back"}
    ]
}

# Sample test goals for demonstration
SAMPLE_TEST_GOALS = {
    "login": "Test the login functionality with valid credentials",
    "browse_products": "Browse the products list and verify product details",
    "add_to_cart": "Add products to the shopping cart and verify cart contents",
    "checkout": "Complete the checkout process with a valid payment method"
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate test scripts in different programming languages')
    parser.add_argument('--provider', default='openai', help='AI provider to use (openai, gemini, huggingface)')
    parser.add_argument('--language', default='python', help='Programming language to generate (python, java, javascript, csharp, ruby, robot)')
    parser.add_argument('--test-goal', default='login', choices=SAMPLE_TEST_GOALS.keys(), help='Test goal to implement')
    parser.add_argument('--output-dir', default='generated_code', help='Directory to save generated code')
    parser.add_argument('--list-languages', action='store_true', help='List supported programming languages and exit')
    return parser.parse_args()


def create_ai_integration(provider: str) -> MCPAIIntegration:
    """
    Create and initialize an MCPAIIntegration instance.
    
    Args:
        provider: Name of the AI provider
    
    Returns:
        MCPAIIntegration: The configured AI integration instance
    """
    # Create a custom configuration with lower temperature for more deterministic outputs
    config = AIModelConfig(
        temperature=0.3,  # Lower temperature for more deterministic code generation
        max_tokens=2048,  # More tokens for complex code generation
        timeout=60,       # Longer timeout for complex generations
        max_retries=2     # Retry logic for API failures
    )
    
    if provider == 'openai':
        return MCPAIIntegration(provider=AIProvider.OPENAI, config=config)
    elif provider == 'gemini':
        return MCPAIIntegration(provider=AIProvider.GEMINI, config=config)
    elif provider == 'huggingface':
        return MCPAIIntegration(provider="huggingface", config=config)
    else:
        # Default to OpenAI
        return MCPAIIntegration(provider=AIProvider.OPENAI, config=config)


def save_generated_code(code: str, language: str, test_goal: str, output_dir: str) -> str:
    """
    Save the generated code to a file.
    
    Args:
        code: The generated code
        language: The programming language
        test_goal: The test goal
        output_dir: The output directory
    
    Returns:
        str: Path to the saved file
    """
    # Map of languages to file extensions
    extensions = {
        "python": "py",
        "java": "java",
        "javascript": "js",
        "js": "js",
        "nodejs": "js",
        "csharp": "cs",
        "c#": "cs",
        "dotnet": "cs",
        "ruby": "rb",
        "robot": "robot",
        "robotframework": "robot"
    }
    
    # Use the correct file extension
    ext = extensions.get(language.lower(), "txt")
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a clean filename from the test goal
    clean_test_goal = test_goal.replace(" ", "_").lower()
    
    # Create the output filename
    filename = f"{clean_test_goal}_{language.lower()}.{ext}"
    filepath = os.path.join(output_dir, filename)
    
    # Write the code to the file
    with open(filepath, 'w') as f:
        f.write(code)
    
    logger.info(f"Generated code saved to: {filepath}")
    return filepath


def list_supported_languages():
    """List all supported programming languages for code generation."""
    supported_languages = [
        "python - Appium Python Client",
        "java - Java-Client with JUnit/TestNG",
        "javascript (js, nodejs) - WebdriverIO with Mocha/Jasmine",
        "csharp (c#, dotnet) - Appium.WebDriver with NUnit/MSTest",
        "ruby - appium_lib with RSpec/Test::Unit",
        "robot (robotframework) - Robot Framework with AppiumLibrary"
    ]
    
    print("\nSupported Programming Languages for Appium Test Script Generation:")
    print("=================================================================")
    for lang in supported_languages:
        print(f"- {lang}")
    print("\nExample usage:")
    print("python code_generation_example.py --language java --test-goal login")
    print("python code_generation_example.py --language robot --test-goal login")


def main():
    """Run the multi-language test script generation example."""
    args = parse_args()
    
    # If --list-languages flag is provided, show the list of supported languages and exit
    if args.list_languages:
        list_supported_languages()
        return
    
    try:
        # Create and initialize the MCPAIIntegration
        mcp_ai = create_ai_integration(args.provider)
        logger.info(f"Successfully initialized {args.provider} AI integration")
        
        # Get the test goal from the predefined samples
        test_goal = SAMPLE_TEST_GOALS[args.test_goal]
        
        # Generate a test script in the specified language
        logger.info(f"Generating {args.language} test script for goal: {test_goal}")
        code = mcp_ai.generate_test_script_with_interface(
            app_info=SAMPLE_APP_INFO,
            test_goal=test_goal,
            language=args.language
        )
        
        # Save the generated code to a file
        filepath = save_generated_code(code, args.language, args.test_goal, args.output_dir)
        
        # Print the first few lines of the generated code
        preview_lines = code.split('\n')[:10]
        preview = '\n'.join(preview_lines)
        
        logger.info(f"Successfully generated {args.language} test script")
        print(f"\nPreview of generated {args.language} code:")
        print("=" * 50)
        print(preview)
        print("..." if len(preview_lines) < len(code.split('\n')) else "")
        print("=" * 50)
        print(f"Full code saved to: {filepath}")
        
    except Exception as e:
        logger.error(f"Error generating test script: {e}")


if __name__ == "__main__":
    main()