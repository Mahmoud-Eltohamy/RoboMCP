"""
Tests for the client module
===========================

This module contains tests for the AppiumClient class.
"""

import pytest
import responses
from unittest.mock import patch, MagicMock

from mcp_appium.client import AppiumClient
from mcp_appium.errors import ConnectionError, SessionNotCreatedError, InvalidArgumentError
from mcp_appium.models import Session


@pytest.fixture
def client():
    """Create a client for testing."""
    return AppiumClient()


@responses.activate
def test_connect_success(client):
    """Test connecting to the Appium server successfully."""
    responses.add(
        responses.GET,
        "http://localhost:4723/status",
        json={"value": {"ready": True, "message": "Appium server is ready"}},
        status=200
    )
    
    result = client.connect()
    assert result is True


@responses.activate
def test_connect_failure(client):
    """Test connecting to the Appium server with a failure."""
    responses.add(
        responses.GET,
        "http://localhost:4723/status",
        json={"value": {"ready": False}},
        status=500
    )
    
    with pytest.raises(ConnectionError):
        client.connect()


@responses.activate
def test_create_session_success(client):
    """Test creating a session successfully."""
    session_id = "12345"
    capabilities = {"platformName": "Android"}
    
    responses.add(
        responses.POST,
        "http://localhost:4723/session",
        json={
            "value": {
                "sessionId": session_id,
                "capabilities": capabilities
            }
        },
        status=200
    )
    
    session = client.create_session(capabilities)
    
    assert isinstance(session, Session)
    assert session.id == session_id
    assert session.capabilities == capabilities
    assert client.session_id == session_id


@responses.activate
def test_create_session_failure(client):
    """Test creating a session with a failure."""
    capabilities = {"platformName": "Android"}
    
    responses.add(
        responses.POST,
        "http://localhost:4723/session",
        json={"value": {"error": "Session not created"}},
        status=500
    )
    
    with pytest.raises(SessionNotCreatedError):
        client.create_session(capabilities)


def test_create_session_empty_capabilities(client):
    """Test creating a session with empty capabilities."""
    with pytest.raises(InvalidArgumentError):
        client.create_session({})


@responses.activate
def test_execute_command_success(client):
    """Test executing a command successfully."""
    session_id = "12345"
    client.session_id = session_id
    
    responses.add(
        responses.GET,
        f"http://localhost:4723/session/{session_id}/screenshot",
        json={"value": "base64-screenshot-data"},
        status=200
    )
    
    result = client.execute_command("screenshot")
    
    assert result["value"] == "base64-screenshot-data"


def test_execute_command_no_session(client):
    """Test executing a command with no active session."""
    client.session_id = None
    
    with pytest.raises(SessionNotCreatedError):
        client.execute_command("screenshot")


def test_execute_command_unknown_command(client):
    """Test executing an unknown command."""
    client.session_id = "12345"
    
    with pytest.raises(InvalidArgumentError):
        client.execute_command("unknown_command")


@responses.activate
def test_quit_success(client):
    """Test quitting a session successfully."""
    session_id = "12345"
    client.session_id = session_id
    
    responses.add(
        responses.DELETE,
        f"http://localhost:4723/session/{session_id}",
        json={"value": None},
        status=200
    )
    
    client.quit()
    
    assert client.session_id is None
    assert client.session is None


@responses.activate
def test_quit_with_error(client):
    """Test quitting a session with an error."""
    session_id = "12345"
    client.session_id = session_id
    
    responses.add(
        responses.DELETE,
        f"http://localhost:4723/session/{session_id}",
        json={"value": {"error": "Session not found"}},
        status=404
    )
    
    client.quit()
    
    # Even with an error, the session should be cleared
    assert client.session_id is None
    assert client.session is None
