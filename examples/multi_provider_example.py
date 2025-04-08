"""
Multi-Provider AI Integration Example for MCP Appium
==================================================

This module demonstrates how to use the Multi-Provider AI integration with MCP Appium.
It shows how to use different AI providers (OpenAI, Gemini, Hugging Face) for
interpreting natural language commands for mobile testing.
"""

import os
import json
import logging
import argparse
from typing import Dict, Any

from mcp_appium.ai_integration import (
    AIProvider, MCPAIIntegration, AIModelConfig,
    AIProviderError, AIConnectionError, AIAuthenticationError
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run MCP Appium multi-provider AI integration example')
    parser.add_argument('--provider', default='openai', 
                        choices=['openai', 'gemini', 'huggingface'],
                        help='AI provider to use (openai, gemini, huggingface)')
    parser.add_argument('--model', help='Model name to use (optional)')
    return parser.parse_args()

def get_sample_context() -> Dict:
    """
    Get a sample context for demonstration.
    
    Returns:
        Dict: A dictionary with sample app context
    """
    # Create a sample page source for a login screen
    page_source = """
    <hierarchy>
      <node class="android.widget.FrameLayout" package="com.example.app" content-desc="">
        <node class="android.widget.LinearLayout">
          <node class="android.widget.FrameLayout" content-desc="Login Screen">
            <node class="android.widget.EditText" resource-id="com.example.app:id/username" text="" hint="Username" />
            <node class="android.widget.EditText" resource-id="com.example.app:id/password" text="" hint="Password" />
            <node class="android.widget.Button" resource-id="com.example.app:id/login_button" text="Login" />
            <node class="android.widget.TextView" resource-id="com.example.app:id/signup_link" text="Sign Up" />
            <node class="android.widget.TextView" resource-id="com.example.app:id/forgot_password" text="Forgot Password?" />
          </node>
        </node>
      </node>
    </hierarchy>
    """
    
    # Create a sample context
    return {
        "page_source": page_source,
        "current_context": "NATIVE_APP",
        "platform_name": "Android",
        "device_info": "Pixel 4 API 30",
        "has_screenshot": True
    }

def run_ai_commands(mcp_ai: MCPAIIntegration, context: Dict):
    """
    Run AI-powered commands.
    
    Args:
        mcp_ai: The MCPAIIntegration instance
        context: App context information
    """
    # 1. Interpret natural language commands
    logger.info("\n=== Interpreting natural language commands ===")
    
    commands = [
        "Log in with username 'testuser' and password 'password123'",
        "Click the signup link",
        "Go back and click forgot password"
    ]
    
    for command in commands:
        logger.info(f"\nCommand: \"{command}\"")
        try:
            result = mcp_ai.interpret_command(command, context)
            logger.info(f"Interpreted as: {json.dumps(result, indent=2)}")
        except Exception as e:
            logger.error(f"Error interpreting command: {e}")
    
    # 2. Get screen description
    logger.info("\n=== Getting screen description ===")
    try:
        description = mcp_ai.describe_screen(context["page_source"])
        logger.info(f"Screen description:\n{description}")
    except Exception as e:
        logger.error(f"Error describing screen: {e}")
    
    # 3. Get test action suggestions
    logger.info("\n=== Getting test action suggestions ===")
    try:
        suggestions = mcp_ai.suggest_test_actions(context["page_source"])
        logger.info(f"Test action suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            logger.info(f"{i}. {suggestion}")
    except Exception as e:
        logger.error(f"Error getting test suggestions: {e}")
    
    # 4. Analyze app structure and generate test script
    logger.info("\n=== Analyzing app structure ===")
    try:
        # Create a sample for another screen (post-login)
        home_screen = """
        <hierarchy>
          <node class="android.widget.FrameLayout" package="com.example.app">
            <node class="android.widget.LinearLayout">
              <node class="android.widget.FrameLayout" content-desc="Home Screen">
                <node class="android.widget.TextView" resource-id="com.example.app:id/welcome_message" text="Welcome, User!" />
                <node class="android.widget.RecyclerView" resource-id="com.example.app:id/items_list">
                  <node class="android.widget.LinearLayout">
                    <node class="android.widget.TextView" text="Item 1" />
                  </node>
                  <node class="android.widget.LinearLayout">
                    <node class="android.widget.TextView" text="Item 2" />
                  </node>
                </node>
                <node class="android.widget.Button" resource-id="com.example.app:id/logout_button" text="Logout" />
              </node>
            </node>
          </node>
        </hierarchy>
        """
        
        app_analysis = mcp_ai.analyze_app_structure([context["page_source"], home_screen])
        logger.info(f"App analysis: {json.dumps(app_analysis, indent=2)}")
        
        logger.info("\n=== Generating test script ===")
        test_goal = "Test the login functionality with valid and invalid credentials"
        test_script = mcp_ai.generate_test_script(app_analysis, test_goal)
        logger.info(f"Generated test script:\n{test_script}")
        
    except Exception as e:
        logger.error(f"Error analyzing app structure or generating test script: {e}")

def check_env_variables(provider: str):
    """
    Check if the required environment variables are set.
    
    Args:
        provider: The AI provider name
        
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    if provider.lower() == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            return False
            
    elif provider.lower() == 'gemini':
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set")
            return False
            
    elif provider.lower() == 'huggingface':
        api_key = os.environ.get('HUGGINGFACE_API_KEY')
        if not api_key:
            logger.error("HUGGINGFACE_API_KEY environment variable not set")
            return False
            
    return True

def main():
    """Run the MCP Appium multi-provider AI integration example."""
    args = parse_args()
    
    if not check_env_variables(args.provider):
        logger.error(f"Missing API key for {args.provider}. Please set the appropriate environment variable.")
        return
    
    try:
        # Create a custom configuration with lower temperature for more deterministic responses
        config = AIModelConfig(
            temperature=0.3,
            max_tokens=1024,
            timeout=30,
            max_retries=2
        )
        
        # Initialize the MCPAIIntegration with the specified provider
        logger.info(f"Initializing AI integration with provider: {args.provider}")
        
        # Create the integration instance
        mcp_ai = MCPAIIntegration(
            provider=args.provider,
            model=args.model,
            config=config
        )
        
        # Get sample context
        context = get_sample_context()
        
        # Run AI commands
        run_ai_commands(mcp_ai, context)
        
        logger.info("Example completed successfully!")
        
    except AIAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        logger.info("Please check your API key and try again.")
    except AIConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.info("Please check your internet connection and try again.")
    except AIProviderError as e:
        logger.error(f"AI provider error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()