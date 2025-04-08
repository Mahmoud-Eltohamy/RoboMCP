"""
Error classes for MCP Appium
===========================

This module defines the error classes used throughout the MCP Appium implementation.
"""

class AppiumMCPError(Exception):
    """Base exception class for MCP Appium errors."""
    pass


class ConnectionError(AppiumMCPError):
    """Exception raised for connection-related errors."""
    pass


class TimeoutError(AppiumMCPError):
    """Exception raised when an operation times out."""
    pass


class InvalidArgumentError(AppiumMCPError):
    """Exception raised when an invalid argument is provided."""
    pass


class SessionNotCreatedError(AppiumMCPError):
    """Exception raised when a session cannot be created."""
    pass


class AIProviderError(AppiumMCPError):
    """Exception raised for errors related to AI provider operations."""
    pass


class AIConnectionError(AIProviderError):
    """Exception raised for AI provider connection errors."""
    pass


class AIAuthenticationError(AIProviderError):
    """Exception raised for AI provider authentication errors."""
    pass


class AIQuotaExceededError(AIProviderError):
    """Exception raised when AI provider quota is exceeded."""
    pass


class AIResponseParsingError(AIProviderError):
    """Exception raised when unable to parse the AI provider response."""
    pass


class AIModelUnavailableError(AIProviderError):
    """Exception raised when the requested AI model is unavailable."""
    pass


class SessionError(AppiumMCPError):
    """Exception raised for errors related to Appium session operations."""
    pass


class ElementError(AppiumMCPError):
    """Exception raised for errors related to element operations."""
    pass


class ElementNotFoundError(ElementError):
    """Exception raised when an element cannot be found."""
    pass


class ProtocolError(AppiumMCPError):
    """Exception raised for errors related to protocol operations."""
    pass


class ConfigurationError(AppiumMCPError):
    """Exception raised for errors related to configuration."""
    pass