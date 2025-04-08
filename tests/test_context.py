"""
Tests for the AppiumContext class.

This module contains unit tests for the AppiumContext class to ensure proper
management of Appium sessions and command execution.
"""

import pytest
from unittest.mock import patch, MagicMock, call

from mcp_appium.client import AppiumClient
from mcp_appium.context import AppiumContext
from mcp_appium.exceptions import SessionNotCreatedError, ElementNotFoundError, CommandFailedError


@pytest.fixture
def mock_client():
    """Create a mocked client for testing."""
    return MagicMock(spec=AppiumClient)


@pytest.fixture
def context(mock_client):
    """Create a context with a mocked client for testing."""
    capabilities = {
        "platformName": "Android",
        "appium:deviceName": "Android Emulator",
        "appium:app": "/path/to/app.apk"
    }
    return AppiumContext(mock_client, capabilities)


def test_start_session_success(mock_client, context):
    """Test successful session start."""
    mock_client.create_session.return_value = {"sessionId": "test-session-123"}
    
    context.start_session()
    
    assert context.session_id == "test-session-123"
    mock_client.create_session.assert_called_once_with(context.capabilities)


def test_start_session_failure(mock_client, context):
    """Test session start failure."""
    mock_client.create_session.side_effect = SessionNotCreatedError("Failed to create session")
    
    with pytest.raises(SessionNotCreatedError):
        context.start_session()
    
    mock_client.create_session.assert_called_once_with(context.capabilities)
    assert context.session_id is None


def test_end_session_with_active_session(mock_client, context):
    """Test ending an active session."""
    context.session_id = "test-session-123"
    
    context.end_session()
    
    mock_client.end_session.assert_called_once_with("test-session-123")
    assert context.session_id is None


def test_end_session_without_active_session(mock_client, context):
    """Test ending without an active session."""
    context.session_id = None
    
    context.end_session()
    
    mock_client.end_session.assert_not_called()
    assert context.session_id is None


def test_context_manager(mock_client, context):
    """Test using the context as a context manager."""
    mock_client.create_session.return_value = {"sessionId": "test-session-123"}
    
    with context as ctx:
        assert ctx.session_id == "test-session-123"
        mock_client.create_session.assert_called_once_with(context.capabilities)
    
    mock_client.end_session.assert_called_once_with("test-session-123")
    assert context.session_id is None


def test_execute_without_session(context):
    """Test executing a command without an active session."""
    context.session_id = None
    
    with pytest.raises(SessionNotCreatedError):
        context.execute("findElement", {"using": "id", "value": "login_button"})


def test_execute_with_session(mock_client, context):
    """Test executing a command with an active session."""
    context.session_id = "test-session-123"
    mock_client.execute_command.return_value = {"value": "test-result"}
    
    result = context.execute("findElement", {"using": "id", "value": "login_button"})
    
    assert result == {"value": "test-result"}
    mock_client.execute_command.assert_called_once_with(
        "test-session-123", "findElement", {"using": "id", "value": "login_button"}
    )


def test_find_element_success(mock_client, context):
    """Test finding an element successfully."""
    context.session_id = "test-session-123"
    mock_client.execute_command.return_value = {"value": {"ELEMENT": "element-123"}}
    
    element_id = context.find_element("id", "login_button")
    
    assert element_id == "element-123"
    mock_client.execute_command.assert_called_once()


def test_find_element_not_found(mock_client, context):
    """Test finding an element that doesn't exist."""
    context.session_id = "test-session-123"
    mock_client.execute_command.return_value = {"value": None}
    
    with pytest.raises(ElementNotFoundError):
        context.find_element("id", "nonexistent_button")


def test_find_elements_success(mock_client, context):
    """Test finding multiple elements successfully."""
    context.session_id = "test-session-123"
    mock_client.execute_command.return_value = {
        "value": [
            {"ELEMENT": "element-1"},
            {"ELEMENT": "element-2"}
        ]
    }
    
    element_ids = context.find_elements("class name", "android.widget.Button")
    
    assert element_ids == ["element-1", "element-2"]
    mock_client.execute_command.assert_called_once()


def test_find_elements_none_found(mock_client, context):
    """Test finding multiple elements with none found."""
    context.session_id = "test-session-123"
    mock_client.execute_command.return_value = {"value": []}
    
    element_ids = context.find_elements("class name", "android.widget.Button")
    
    assert element_ids == []
    mock_client.execute_command.assert_called_once()


def test_click_element(mock_client, context):
    """Test clicking an element."""
    context.session_id = "test-session-123"
    element_id = "element-123"
    
    context.click_element(element_id)
    
    mock_client.execute_command.assert_called_once_with(
        "test-session-123", "click", {"elementId": element_id}
    )


def test_send_keys(mock_client, context):
    """Test sending keys to an element."""
    context.session_id = "test-session-123"
    element_id = "element-123"
    text = "test text"
    
    context.send_keys(element_id, text)
    
    mock_client.execute_command.assert_called_once_with(
        "test-session-123", "sendKeys", {"elementId": element_id, "text": text}
    )


def test_get_text(mock_client, context):
    """Test getting text from an element."""
    context.session_id = "test-session-123"
    element_id = "element-123"
    mock_client.execute_command.return_value = {"value": "Element text"}
    
    text = context.get_text(element_id)
    
    assert text == "Element text"
    mock_client.execute_command.assert_called_once()


def test_get_page_source(mock_client, context):
    """Test getting page source."""
    context.session_id = "test-session-123"
    mock_client.execute_command.return_value = {"value": "<xml>page source</xml>"}
    
    source = context.get_page_source()
    
    assert source == "<xml>page source</xml>"
    mock_client.execute_command.assert_called_once()


def test_take_screenshot(mock_client, context):
    """Test taking a screenshot."""
    context.session_id = "test-session-123"
    mock_client.execute_command.return_value = {"value": "base64-encoded-image"}
    
    screenshot = context.take_screenshot()
    
    assert screenshot == "base64-encoded-image"
    mock_client.execute_command.assert_called_once()
