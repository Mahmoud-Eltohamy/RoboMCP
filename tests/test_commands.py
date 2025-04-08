"""
Tests for the commands module
============================

This module contains tests for the AppiumCommands class.
"""

import pytest

from mcp_appium.commands import AppiumCommands


@pytest.fixture
def commands():
    """Create a commands object for testing."""
    return AppiumCommands()


def test_get_command_info_exists(commands):
    """Test getting info for an existing command."""
    command_info = commands.get_command_info("findElement")
    
    assert command_info is not None
    assert command_info["method"] == "POST"
    assert "/session/:session_id/element" in command_info["url"]
    assert "using" in command_info["parameters"]
    assert "value" in command_info["parameters"]


def test_get_command_info_not_exists(commands):
    """Test getting info for a non-existent command."""
    command_info = commands.get_command_info("nonExistentCommand")
    assert command_info is None


def test_get_all_commands(commands):
    """Test getting all commands."""
    all_commands = commands.get_all_commands()
    
    assert isinstance(all_commands, dict)
    assert len(all_commands) > 0
    
    # Check for some essential commands
    assert "createSession" in all_commands
    assert "findElement" in all_commands
    assert "click" in all_commands
    assert "sendKeys" in all_commands
    assert "deleteSession" in all_commands


def test_command_structure(commands):
    """Test the structure of command objects."""
    all_commands = commands.get_all_commands()
    
    for command_name, command_info in all_commands.items():
        assert "method" in command_info
        assert "url" in command_info
        assert "parameters" in command_info
        
        assert command_info["method"] in ["GET", "POST", "DELETE"]
        assert isinstance(command_info["url"], str)
        assert isinstance(command_info["parameters"], list)


def test_session_commands_exist(commands):
    """Test that session management commands exist."""
    session_commands = [
        "createSession",
        "getSession",
        "getSessions",
        "deleteSession",
        "getStatus"
    ]
    
    for command in session_commands:
        assert commands.get_command_info(command) is not None


def test_element_commands_exist(commands):
    """Test that element commands exist."""
    element_commands = [
        "findElement",
        "findElements",
        "click",
        "clear",
        "sendKeys",
        "getText",
        "getAttribute",
        "isDisplayed",
        "isEnabled",
        "isSelected"
    ]
    
    for command in element_commands:
        assert commands.get_command_info(command) is not None


def test_navigation_commands_exist(commands):
    """Test that navigation commands exist."""
    navigation_commands = [
        "back"
    ]
    
    for command in navigation_commands:
        assert commands.get_command_info(command) is not None


def test_mobile_specific_commands_exist(commands):
    """Test that mobile-specific commands exist."""
    mobile_commands = [
        "getOrientation",
        "setOrientation",
        "getGeolocation",
        "setGeolocation",
        "shake",
        "lock",
        "unlock"
    ]
    
    for command in mobile_commands:
        assert commands.get_command_info(command) is not None


def test_app_management_commands_exist(commands):
    """Test that app management commands exist."""
    app_commands = [
        "launchApp",
        "closeApp",
        "resetApp",
        "installApp",
        "removeApp",
        "isAppInstalled"
    ]
    
    for command in app_commands:
        assert commands.get_command_info(command) is not None
