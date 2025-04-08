"""
Exceptions module defines custom exceptions for MCP Appium.

This module provides custom exception classes for various error conditions
that may occur when using the MCP Appium framework.
"""

class AppiumMCPException(Exception):
    """Base exception class for all MCP Appium exceptions."""
    pass


class SessionNotCreatedError(AppiumMCPException):
    """Exception raised when a new session cannot be created."""
    pass


class ElementNotFoundError(AppiumMCPException):
    """Exception raised when an element cannot be found."""
    pass


class CommandFailedError(AppiumMCPException):
    """Exception raised when a command execution fails."""
    pass


class InvalidArgumentError(AppiumMCPException):
    """Exception raised when invalid arguments are provided."""
    pass


class ContextSwitchError(AppiumMCPException):
    """Exception raised when context switching fails."""
    pass


class TimeoutError(AppiumMCPException):
    """Exception raised when an action times out."""
    pass


class NoSuchContextError(AppiumMCPException):
    """Exception raised when a requested context does not exist."""
    pass


class NoSuchWindowError(AppiumMCPException):
    """Exception raised when a requested window does not exist."""
    pass


class UnknownCommandError(AppiumMCPException):
    """Exception raised when an unknown command is executed."""
    pass
