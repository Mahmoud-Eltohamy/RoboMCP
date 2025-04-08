"""
AI Integration for MCP Appium
============================

This module provides integration with various AI providers for the MCP Appium implementation.
It supports multiple AI providers including OpenAI, Google's Gemini, and direct API calls to Hugging Face.
"""

import json
import logging
import os
import time
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

# OpenAI
try:
    from openai import OpenAI
    from openai.types.chat import ChatCompletion
    from openai import APIError, RateLimitError, APIConnectionError, AuthenticationError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Google GenerativeAI (Gemini)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Use direct REST API calls for Hugging Face
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

# Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from mcp_appium.errors import (
    AppiumMCPError, AIProviderError, AIConnectionError, 
    AIAuthenticationError, AIQuotaExceededError, 
    AIResponseParsingError, AIModelUnavailableError
)

# Configure logging
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """
    Enumeration of supported AI providers.
    """
    OPENAI = "openai"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


# Default configuration values
DEFAULT_TIMEOUT = 60  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RETRY_BACKOFF_FACTOR = 2  # exponential backoff


class AIModelConfig:
    """
    Configuration class for AI models.
    Provides centralized configuration for timeouts, retries, and other parameters.
    """
    
    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delay: int = RETRY_DELAY,
        retry_backoff_factor: float = RETRY_BACKOFF_FACTOR,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ):
        """
        Initialize AI model configuration.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            retry_backoff_factor: Exponential backoff factor for retry delays
            temperature: Sampling temperature (0.0 to 1.0, lower is more deterministic)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model-specific parameters
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff_factor = retry_backoff_factor
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.additional_params = kwargs


class AIModelInterface(ABC):
    """
    Abstract base class for AI model implementations.
    Each AI provider will implement this interface.
    """
    
    def __init__(self, config: Optional[AIModelConfig] = None):
        """
        Initialize with optional configuration.
        
        Args:
            config: AI model configuration
        """
        self.config = config or AIModelConfig()
    
    @abstractmethod
    def initialize(self):
        """
        Initialize the AI model with necessary credentials.
        """
        pass
    
    @abstractmethod
    def chat_completion(self, system_prompt: str, user_prompt: str, json_response: bool = False) -> str:
        """
        Generate a chat completion.
        
        Args:
            system_prompt: System instructions
            user_prompt: User's message
            json_response: Whether to request a JSON-formatted response
            
        Returns:
            str: The generated response
        """
        pass
    
    def _retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic and exponential backoff.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result of the function
            
        Raises:
            AIProviderError: If all retries fail
        """
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{self.config.max_retries} failed: {str(e)}")
                
                # If it's the last attempt, don't sleep
                if attempt < self.config.max_retries - 1:
                    # Calculate delay with exponential backoff
                    delay = self.config.retry_delay * (self.config.retry_backoff_factor ** attempt)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
        
        # Convert the last error to an appropriate AI error
        if isinstance(last_error, (ConnectionError, Timeout, APIConnectionError)):
            raise AIConnectionError(f"Failed to connect to AI provider after {self.config.max_retries} attempts: {str(last_error)}")
        elif isinstance(last_error, (AuthenticationError)):
            raise AIAuthenticationError(f"Authentication failed with AI provider: {str(last_error)}")
        elif isinstance(last_error, (RateLimitError)):
            raise AIQuotaExceededError(f"AI provider quota exceeded: {str(last_error)}")
        else:
            raise AIProviderError(f"Failed after {self.config.max_retries} attempts: {str(last_error)}")

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text to prevent common issues with AI providers.
        Removes control characters, excessive whitespace, etc.
        
        Args:
            text: Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return ""
        
        # Ensure text is a string
        text = str(text)
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Replace sequences of whitespace with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Trim leading/trailing whitespace
        text = text.strip()
        
        return text


class OpenAIModel(AIModelInterface):
    """
    Implementation of the AIModelInterface for OpenAI.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", config: Optional[AIModelConfig] = None):
        """
        Initialize the OpenAI model.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: Model to use (default: gpt-4o)
            config: AI model configuration
        """
        super().__init__(config)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.client = None
    
    def initialize(self):
        """
        Initialize the OpenAI client.
        
        Raises:
            AIProviderError: If OpenAI package is not available or API key is missing
        """
        if not OPENAI_AVAILABLE:
            raise AIProviderError("OpenAI package is not installed. Install it with 'pip install openai'")
            
        if not self.api_key:
            raise AIAuthenticationError("OpenAI API key not found. Set OPENAI_API_KEY environment variable")
            
        try:
            self.client = OpenAI(api_key=self.api_key, timeout=self.config.timeout)
            logger.info(f"Initialized OpenAI with model {self.model}")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def chat_completion(self, system_prompt: str, user_prompt: str, json_response: bool = False) -> str:
        """
        Generate a chat completion using OpenAI.
        
        Args:
            system_prompt: System instructions
            user_prompt: User's message
            json_response: Whether to request a JSON-formatted response
            
        Returns:
            str: The generated response
            
        Raises:
            AIProviderError: If OpenAI client is not initialized or generation fails
        """
        if not self.client:
            self.initialize()
            
        def _execute_chat_completion() -> str:
            # Ensure all strings are properly encoded as UTF-8
            system_prompt_encoded = self._sanitize_text(system_prompt).encode('utf-8', errors='replace').decode('utf-8')
            user_prompt_encoded = self._sanitize_text(user_prompt).encode('utf-8', errors='replace').decode('utf-8')
            
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt_encoded},
                    {"role": "user", "content": user_prompt_encoded}
                ],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            if json_response:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = self.client.chat.completions.create(**kwargs)
            if not isinstance(response, ChatCompletion):
                raise AIResponseParsingError("Unexpected response type from OpenAI")
                
            if not response.choices or len(response.choices) == 0:
                raise AIResponseParsingError("No choices in OpenAI response")
                
            return response.choices[0].message.content
        
        try:
            return self._retry_with_backoff(_execute_chat_completion)
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            if isinstance(e, AIProviderError):
                raise e
            raise AIProviderError(f"OpenAI generation failed: {str(e)}")


class GeminiModel(AIModelInterface):
    """
    Implementation of the AIModelInterface for Google's Gemini.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro", config: Optional[AIModelConfig] = None):
        """
        Initialize the Gemini model.
        
        Args:
            api_key: Google API key (defaults to environment variable)
            model: Model to use (default: gemini-pro)
            config: AI model configuration
        """
        super().__init__(config)
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model = model
        self.initialized = False
    
    def initialize(self):
        """
        Initialize the Gemini client.
        
        Raises:
            AIProviderError: If Gemini package is not available or API key is missing
        """
        if not GEMINI_AVAILABLE:
            raise AIProviderError("Google GenerativeAI package is not installed. Install it with 'pip install google-generativeai'")
            
        if not self.api_key:
            raise AIAuthenticationError("Google API key not found. Set GOOGLE_API_KEY environment variable")
            
        try:
            genai.configure(api_key=self.api_key)
            self.initialized = True
            logger.info(f"Initialized Gemini with model {self.model}")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize Gemini: {str(e)}")
    
    def chat_completion(self, system_prompt: str, user_prompt: str, json_response: bool = False) -> str:
        """
        Generate a chat completion using Gemini.
        
        Args:
            system_prompt: System instructions
            user_prompt: User's message
            json_response: Whether to request a JSON-formatted response
            
        Returns:
            str: The generated response
            
        Raises:
            AIProviderError: If Gemini is not initialized or generation fails
        """
        if not self.initialized:
            self.initialize()
            
        def _execute_chat_completion() -> str:
            # Ensure all strings are properly encoded as UTF-8
            system_prompt_encoded = self._sanitize_text(system_prompt).encode('utf-8', errors='replace').decode('utf-8')
            user_prompt_encoded = self._sanitize_text(user_prompt).encode('utf-8', errors='replace').decode('utf-8')
            
            # Combine system prompt and user prompt for Gemini (different structure than OpenAI)
            prompt = f"{system_prompt_encoded}\n\n{user_prompt_encoded}"
            
            if json_response:
                prompt += "\n\nPlease provide your response as a valid JSON object."
                
            model = genai.GenerativeModel(
                self.model,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                }
            )
            
            response = model.generate_content(prompt)
            
            if not hasattr(response, 'text'):
                raise AIResponseParsingError("Unexpected response format from Gemini")
                
            return response.text
            
        try:
            return self._retry_with_backoff(_execute_chat_completion)
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {str(e)}")
            if isinstance(e, AIProviderError):
                raise e
            raise AIProviderError(f"Gemini generation failed: {str(e)}")


class HuggingFaceModel(AIModelInterface):
    """
    Implementation of the AIModelInterface for Hugging Face models via API.
    Uses direct API calls instead of a Python client.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "meta-llama/Llama-2-70b-chat-hf", config: Optional[AIModelConfig] = None):
        """
        Initialize the Hugging Face model.
        
        Args:
            api_key: Hugging Face API token (defaults to environment variable)
            model: Model to use (default: meta-llama/Llama-2-70b-chat-hf)
            config: AI model configuration
        """
        super().__init__(config)
        self.api_key = api_key or os.environ.get("HUGGINGFACE_API_KEY")
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    def initialize(self):
        """
        Check that Hugging Face API key is available.
        
        Raises:
            AIProviderError: If API key is missing
        """
        if not self.api_key:
            raise AIAuthenticationError("Hugging Face API key not found. Set HUGGINGFACE_API_KEY environment variable")
            
        logger.info(f"Initialized Hugging Face with model {self.model}")
    
    def chat_completion(self, system_prompt: str, user_prompt: str, json_response: bool = False) -> str:
        """
        Generate a chat completion using Hugging Face API.
        
        Args:
            system_prompt: System instructions
            user_prompt: User's message
            json_response: Whether to request a JSON-formatted response
            
        Returns:
            str: The generated response
            
        Raises:
            AIProviderError: If the API call fails
        """
        self.initialize()
            
        def _execute_chat_completion() -> str:
            # Ensure all strings are properly encoded as UTF-8
            system_prompt_encoded = self._sanitize_text(system_prompt).encode('utf-8', errors='replace').decode('utf-8')
            user_prompt_encoded = self._sanitize_text(user_prompt).encode('utf-8', errors='replace').decode('utf-8')
            
            # Format prompt based on common Hugging Face text generation format
            prompt = f"<system>\n{system_prompt_encoded}\n</system>\n\n<user>\n{user_prompt_encoded}\n</user>\n\n<assistant>"
            
            if json_response:
                prompt += "\nI'll provide my response as a valid JSON object.\n"
                
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 401:
                raise AIAuthenticationError(f"Authentication failed with Hugging Face API: {response.text}")
            elif response.status_code == 429:
                raise AIQuotaExceededError(f"Hugging Face API rate limit exceeded: {response.text}")
            elif response.status_code != 200:
                raise AIProviderError(f"Hugging Face API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            # Extract the generated text from the response
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                    
            raise AIResponseParsingError(f"Could not parse response from Hugging Face: {result}")
            
        try:
            return self._retry_with_backoff(_execute_chat_completion)
        except Exception as e:
            logger.error(f"Error generating response with Hugging Face: {str(e)}")
            if isinstance(e, AIProviderError):
                raise e
            raise AIProviderError(f"Hugging Face API call failed: {str(e)}")


class OllamaModel(AIModelInterface):
    """
    Implementation of the AIModelInterface for Ollama.
    Supports local LLM deployment using Ollama.
    """
    
    def __init__(self, model: str = "mistral:7b-instruct", ollama_host: Optional[str] = None, config: Optional[AIModelConfig] = None):
        """
        Initialize the Ollama model.
        
        Args:
            model: Model to use (default: mistral:7b-instruct)
            ollama_host: Ollama host URL (defaults to environment variable OLLAMA_BASE_URL)
            config: AI model configuration
        """
        super().__init__(config)
        self.model = model
        self.ollama_host = ollama_host or os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
    
    def initialize(self):
        """
        Initialize Ollama client and check that the model is available.
        
        Raises:
            AIProviderError: If Ollama package is not available or model is not accessible
        """
        if not OLLAMA_AVAILABLE:
            raise AIProviderError("Ollama package is not installed. Install it with 'pip install ollama'")
            
        try:
            # Set the host
            ollama.host = self.ollama_host
            
            # List available models to verify connection
            models = ollama.list()
            logger.info(f"Connected to Ollama at {self.ollama_host}")
            
            # Check if the model is already available
            model_available = any(m.get('name') == self.model for m in models.get('models', []))
            
            if not model_available:
                logger.info(f"Model {self.model} not found locally, attempting to pull...")
                try:
                    # This will pull the model if it's not available
                    ollama.pull(self.model)
                    logger.info(f"Successfully pulled model {self.model}")
                except Exception as e:
                    raise AIModelUnavailableError(f"Failed to pull model {self.model}: {str(e)}")
            
            logger.info(f"Initialized Ollama with model {self.model}")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize Ollama client: {str(e)}")
    
    def chat_completion(self, system_prompt: str, user_prompt: str, json_response: bool = False) -> str:
        """
        Generate a chat completion using Ollama.
        
        Args:
            system_prompt: System instructions
            user_prompt: User's message
            json_response: Whether to request a JSON-formatted response
            
        Returns:
            str: The generated response
            
        Raises:
            AIProviderError: If Ollama model is not accessible or generation fails
        """
        def _execute_chat_completion() -> str:
            # Ensure all strings are properly encoded as UTF-8
            system_prompt_encoded = self._sanitize_text(system_prompt).encode('utf-8', errors='replace').decode('utf-8')
            user_prompt_encoded = self._sanitize_text(user_prompt).encode('utf-8', errors='replace').decode('utf-8')
            
            # Format message for json response if needed
            messages = [
                {"role": "system", "content": system_prompt_encoded}
            ]
            
            if json_response:
                user_prompt_encoded += "\n\nPlease format your response as a valid JSON object."
                
            messages.append({"role": "user", "content": user_prompt_encoded})
            
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens
                    }
                )
                
                if not response or "message" not in response:
                    raise AIResponseParsingError("No valid message in Ollama response")
                    
                return response["message"]["content"]
            except Exception as e:
                raise AIProviderError(f"Ollama generation failed: {str(e)}")
        
        try:
            return self._retry_with_backoff(_execute_chat_completion)
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {str(e)}")
            if isinstance(e, AIProviderError):
                raise e
            raise AIProviderError(f"Ollama generation failed: {str(e)}")


class AIModelFactory:
    """
    Factory class to create AI model instances based on provider.
    """
    
    @staticmethod
    def create_model(
        provider: AIProvider, 
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[AIModelConfig] = None
    ) -> AIModelInterface:
        """
        Create and return an AI model instance.
        
        Args:
            provider: AI provider type
            api_key: Optional API key (defaults to environment variable)
            model: Optional model name (defaults to provider's default)
            config: Optional AI model configuration
            
        Returns:
            AIModelInterface: An instance of the requested AI model
            
        Raises:
            AIProviderError: If the provider is not supported
        """
        if provider == AIProvider.OPENAI:
            return OpenAIModel(api_key=api_key, model=model or "gpt-4o", config=config)
            
        elif provider == AIProvider.GEMINI:
            return GeminiModel(api_key=api_key, model=model or "gemini-pro", config=config)
            
        elif provider == AIProvider.HUGGINGFACE:
            return HuggingFaceModel(api_key=api_key, model=model or "meta-llama/Llama-2-70b-chat-hf", config=config)
            
        elif provider == AIProvider.OLLAMA:
            return OllamaModel(model=model or "mistral:7b-instruct", ollama_host=api_key, config=config)
            
        else:
            raise AIProviderError(f"Unsupported AI provider: {provider}")


class MCPAIIntegration:
    """
    Main class for AI integration with MCP Appium.
    Provides a unified interface for different AI providers.
    """
    
    def __init__(
        self,
        provider: Union[str, AIProvider] = AIProvider.OPENAI, 
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[AIModelConfig] = None
    ):
        """
        Initialize the AI integration.
        
        Args:
            provider: AI provider to use (default: OpenAI)
            api_key: Optional API key (defaults to environment variable)
            model: Optional model name (defaults to provider's default)
            config: Optional AI model configuration
        """
        # Convert string to enum if needed
        if isinstance(provider, str):
            try:
                provider = AIProvider(provider.lower())
            except ValueError:
                raise AIProviderError(f"Unknown AI provider: {provider}. Supported providers: {[p.value for p in AIProvider]}")
                
        self.provider = provider
        self.config = config or AIModelConfig()
        self.model = AIModelFactory.create_model(provider, api_key, model, self.config)
        
        # Initialize the model
        try:
            self.model.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {str(e)}")
            if isinstance(e, AIProviderError):
                raise e
            raise AIProviderError(f"AI model initialization failed: {str(e)}")
        
    def interpret_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Interpret a natural language command into a structured Appium command.
        
        Args:
            command: Natural language command
            context: Optional context information
            
        Returns:
            Dict: Structured command with action and parameters
        """
        if not command:
            return {"status": "error", "message": "Command cannot be empty"}
            
        # Default context if none provided
        if context is None:
            context = {}
            
        try:
            # Prepare the prompt
            system_prompt = """
            You are an expert in mobile app testing with Appium.
            Your job is to interpret natural language commands and convert them into structured Appium commands.
            
            Return a JSON object with the following structure:
            {
              "action": "<appium_action>",
              "parameters": {
                "<param_name>": "<param_value>",
                ...
              }
            }
            
            Available actions and their parameters:
            1. find_element: {"by": "<locator_strategy>", "value": "<locator_value>"}
            2. find_elements: {"by": "<locator_strategy>", "value": "<locator_value>"}
            3. click_element: {"element_id": "<element_id>"}
            4. send_keys: {"element_id": "<element_id>", "text": "<text_to_send>"}
            5. get_text: {"element_id": "<element_id>"}
            6. back: {}
            7. screenshot: {}
            8. get_contexts: {}
            9. switch_to_context: {"context_name": "<context_name>"}
            10. execute_script: {"script": "<javascript_code>", "args": [<arg1>, <arg2>, ...]}
            
            Locator strategies include: "id", "accessibility id", "class name", "xpath", "css selector" (for web contexts), 
            "ios predicate string" (for iOS), "android uiautomator" (for Android).
            
            Before responding, analyze the current app state from the provided context (if available).
            """
            
            # Add context information to the user prompt
            context_info = ""
            if context.get("page_source"):
                context_info += "\nCurrent page source:\n"
                context_info += context["page_source"]
            
            if context.get("current_context"):
                context_info += f"\nCurrent context: {context['current_context']}\n"
            
            if context.get("has_screenshot"):
                context_info += "\nA screenshot is available for reference.\n"
            
            if context.get("platform_name"):
                context_info += f"\nPlatform: {context['platform_name']}\n"
                
            if context.get("device_info"):
                context_info += f"\nDevice info: {context['device_info']}\n"
            
            user_prompt = f"App state context:{context_info}\n\nCommand to interpret: {command}"
            
            # Get the completion from the AI model
            result_text = self.model.chat_completion(system_prompt, user_prompt, json_response=True)
            
            # Parse the response
            try:
                result = json.loads(result_text)
                
                # Basic validation
                if "action" not in result:
                    return {"status": "error", "message": "Missing 'action' in response", "raw_response": result_text}
                
                if "parameters" not in result:
                    result["parameters"] = {}
                
                return {
                    "status": "success",
                    "action": result["action"],
                    "parameters": result["parameters"]
                }
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {result_text}")
                return {"status": "error", "message": "Could not parse JSON response", "raw_response": result_text}
                
        except Exception as e:
            logger.error(f"Error interpreting command: {str(e)}")
            return {"status": "error", "message": f"Error interpreting command: {str(e)}"}
        
    def describe_screen(self, page_source: str) -> str:
        """
        Generate a description of the current screen.
        
        Args:
            page_source: XML/HTML representation of the screen
            
        Returns:
            str: Description of the screen
        """
        if not page_source:
            return "No page source provided"
            
        try:
            system_prompt = """
            You are an expert in mobile app testing and user interfaces.
            Your job is to analyze the XML/HTML representation of a mobile app screen and provide a detailed description.
            
            Focus on:
            1. The overall purpose of this screen (e.g., login, settings, profile)
            2. Key UI elements present (text fields, buttons, labels)
            3. The layout and structure of the screen
            4. Any notable accessibility features or issues
            
            Provide a comprehensive but concise description that would help someone understand what is displayed without seeing it.
            """
            
            user_prompt = f"Please describe this mobile app screen based on its source:\n\n{page_source}"
            
            # Get the completion from the AI model
            result = self.model.chat_completion(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Error describing screen: {str(e)}")
            return f"Error describing screen: {str(e)}"
        
    def suggest_test_actions(self, page_source: str) -> List[str]:
        """
        Generate suggested test actions for the current screen.
        
        Args:
            page_source: XML/HTML representation of the screen
            
        Returns:
            List[str]: List of suggested test actions
        """
        if not page_source:
            return ["No page source provided for generating suggestions"]
            
        try:
            system_prompt = """
            You are an expert in mobile app testing with Appium.
            Your job is to analyze the XML/HTML representation of a mobile app screen and suggest test actions.
            
            Provide a list of 5-10 natural language test commands that would be useful for testing this screen.
            Format your response as a JSON array of strings.
            
            Examples of test commands:
            - "Click the login button"
            - "Enter 'test@example.com' in the email field"
            - "Verify the error message is displayed"
            - "Check if the username label shows the correct value"
            - "Swipe down to refresh the feed"
            
            Focus on:
            1. Testing important functionality visible on this screen
            2. Validating user flows
            3. Checking error states and edge cases
            4. Verifying correct display of dynamic content
            """
            
            user_prompt = f"Please suggest test actions for this mobile app screen:\n\n{page_source}"
            
            # Get the completion from the AI model
            result_text = self.model.chat_completion(system_prompt, user_prompt, json_response=True)
            
            # Parse the response
            try:
                result = json.loads(result_text)
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict) and "suggestions" in result:
                    return result["suggestions"]
                else:
                    return [str(result)]
                
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract a list from the text
                return [line.strip() for line in result_text.split("\n") if line.strip()]
                
        except Exception as e:
            logger.error(f"Error suggesting test actions: {str(e)}")
            return [f"Error suggesting test actions: {str(e)}"]
            
    def analyze_app_structure(self, page_sources: List[str]) -> Dict[str, Any]:
        """
        Analyze the structure of an app based on multiple screen page sources.
        
        Args:
            page_sources: List of XML/HTML representations of different screens
            
        Returns:
            Dict: Analysis of app structure including screens, elements, and flows
        """
        if not page_sources:
            return {"error": "No page sources provided for analysis"}
            
        try:
            system_prompt = """
            You are an expert in mobile app architecture and testing.
            Your job is to analyze multiple screens of a mobile app and provide insights about its structure.
            
            Return a JSON object with the following structure:
            {
              "app_type": "string (e.g., 'e-commerce', 'social media', 'utility')",
              "screens": [
                {
                  "name": "descriptive name of the screen",
                  "purpose": "primary purpose of this screen",
                  "key_elements": ["list", "of", "important", "UI", "elements"]
                }
              ],
              "flows": [
                {
                  "name": "name of the user flow",
                  "description": "description of the flow",
                  "screens": ["screen names", "involved", "in", "this", "flow"]
                }
              ],
              "suggestions": [
                "list of suggestions for testing or improving the app"
              ]
            }
            """
            
            user_prompt = "Please analyze these app screens and provide insights about the app structure:\n\n"
            for i, page_source in enumerate(page_sources[:5]):  # Limit to first 5 to avoid token limits
                user_prompt += f"SCREEN {i+1}:\n{page_source[:2000]}...\n\n"  # Truncate each page source
            
            # Get the completion from the AI model
            result_text = self.model.chat_completion(system_prompt, user_prompt, json_response=True)
            
            # Parse the response
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {result_text}")
                return {"error": "Could not parse JSON response", "raw_response": result_text[:500]}
                
        except Exception as e:
            logger.error(f"Error analyzing app structure: {str(e)}")
            return {"error": f"Error analyzing app structure: {str(e)}"}
            
    def generate_test_script(self, app_info: Dict[str, Any], test_goal: str) -> str:
        """
        Generate a test script based on app information and a testing goal.
        
        Args:
            app_info: Information about the app (structure, elements, etc.)
            test_goal: Description of what to test
            
        Returns:
            str: Generated test script as Python code
        """
        # For backward compatibility, default to Python
        return self.generate_test_script_with_interface(app_info, test_goal, "python")
        
    def generate_test_script_with_interface(self, app_info: Dict[str, Any], test_goal: str, language: str = "python") -> str:
        """
        Generate a test script in the specified programming language based on app information and a testing goal.
        
        Args:
            app_info: Information about the app (structure, elements, etc.)
            test_goal: Description of what to test
            language: Programming language/interface to use (python, java, javascript, csharp, ruby)
            
        Returns:
            str: Generated test script in the specified language
        """
        if not app_info:
            return f"# No app information provided\n# Cannot generate test script without app information"
            
        # Normalize language input
        language = language.lower().strip()
        
        # Map of supported languages to their file extensions and code block markers
        language_config = {
            "python": {"ext": "py", "marker": "python", "comment": "#"},
            "java": {"ext": "java", "marker": "java", "comment": "//"},
            "javascript": {"ext": "js", "marker": "javascript", "comment": "//"},
            "js": {"ext": "js", "marker": "javascript", "comment": "//"},
            "nodejs": {"ext": "js", "marker": "javascript", "comment": "//"},
            "csharp": {"ext": "cs", "marker": "csharp", "comment": "//"},
            "c#": {"ext": "cs", "marker": "csharp", "comment": "//"},
            "dotnet": {"ext": "cs", "marker": "csharp", "comment": "//"},
            "ruby": {"ext": "rb", "marker": "ruby", "comment": "#"},
            "robot": {"ext": "robot", "marker": "robotframework", "comment": "#"},
            "robotframework": {"ext": "robot", "marker": "robotframework", "comment": "#"},
        }
        
        # Check if language is supported
        if language not in language_config:
            supported_langs = ", ".join(sorted(set(language_config.keys())))
            return f"# Unsupported language: {language}\n# Supported languages: {supported_langs}"
        
        config = language_config[language]
        
        try:
            # Create language-specific system prompt
            system_prompts = {
                "python": """
                You are an expert in mobile app test automation with Appium and Python.
                Your job is to generate a Python test script for Appium based on app information and a testing goal.
                
                Write a complete, working Python script that:
                1. Uses the Appium Python client (from appium import webdriver)
                2. Includes proper setup and teardown
                3. Implements the test goal provided
                4. Includes comments explaining key sections
                5. Handles errors appropriately with try/except blocks
                6. Uses best practices for test automation in Python
                
                The script should be ready to run with minimal modification.
                """,
                
                "java": """
                You are an expert in mobile app test automation with Appium and Java.
                Your job is to generate a Java test script for Appium based on app information and a testing goal.
                
                Write a complete, working Java class that:
                1. Uses the Java Client for Appium (io.appium:java-client)
                2. Uses JUnit or TestNG for test structure
                3. Includes proper setup (@Before) and teardown (@After) methods
                4. Implements the test goal provided
                5. Includes comments explaining key sections
                6. Handles errors appropriately with try/catch blocks
                7. Uses best practices for test automation in Java
                
                The script should be ready to run with minimal modification.
                """,
                
                "javascript": """
                You are an expert in mobile app test automation with Appium and JavaScript.
                Your job is to generate a JavaScript test script for Appium based on app information and a testing goal.
                
                Write a complete, working JavaScript script that:
                1. Uses WebdriverIO with Appium
                2. Uses Mocha, Jasmine, or Jest for test structure
                3. Includes proper setup (before) and teardown (after) hooks
                4. Implements the test goal provided
                5. Includes comments explaining key sections
                6. Handles errors appropriately with try/catch blocks
                7. Uses best practices for test automation in JavaScript
                
                The script should be ready to run with minimal modification.
                """,
                
                "csharp": """
                You are an expert in mobile app test automation with Appium and C#.
                Your job is to generate a C# test script for Appium based on app information and a testing goal.
                
                Write a complete, working C# class that:
                1. Uses Appium.WebDriver NuGet package
                2. Uses NUnit or MSTest for test structure
                3. Includes proper setup and teardown methods
                4. Implements the test goal provided
                5. Includes comments explaining key sections
                6. Handles errors appropriately with try/catch blocks
                7. Uses best practices for test automation in C#
                
                The script should be ready to run with minimal modification.
                """,
                
                "ruby": """
                You are an expert in mobile app test automation with Appium and Ruby.
                Your job is to generate a Ruby test script for Appium based on app information and a testing goal.
                
                Write a complete, working Ruby script that:
                1. Uses the appium_lib gem
                2. Uses RSpec or Test::Unit for test structure
                3. Includes proper setup and teardown methods
                4. Implements the test goal provided
                5. Includes comments explaining key sections
                6. Handles errors appropriately with begin/rescue blocks
                7. Uses best practices for test automation in Ruby
                
                The script should be ready to run with minimal modification.
                """,
                
                "robot": """
                You are an expert in mobile app test automation with Appium and Robot Framework.
                Your job is to generate a Robot Framework test script for Appium based on app information and a testing goal.
                
                Write a complete, working Robot Framework script that:
                1. Uses the AppiumLibrary for Robot Framework
                2. Includes proper Test Setup and Test Teardown
                3. Uses appropriate Robot Framework keywords and syntax
                4. Implements the test goal provided
                5. Includes comments explaining key sections
                6. Handles errors appropriately
                7. Uses best practices for test automation in Robot Framework
                8. Organizes the script with proper sections (Settings, Variables, Keywords, Test Cases)
                
                The script should be ready to run with minimal modification.
                """
            }
            
            # Use appropriate system prompt based on language
            system_prompt = system_prompts.get(
                language,
                system_prompts["python"]  # Default to Python if specific language not in prompts
            )
            
            user_prompt = f"""
            Please generate a test script in {language.upper()} for the following app and test goal:
            
            TEST GOAL:
            {test_goal}
            
            APP INFORMATION:
            {json.dumps(app_info, indent=2)}
            """
            
            # Get the completion from the AI model
            result = self.model.chat_completion(system_prompt, user_prompt)
            
            # Extract code block if present
            code_pattern = r"```(?:" + config["marker"] + r"|" + config["ext"] + r")(.*?)```"
            code_matches = re.findall(code_pattern, result, re.DOTALL)
            
            if code_matches:
                return code_matches[0].strip()
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error generating test script: {str(e)}")
            return f"{config['comment']} Error generating test script: {str(e)}"