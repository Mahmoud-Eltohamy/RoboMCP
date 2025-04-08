"""
Tests for the AppiumModel class.

This module contains unit tests for the AppiumModel class to ensure proper
representation and interaction with UI elements.
"""

import pytest
from unittest.mock import patch, MagicMock, call

from mcp_appium.model import AppiumModel, By
from mcp_appium.context import AppiumContext
from mcp_appium.exceptions import ElementNotFoundError, InvalidArgumentError


@pytest.fixture
def mock_context():
    """Create a mocked context for testing."""
    return MagicMock(spec=AppiumContext)


@pytest.fixture
def model(mock_context):
    """Create a model with a mocked context for testing."""
    return AppiumModel(mock_context, By.ID, "login_button", "Login Button")


def test_init_with_string_by(mock_context):
    """Test initialization with string locator strategy."""
    model = AppiumModel(mock_context, "id", "login_button", "Login Button")
    
    assert model.by == "id"
    assert model.value == "login_button"
    assert model.name == "Login Button"
    assert model.element_id is None


def test_init_with_enum_by(mock_context):
    """Test initialization with By enum locator strategy."""
    model = AppiumModel(mock_context, By.ID, "login_button", "Login Button")
    
    assert model.by == "id"
    assert model.value == "login_button"
    assert model.name == "Login Button"
    assert model.element_id is None


def test_init_without_name(mock_context):
    """Test initialization without a name."""
    model = AppiumModel(mock_context, By.ID, "login_button")
    
    assert model.name == "id=login_button"


def test_repr(model):
    """Test string representation."""
    assert repr(model) == "AppiumModel(name='Login Button', by='id', value='login_button')"


def test_locate_success(mock_context, model):
    """Test locating an element successfully."""
    mock_context.find_element.return_value = "element-123"
    
    assert model.locate() is True
    assert model.element_id == "element-123"
    mock_context.find_element.assert_called_once_with("id", "login_button")


def test_locate_failure(mock_context, model):
    """Test locating an element that doesn't exist."""
    mock_context.find_element.side_effect = ElementNotFoundError("Element not found")
    
    assert model.locate() is False
    assert model.element_id is None
    mock_context.find_element.assert_called_once_with("id", "login_button")


def test_assert_located_already_located(mock_context, model):
    """Test asserting an element is located when it already is."""
    model.element_id = "element-123"
    
    model.assert_located()
    
    mock_context.find_element.assert_not_called()


def test_assert_located_needs_locating_success(mock_context, model):
    """Test asserting an element is located when it needs to be located first."""
    model.element_id = None
    mock_context.find_element.return_value = "element-123"
    
    model.assert_located()
    
    assert model.element_id == "element-123"
    mock_context.find_element.assert_called_once_with("id", "login_button")


def test_assert_located_needs_locating_failure(mock_context, model):
    """Test asserting an element is located when it can't be found."""
    model.element_id = None
    mock_context.find_element.side_effect = ElementNotFoundError("Element not found")
    
    with pytest.raises(ElementNotFoundError):
        model.assert_located()
        
    mock_context.find_element.assert_called_once_with("id", "login_button")


def test_click(mock_context, model):
    """Test clicking an element."""
    model.element_id = "element-123"
    
    result = model.click()
    
    assert result is model  # Method chaining returns self
    mock_context.click_element.assert_called_once_with("element-123")


def test_click_not_located(mock_context, model):
    """Test clicking an element that needs to be located first."""
    model.element_id = None
    mock_context.find_element.return_value = "element-123"
    
    model.click()
    
    mock_context.find_element.assert_called_once_with("id", "login_button")
    mock_context.click_element.assert_called_once_with("element-123")


def test_send_keys(mock_context, model):
    """Test sending keys to an element."""
    model.element_id = "element-123"
    
    result = model.send_keys("test text")
    
    assert result is model  # Method chaining returns self
    mock_context.send_keys.assert_called_once_with("element-123", "test text")


def test_get_text(mock_context, model):
    """Test getting text from an element."""
    model.element_id = "element-123"
    mock_context.get_text.return_value = "Button Text"
    
    text = model.get_text()
    
    assert text == "Button Text"
    mock_context.get_text.assert_called_once_with("element-123")


def test_is_displayed_true(mock_context, model):
    """Test checking if an element is displayed when it is."""
    model.element_id = "element-123"
    mock_context.execute.return_value = {"value": True}
    
    assert model.is_displayed() is True
    mock_context.execute.assert_called_once_with("isDisplayed", {"elementId": "element-123"})


def test_is_displayed_false(mock_context, model):
    """Test checking if an element is displayed when it isn't."""
    model.element_id = "element-123"
    mock_context.execute.return_value = {"value": False}
    
    assert model.is_displayed() is False
    mock_context.execute.assert_called_once_with("isDisplayed", {"elementId": "element-123"})


def test_is_displayed_not_found(mock_context, model):
    """Test checking if an element is displayed when it can't be found."""
    model.element_id = None
    mock_context.find_element.side_effect = ElementNotFoundError("Element not found")
    
    assert model.is_displayed() is False
    mock_context.find_element.assert_called_once_with("id", "login_button")


def test_swipe_invalid_direction(mock_context, model):
    """Test swiping with an invalid direction."""
    model.element_id = "element-123"
    
    with pytest.raises(InvalidArgumentError):
        model.swipe("invalid")


def test_swipe_invalid_percentage(mock_context, model):
    """Test swiping with an invalid percentage."""
    model.element_id = "element-123"
    
    with pytest.raises(InvalidArgumentError):
        model.swipe("up", percentage=1.5)


def test_swipe_valid(mock_context, model):
    """Test swiping with valid parameters."""
    model.element_id = "element-123"
    
    result = model.swipe("up", percentage=0.75, speed=500)
    
    assert result is model  # Method chaining returns self
    mock_context.execute.assert_called_once_with("swipe", {
        "elementId": "element-123",
        "direction": "up",
        "percent": 0.75,
        "speed": 500
    })


def test_long_press(mock_context, model):
    """Test long pressing an element."""
    model.element_id = "element-123"
    
    result = model.long_press(duration=2000)
    
    assert result is model  # Method chaining returns self
    mock_context.execute.assert_called_once_with("longPress", {
        "elementId": "element-123",
        "duration": 2000
    })


def test_find_child_with_id(mock_context, model):
    """Test finding a child element by ID."""
    model.element_id = "element-123"
    mock_context.find_element.return_value = "child-element-456"
    
    child = model.find_child(By.ID, "child_button", "Child Button")
    
    assert child.by == "xpath"
    assert child.value == ".//*[@resource-id='child_button']"
    assert child.name == "Child Button"
    mock_context.find_element.assert_called_once()


def test_find_child_with_xpath(mock_context, model):
    """Test finding a child element by XPath."""
    model.element_id = "element-123"
    mock_context.find_element.return_value = "child-element-456"
    
    child = model.find_child(By.XPATH, "//android.widget.Button", "Child Button")
    
    assert child.by == "xpath"
    assert child.value == ".//android.widget.Button"
    assert child.name == "Child Button"
    mock_context.find_element.assert_called_once()


def test_find_child_not_found(mock_context, model):
    """Test finding a child element that doesn't exist."""
    model.element_id = "element-123"
    mock_context.find_element.side_effect = ElementNotFoundError("Element not found")
    
    with pytest.raises(ElementNotFoundError):
        model.find_child(By.ID, "nonexistent_button")
