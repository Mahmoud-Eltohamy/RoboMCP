#!/usr/bin/env python3
"""
Ollama Integration Example for MCP Appium
=========================================

This module demonstrates how to use the Ollama integration in MCP Appium.
It allows running AI models locally without requiring external API keys.

This example:
1. Initializes the MCP Appium AI integration with Ollama
2. Demonstrates basic functionality like describing a screen and suggesting test actions
3. Shows how to configure the Ollama endpoint and model

Requirements:
- Ollama service running locally or in a container
- A downloaded model in Ollama (pulls automatically if not available)

Note: For Docker setup, make sure Ollama service is included in the docker-compose.yml
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, List, Any, Optional

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from mcp_appium.ai_integration import MCPAIIntegration, AIProvider, AIModelConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ollama Example for MCP Appium")
    
    parser.add_argument(
        "--ollama-host",
        type=str,
        default=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        help="Ollama host URL (default: http://localhost:11434)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="mistral:7b-instruct",
        help="Ollama model to use (default: mistral:7b-instruct)"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for model generation (default: 0.7)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Maximum number of tokens to generate (default: 1024)"
    )
    
    return parser.parse_args()


def create_mcp_ai_integration(ollama_host: str, model: str, temperature: float, max_tokens: int) -> MCPAIIntegration:
    """
    Create and initialize an MCPAIIntegration instance with Ollama.
    
    Args:
        ollama_host: URL of the Ollama service
        model: Name of the model to use
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        
    Returns:
        MCPAIIntegration: The configured AI integration instance
    """
    # Configure the AI model
    config = AIModelConfig(
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=120,  # Longer timeout for local models which might be slower
        max_retries=2
    )
    
    try:
        # Initialize with Ollama provider
        # Note: For Ollama, we pass the host URL as the api_key parameter
        mcp_ai = MCPAIIntegration(
            provider=AIProvider.OLLAMA,
            api_key=ollama_host,  # This is used as the ollama_host parameter
            model=model,
            config=config
        )
        
        logger.info(f"Successfully initialized Ollama integration with model {model}")
        return mcp_ai
    except Exception as e:
        logger.error(f"Failed to initialize Ollama integration: {str(e)}")
        raise


def demonstrate_screen_description(mcp_ai: MCPAIIntegration):
    """
    Demonstrate the screen description functionality.
    
    Args:
        mcp_ai: The MCPAIIntegration instance
    """
    # Sample XML from an Android screen (simplified)
    page_source = """
    <hierarchy rotation="0">
      <android.widget.FrameLayout bounds="[0,0][1080,2400]">
        <android.widget.LinearLayout bounds="[0,0][1080,2400]">
          <android.widget.FrameLayout bounds="[0,81][1080,2400]">
            <android.widget.FrameLayout bounds="[0,0][1080,2319]">
              <android.view.ViewGroup bounds="[0,0][1080,2319]">
                <android.view.ViewGroup bounds="[0,0][1080,2319]">
                  <android.widget.TextView bounds="[43,66][402,156]" text="Products" />
                  <android.widget.ImageView bounds="[978,66][1036,156]" content-desc="Cart with items" />
                  <android.view.ViewGroup bounds="[0,177][1080,2319]">
                    <android.widget.ScrollView bounds="[0,0][1080,2142]">
                      <android.view.ViewGroup bounds="[0,0][1080,1708]">
                        <android.view.ViewGroup bounds="[0,0][1080,1708]">
                          <android.view.ViewGroup bounds="[42,0][519,650]">
                            <android.widget.ImageView bounds="[42,22][519,354]" content-desc="Sauce Labs Backpack" />
                            <android.widget.TextView bounds="[42,376][519,431]" text="Sauce Labs Backpack" />
                            <android.widget.TextView bounds="[42,443][519,480]" text="$29.99" />
                          </android.view.ViewGroup>
                          <android.view.ViewGroup bounds="[561,0][1038,650]">
                            <android.widget.ImageView bounds="[561,22][1038,354]" content-desc="Sauce Labs Bike Light" />
                            <android.widget.TextView bounds="[561,376][1038,431]" text="Sauce Labs Bike Light" />
                            <android.widget.TextView bounds="[561,443][1038,480]" text="$9.99" />
                          </android.view.ViewGroup>
                          <android.view.ViewGroup bounds="[42,692][519,1342]">
                            <android.widget.ImageView bounds="[42,714][519,1046]" content-desc="Sauce Labs Bolt T-Shirt" />
                            <android.widget.TextView bounds="[42,1068][519,1123]" text="Sauce Labs Bolt T-Shirt" />
                            <android.widget.TextView bounds="[42,1135][519,1172]" text="$15.99" />
                          </android.view.ViewGroup>
                        </android.view.ViewGroup>
                      </android.view.ViewGroup>
                    </android.widget.ScrollView>
                  </android.view.ViewGroup>
                </android.view.ViewGroup>
              </android.view.ViewGroup>
            </android.widget.FrameLayout>
          </android.widget.FrameLayout>
        </android.widget.LinearLayout>
      </android.widget.FrameLayout>
    </hierarchy>
    """
    
    logger.info("Generating screen description using Ollama...")
    description = mcp_ai.describe_screen(page_source)
    
    logger.info("\n--- Screen Description ---\n")
    print(description)
    print("\n-------------------------\n")


def demonstrate_test_suggestions(mcp_ai: MCPAIIntegration):
    """
    Demonstrate the test suggestion functionality.
    
    Args:
        mcp_ai: The MCPAIIntegration instance
    """
    # Use the same page source from above
    page_source = """
    <hierarchy rotation="0">
      <android.widget.FrameLayout bounds="[0,0][1080,2400]">
        <android.widget.LinearLayout bounds="[0,0][1080,2400]">
          <android.widget.FrameLayout bounds="[0,81][1080,2400]">
            <android.widget.FrameLayout bounds="[0,0][1080,2319]">
              <android.view.ViewGroup bounds="[0,0][1080,2319]">
                <android.view.ViewGroup bounds="[0,0][1080,2319]">
                  <android.widget.TextView bounds="[43,66][402,156]" text="Products" />
                  <android.widget.ImageView bounds="[978,66][1036,156]" content-desc="Cart with items" />
                  <android.view.ViewGroup bounds="[0,177][1080,2319]">
                    <android.widget.ScrollView bounds="[0,0][1080,2142]">
                      <android.view.ViewGroup bounds="[0,0][1080,1708]">
                        <android.view.ViewGroup bounds="[0,0][1080,1708]">
                          <android.view.ViewGroup bounds="[42,0][519,650]">
                            <android.widget.ImageView bounds="[42,22][519,354]" content-desc="Sauce Labs Backpack" />
                            <android.widget.TextView bounds="[42,376][519,431]" text="Sauce Labs Backpack" />
                            <android.widget.TextView bounds="[42,443][519,480]" text="$29.99" />
                          </android.view.ViewGroup>
                          <android.view.ViewGroup bounds="[561,0][1038,650]">
                            <android.widget.ImageView bounds="[561,22][1038,354]" content-desc="Sauce Labs Bike Light" />
                            <android.widget.TextView bounds="[561,376][1038,431]" text="Sauce Labs Bike Light" />
                            <android.widget.TextView bounds="[561,443][1038,480]" text="$9.99" />
                          </android.view.ViewGroup>
                          <android.view.ViewGroup bounds="[42,692][519,1342]">
                            <android.widget.ImageView bounds="[42,714][519,1046]" content-desc="Sauce Labs Bolt T-Shirt" />
                            <android.widget.TextView bounds="[42,1068][519,1123]" text="Sauce Labs Bolt T-Shirt" />
                            <android.widget.TextView bounds="[42,1135][519,1172]" text="$15.99" />
                          </android.view.ViewGroup>
                        </android.view.ViewGroup>
                      </android.view.ViewGroup>
                    </android.widget.ScrollView>
                  </android.view.ViewGroup>
                </android.view.ViewGroup>
              </android.view.ViewGroup>
            </android.widget.FrameLayout>
          </android.widget.FrameLayout>
        </android.widget.LinearLayout>
      </android.widget.FrameLayout>
    </hierarchy>
    """
    
    logger.info("Generating test suggestions using Ollama...")
    suggestions = mcp_ai.suggest_test_actions(page_source)
    
    logger.info("\n--- Test Suggestions ---\n")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    print("\n-------------------------\n")


def demonstrate_command_interpretation(mcp_ai: MCPAIIntegration):
    """
    Demonstrate the command interpretation functionality.
    
    Args:
        mcp_ai: The MCPAIIntegration instance
    """
    # Natural language commands to interpret
    commands = [
        "Click on the Sauce Labs Backpack",
        "Check the price of the Bike Light",
        "Go to the shopping cart",
        "Scroll down to see more products"
    ]
    
    logger.info("Interpreting natural language commands using Ollama...")
    
    for cmd in commands:
        logger.info(f"\nInterpreting: '{cmd}'")
        result = mcp_ai.interpret_command(cmd)
        
        if result.get("status") == "success":
            print(f"Action: {result.get('action')}")
            print(f"Parameters: {json.dumps(result.get('parameters', {}), indent=2)}")
        else:
            print(f"Error: {result.get('message')}")
            if 'raw_response' in result:
                print(f"Raw response: {result.get('raw_response')[:100]}...")
        
        print("-------------------------")


def main():
    """Run the Ollama integration example."""
    args = parse_args()
    
    logger.info("Starting Ollama integration example")
    logger.info(f"Ollama host: {args.ollama_host}")
    logger.info(f"Model: {args.model}")
    
    try:
        mcp_ai = create_mcp_ai_integration(
            ollama_host=args.ollama_host,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
        
        # Demonstrate various functionalities
        demonstrate_screen_description(mcp_ai)
        demonstrate_test_suggestions(mcp_ai)
        demonstrate_command_interpretation(mcp_ai)
        
        logger.info("Ollama integration example completed successfully")
        
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()