"""
Tests for the element module
===========================

This module contains tests for the Element class.
"""

import pytest
from unittest.mock import MagicMock, patch

from mcp_appium.element import Element
from mcp_appium.errors import InvalidArgumentError, ElementNotFoundError


@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    mock_session = MagicMock()
    mock_session.id = "session123"
    mock_client = MagicMock()
    mock_session.client = mock_client
    return mock_session


@pytest.fixture
def element(mock_session):
    """Create an element for testing."""
    return Element(mock_session, "element123")


def test_element_initialization(mock_session):
    """Test element initialization."""
    element_id = "element123"
    element_info = {"key": "value"}
    
    element = Element(mock_session, element_id, element_info)
    
    assert element.session == mock_session
    assert element.id == element_id
    assert element.info == element_info


def test_click(element):
    """Test clicking an element."""
    element.click()
    
    element.session.client.execute_command.assert_called_once_with(
        "click", {"element_id": element.id}
    )


def test_clear(element):
    """Test clearing an element."""
    element.clear()
    
    element.session.client.execute_command.assert_called_once_with(
        "clear", {"element_id": element.id}
    )


def test_send_keys_success(element):
    """Test sending keys to an element successfully."""
    text = "test text"
    element.send_keys(text)
    
    element.session.client.execute_command.assert_called_once_with(
        "sendKeys", 
        {
            "element_id": element.id,
            "text": text,
            "value": list(text)
        }
    )


def test_send_keys_empty_text(element):
    """Test sending empty text to an element."""
    with pytest.raises(InvalidArgumentError):
        element.send_keys("")


def test_get_text(element):
    """Test getting an element's text."""
    expected_text = "Element text"
    element.session.client.execute_command.return_value = {"value": expected_text}
    
    text = element.get_text()
    
    element.session.client.execute_command.assert_called_once_with(
        "getText", {"element_id": element.id}
    )
    assert text == expected_text


def test_get_attribute_success(element):
    """Test getting an element's attribute successfully."""
    attribute_name = "class"
    expected_value = "button"
    element.session.client.execute_command.return_value = {"value": expected_value}
    
    value = element.get_attribute(attribute_name)
    
    element.session.client.execute_command.assert_called_once_with(
        "getAttribute", 
        {
            "element_id": element.id,
            "name": attribute_name
        }
    )
    assert value == expected_value


def test_get_attribute_empty_name(element):
    """Test getting an attribute with an empty name."""
    with pytest.raises(InvalidArgumentError):
        element.get_attribute("")


def test_is_displayed(element):
    """Test checking if an element is displayed."""
    element.session.client.execute_command.return_value = {"value": True}
    
    result = element.is_displayed()
    
    element.session.client.execute_command.assert_called_once_with(
        "isDisplayed", {"element_id": element.id}
    )
    assert result is True


def test_is_enabled(element):
    """Test checking if an element is enabled."""
    element.session.client.execute_command.return_value = {"value": True}
    
    result = element.is_enabled()
    
    element.session.client.execute_command.assert_called_once_with(
        "isEnabled", {"element_id": element.id}
    )
    assert result is True


def test_is_selected(element):
    """Test checking if an element is selected."""
    element.session.client.execute_command.return_value = {"value": False}
    
    result = element.is_selected()
    
    element.session.client.execute_command.assert_called_once_with(
        "isSelected", {"element_id": element.id}
    )
    assert result is False


def test_find_element_success(element, mock_session):
    """Test finding a child element successfully."""
    by = "id"
    value = "childElement"
    child_element_id = "child123"
    element.session.client.execute_command.return_value = {
        "value": {"ELEMENT": child_element_id}
    }
    
    child_element = element.find_element(by, value)
    
    element.session.client.execute_command.assert_called_once_with(
        "findElementFromElement", 
        {
            "element_id": element.id,
            "using": by,
            "value": value
        }
    )
    assert isinstance(child_element, Element)
    assert child_element.id == child_element_id
    assert child_element.session == mock_session


def test_find_element_empty_by(element):
    """Test finding a child element with an empty locator strategy."""
    with pytest.raises(InvalidArgumentError):
        element.find_element("", "value")


def test_find_element_empty_value(element):
    """Test finding a child element with an empty locator value."""
    with pytest.raises(InvalidArgumentError):
        element.find_element("id", "")


def test_find_element_not_found(element):
    """Test finding a child element that doesn't exist."""
    element.session.client.execute_command.return_value = {"value": {}}
    
    with pytest.raises(ElementNotFoundError):
        element.find_element("id", "nonExistentElement")


def test_find_elements_success(element, mock_session):
    """Test finding child elements successfully."""
    by = "class name"
    value = "button"
    element.session.client.execute_command.return_value = {
        "value": [
            {"ELEMENT": "child1"},
            {"ELEMENT": "child2"}
        ]
    }
    
    children = element.find_elements(by, value)
    
    element.session.client.execute_command.assert_called_once_with(
        "findElementsFromElement", 
        {
            "element_id": element.id,
            "using": by,
            "value": value
        }
    )
    assert len(children) == 2
    assert all(isinstance(child, Element) for child in children)
    assert children[0].id == "child1"
    assert children[1].id == "child2"
    assert all(child.session == mock_session for child in children)


def test_find_elements_empty_by(element):
    """Test finding child elements with an empty locator strategy."""
    with pytest.raises(InvalidArgumentError):
        element.find_elements("", "value")


def test_find_elements_empty_value(element):
    """Test finding child elements with an empty locator value."""
    with pytest.raises(InvalidArgumentError):
        element.find_elements("id", "")


def test_find_elements_none_found(element):
    """Test finding child elements when none exist."""
    element.session.client.execute_command.return_value = {"value": []}
    
    children = element.find_elements("id", "nonExistentElement")
    
    assert len(children) == 0


def test_str_representation(element):
    """Test the string representation of an element."""
    assert str(element) == "Element(id=element123)"


def test_repr_representation(element):
    """Test the detailed representation of an element."""
    assert repr(element) == "Element(id=element123, session_id=session123)"
