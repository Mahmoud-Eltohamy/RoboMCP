"""
AI Configuration and Error Handling Example for MCP Appium
========================================================

This module demonstrates how to use the advanced configuration and error
handling features of the AI integration in MCP Appium.

It shows how to:
1. Configure AI model parameters (temperature, max tokens, etc.)
2. Set up retry and timeout behavior
3. Handle specific AI provider errors gracefully
4. Use the new analyze_app_structure and generate_test_script methods
"""

import os
import logging
import json
import time
from typing import Dict, Any

from mcp_appium.ai_integration import (
    AIProvider, MCPAIIntegration, AIModelConfig,
    AIProviderError, AIConnectionError, AIAuthenticationError, AIQuotaExceededError
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description='Run MCP Appium AI configuration example')
    parser.add_argument('--provider', default='openai', help='AI provider to use (openai, gemini, huggingface)')
    parser.add_argument('--model', help='Model name to use (optional)')
    return parser.parse_args()

def create_mcp_ai_integration(provider_name: str, model_name: str = None) -> MCPAIIntegration:
    """
    Create and initialize an MCPAIIntegration instance with custom configuration.
    
    Args:
        provider_name: Name of the AI provider
        model_name: Optional model name
        
    Returns:
        MCPAIIntegration: The configured AI integration instance
    """
    # Create a custom configuration
    config = AIModelConfig(
        timeout=30,                 # 30 second timeout for API calls
        max_retries=3,              # Retry API calls up to 3 times
        retry_delay=1,              # Start with a 1 second delay between retries
        retry_backoff_factor=2.0,   # Double the delay with each retry
        temperature=0.5,            # Lower temperature for more deterministic responses
        max_tokens=1024,            # Maximum tokens to generate
        # Additional provider-specific parameters could be added here
    )
    
    # Create the MCPAIIntegration instance with the custom configuration
    try:
        # Check for API keys based on the provider
        api_key = None
        if provider_name.lower() == 'openai':
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set")
                raise ValueError("OpenAI API key is required")
                
        elif provider_name.lower() == 'gemini':
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key:
                logger.error("GOOGLE_API_KEY environment variable not set")
                raise ValueError("Google API key is required")
                
        elif provider_name.lower() == 'huggingface':
            api_key = os.environ.get('HUGGINGFACE_API_KEY')
            if not api_key:
                logger.error("HUGGINGFACE_API_KEY environment variable not set")
                raise ValueError("Hugging Face API key is required")
        
        # Initialize the MCPAIIntegration
        mcp_ai = MCPAIIntegration(
            provider=provider_name,
            api_key=api_key,
            model=model_name,
            config=config
        )
        
        logger.info(f"Successfully initialized {provider_name} AI integration")
        return mcp_ai
        
    except AIAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise
    except AIConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise
    except AIProviderError as e:
        logger.error(f"AI provider error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def demo_error_handling(mcp_ai: MCPAIIntegration):
    """
    Demonstrate error handling with various scenarios.
    
    Args:
        mcp_ai: The MCPAIIntegration instance
    """
    logger.info("Demonstrating error handling...")
    
    # Example 1: Handle network errors
    try:
        # Simulate a network error by setting an invalid API key temporarily
        original_api_key = mcp_ai.model.api_key
        mcp_ai.model.api_key = "invalid_key_to_trigger_auth_error"
        
        # This should fail with an authentication error
        result = mcp_ai.describe_screen("<screen>Test</screen>")
        logger.info(f"Result: {result}")
        
    except AIAuthenticationError as e:
        logger.info(f"Successfully caught authentication error: {e}")
    except AIProviderError as e:
        logger.info(f"Caught AI provider error: {e}")
    finally:
        # Restore the original API key
        mcp_ai.model.api_key = original_api_key
    
    # Example 2: Handle parsing errors
    try:
        # Create malformed page source to potentially trigger parsing issues
        malformed_page_source = "<xml><<unclosed tag</unclosed>><<"
        
        # The AI model should still handle this, but we're demonstrating error handling
        suggestions = mcp_ai.suggest_test_actions(malformed_page_source)
        logger.info(f"Got {len(suggestions)} suggestions for malformed page source")
        
    except AIProviderError as e:
        logger.info(f"Caught AI provider error during parsing: {e}")
    except Exception as e:
        logger.info(f"Caught unexpected error: {e}")

def demo_new_methods(mcp_ai: MCPAIIntegration):
    """
    Demonstrate the new methods in the enhanced MCPAIIntegration.
    
    Args:
        mcp_ai: The MCPAIIntegration instance
    """
    logger.info("Demonstrating new methods...")
    
    # Example page sources (simulated)
    login_screen = """
    <screen name="login_screen">
        <input type="text" id="username" hint="Email or username" />
        <input type="password" id="password" hint="Password" />
        <button id="login_button" text="Log In" />
        <text id="signup_link" text="Create account" />
        <text id="forgot_password" text="Forgot password?" />
    </screen>
    """
    
    home_screen = """
    <screen name="home_screen">
        <header>
            <text id="welcome_message" text="Welcome, User!" />
            <button id="notifications" text="Notifications (3)" />
        </header>
        <scrollview>
            <list id="feed">
                <item>
                    <text id="post_title" text="First Post" />
                    <text id="post_content" text="This is the content of the first post" />
                </item>
                <item>
                    <text id="post_title" text="Second Post" />
                    <text id="post_content" text="This is the content of the second post" />
                </item>
            </list>
        </scrollview>
        <navbar>
            <button id="home" text="Home" />
            <button id="search" text="Search" />
            <button id="profile" text="Profile" />
        </navbar>
    </screen>
    """
    
    # 1. App structure analysis
    logger.info("Analyzing app structure...")
    app_analysis = mcp_ai.analyze_app_structure([login_screen, home_screen])
    logger.info(f"App analysis: {json.dumps(app_analysis, indent=2)}")
    
    # 2. Generate test script
    logger.info("Generating test script...")
    test_goal = "Test the login functionality with valid and invalid credentials"
    test_script = mcp_ai.generate_test_script(app_analysis, test_goal)
    logger.info(f"Generated test script:\n{test_script}")

def main():
    """Run the MCP Appium AI configuration example."""
    args = parse_args()
    
    try:
        # Create and initialize the MCPAIIntegration
        mcp_ai = create_mcp_ai_integration(args.provider, args.model)
        
        # Demonstrate error handling
        demo_error_handling(mcp_ai)
        
        # Demonstrate new methods
        demo_new_methods(mcp_ai)
        
        logger.info("Example completed successfully!")
        
    except AIAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        logger.info("Please check your API key and try again.")
    except AIConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.info("Please check your internet connection and try again.")
    except AIQuotaExceededError as e:
        logger.error(f"Quota exceeded: {e}")
        logger.info("Your API quota has been exceeded. Please try again later or upgrade your plan.")
    except AIProviderError as e:
        logger.error(f"AI provider error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()