"""
Robot Framework Mobile Test Generator
====================================

This script generates Robot Framework test scripts using AppiumLibrary
for any given mobile application. It provides a generic framework to:

1. Generate a base test suite with setup/teardown
2. Create test cases for common mobile interactions
3. Allow customization for specific applications

Example usage:
    python robot_mobile_generator.py --app ../app_tests/sauce_labs_demo/sauce_labs_demo.apk --output ../data/generated_tests/swaglabs_tests.robot
"""

import os
import sys
import argparse
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to allow importing mcp_appium
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("robot_mobile_generator")

# Path to store generated tests
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ROBOT_DIR = os.path.join(DATA_DIR, "generated_tests")

# Create directories if they don't exist
os.makedirs(ROBOT_DIR, exist_ok=True)

# Default test data for common apps
APP_CONFIGS = {
    "sauce_labs_demo": {
        "login": {
            "username_field": "test-Username",
            "password_field": "test-Password",
            "login_button": "test-LOGIN",
            "credentials": [
                {"username": "standard_user", "password": "secret_sauce"}
            ],
            "success_indicator": "//android.view.ViewGroup[@content-desc='test-Inventory page']"
        },
        "product_page": {
            "products_container": "//android.widget.ScrollView[@content-desc='test-PRODUCTS']",
            "product_item": "//android.view.ViewGroup[@content-desc='test-Item']",
            "add_to_cart_button": "//android.view.ViewGroup[@content-desc='test-ADD TO CART']",
            "product_name": "//android.widget.TextView[@content-desc='test-Item title']",
            "cart_button": "//android.view.ViewGroup[@content-desc='test-Cart']"
        },
        "checkout": {
            "checkout_button": "//android.view.ViewGroup[@content-desc='test-CHECKOUT']",
            "first_name_field": "//android.widget.EditText[@content-desc='test-First Name']",
            "last_name_field": "//android.widget.EditText[@content-desc='test-Last Name']",
            "postal_code_field": "//android.widget.EditText[@content-desc='test-Zip/Postal Code']",
            "continue_button": "//android.view.ViewGroup[@content-desc='test-CONTINUE']",
            "finish_button": "//android.view.ViewGroup[@content-desc='test-FINISH']",
            "success_message": "//android.widget.TextView[@text='THANK YOU FOR YOU ORDER']"
        }
    }
}


class RobotMobileGenerator:
    """Generator for Robot Framework mobile test scripts using AppiumLibrary."""
    
    def __init__(self, app_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Robot Framework mobile test generator.
        
        Args:
            app_path: Path to the mobile app APK to test
            config: Optional configuration for the specific app
        """
        self.app_path = app_path
        self.app_name = self._extract_app_name(app_path)
        self.config = self._get_config(config)
    
    def _extract_app_name(self, app_path: str) -> str:
        """Extract the app name from the APK path."""
        # Get the filename without extension
        app_file = os.path.basename(app_path)
        app_name = os.path.splitext(app_file)[0]
        
        # Clean up the name
        app_name = app_name.lower().replace(" ", "_")
        
        return app_name
    
    def _get_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get configuration for the app.
        
        Args:
            config: Custom configuration (optional)
            
        Returns:
            Dict: Configuration for the app
        """
        if config:
            return config
        
        # Try to find a matching configuration
        for app_id, app_config in APP_CONFIGS.items():
            if app_id in self.app_name:
                logger.info(f"Using predefined configuration for {app_id}")
                return app_config
        
        # Return a generic configuration
        logger.info("Using generic configuration")
        return {
            "login": {
                "username_field": "//android.widget.EditText[1]",
                "password_field": "//android.widget.EditText[2]",
                "login_button": "//android.widget.Button[contains(@text, 'Login') or contains(@text, 'Sign in')]"
            }
        }
    
    def generate_robot_suite(self, output_file: str) -> bool:
        """
        Generate a complete Robot Framework test suite.
        
        Args:
            output_file: Path to save the generated Robot Framework test suite
            
        Returns:
            bool: True if generation was successful, False otherwise
        """
        try:
            # Generate the suite
            suite_header = self._generate_suite_header()
            settings_section = self._generate_settings_section()
            variables_section = self._generate_variables_section()
            keywords_section = self._generate_keywords_section()
            test_cases = self._generate_test_cases()
            
            # Combine all sections
            robot_suite = f"{suite_header}\n\n{settings_section}\n\n{variables_section}\n\n{keywords_section}\n\n{test_cases}"
            
            # Write to file
            with open(output_file, 'w') as f:
                f.write(robot_suite)
            
            logger.info(f"Generated Robot Framework mobile test suite: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating Robot Framework mobile test suite: {str(e)}")
            return False
    
    def _generate_suite_header(self) -> str:
        """Generate the suite header with documentation."""
        header = f"# Robot Framework Mobile Tests for {self.app_name}\n"
        header += f"# Generated by MCP Appium Robot Mobile Generator"
        return header
    
    def _generate_settings_section(self) -> str:
        """Generate the settings section."""
        settings = "*** Settings ***\n"
        settings += f"Documentation     Automated mobile tests for {self.app_name}\n"
        settings += "Library           AppiumLibrary\n"
        settings += "Suite Setup       Open Application\n"
        settings += "Suite Teardown    Close Application\n"
        return settings
    
    def _generate_variables_section(self) -> str:
        """Generate the variables section."""
        variables = "*** Variables ***\n"
        variables += f"${'APP_PATH'}    {self.app_path}\n"
        
        # Add appium server details
        variables += "${APPIUM_SERVER}    http://localhost:4723/wd/hub\n"
        
        # Add appium desired capabilities
        variables += "\n# Appium Desired Capabilities\n"
        variables += "${PLATFORM_NAME}    Android\n"
        variables += "${AUTOMATION_NAME}    UiAutomator2\n"
        variables += "${DEVICE_NAME}    Android Emulator\n"
        
        # Add app-specific variables based on config
        if "login" in self.config:
            login_config = self.config["login"]
            variables += f"\n# Login selectors\n"
            username_field = login_config.get('username_field', '//android.widget.EditText[1]')
            password_field = login_config.get('password_field', '//android.widget.EditText[2]')
            login_button = login_config.get('login_button', '//android.widget.Button[@text="Login"]')
            
            variables += f"${{'USERNAME_FIELD'}}    {username_field}\n"
            variables += f"${{'PASSWORD_FIELD'}}    {password_field}\n"
            variables += f"${{'LOGIN_BUTTON'}}    {login_button}\n"
            
            # Add credentials if available
            if "credentials" in login_config and login_config["credentials"]:
                cred = login_config["credentials"][0]
                variables += f"${'USERNAME'}    {cred.get('username', 'username')}\n"
                variables += f"${'PASSWORD'}    {cred.get('password', 'password')}\n"
            else:
                variables += "${'USERNAME'}    username\n"
                variables += "${'PASSWORD'}    password\n"
        
        # Add product page selectors if available
        if "product_page" in self.config:
            product_config = self.config["product_page"]
            variables += f"\n# Product page selectors\n"
            products_container = product_config.get('products_container', '//android.widget.ScrollView')
            product_item = product_config.get('product_item', '//android.view.ViewGroup')
            add_to_cart_button = product_config.get('add_to_cart_button', '//android.widget.Button[contains(@text,"Add")]')
            product_name = product_config.get('product_name', '//android.widget.TextView')
            cart_button = product_config.get('cart_button', '//android.widget.Button[contains(@text,"Cart")]')
            
            variables += f"${{'PRODUCTS_CONTAINER'}}    {products_container}\n"
            variables += f"${{'PRODUCT_ITEM'}}    {product_item}\n"
            variables += f"${{'ADD_TO_CART_BUTTON'}}    {add_to_cart_button}\n"
            variables += f"${{'PRODUCT_NAME'}}    {product_name}\n"
            variables += f"${{'CART_BUTTON'}}    {cart_button}\n"
        
        # Add checkout selectors if available
        if "checkout" in self.config:
            checkout_config = self.config["checkout"]
            variables += f"\n# Checkout selectors\n"
            checkout_button = checkout_config.get('checkout_button', '//android.widget.Button[contains(@text,"Checkout")]')
            first_name_field = checkout_config.get('first_name_field', '//android.widget.EditText[1]')
            last_name_field = checkout_config.get('last_name_field', '//android.widget.EditText[2]')
            postal_code_field = checkout_config.get('postal_code_field', '//android.widget.EditText[3]')
            continue_button = checkout_config.get('continue_button', '//android.widget.Button[contains(@text,"Continue")]')
            finish_button = checkout_config.get('finish_button', '//android.widget.Button[contains(@text,"Finish")]')
            success_message = checkout_config.get('success_message', '//android.widget.TextView[contains(@text,"Thank")]')
            
            variables += f"${{'CHECKOUT_BUTTON'}}    {checkout_button}\n"
            variables += f"${{'FIRST_NAME_FIELD'}}    {first_name_field}\n"
            variables += f"${{'LAST_NAME_FIELD'}}    {last_name_field}\n"
            variables += f"${{'POSTAL_CODE_FIELD'}}    {postal_code_field}\n"
            variables += f"${{'CONTINUE_BUTTON'}}    {continue_button}\n"
            variables += f"${{'FINISH_BUTTON'}}    {finish_button}\n"
            variables += f"$SUCCESS_MESSAGE    {success_message}\n"
        
        return variables
    
    def _generate_keywords_section(self) -> str:
        """Generate the keywords section with reusable keywords."""
        keywords = "*** Keywords ***\n"
        
        # Open Application keyword
        keywords += "Open Application\n"
        keywords += "    AppiumLibrary.Open Application    ${APPIUM_SERVER}\n"
        keywords += "    ...    platformName=${PLATFORM_NAME}\n"
        keywords += "    ...    automationName=${AUTOMATION_NAME}\n"
        keywords += "    ...    deviceName=${DEVICE_NAME}\n"
        keywords += "    ...    app=${APP_PATH}\n"
        keywords += "    ...    newCommandTimeout=60\n"
        keywords += "    ...    appActivity=com.swaglabsmobileapp.MainActivity\n\n"
        
        # Login keyword
        if "login" in self.config:
            keywords += "Login\n"
            keywords += "    [Arguments]    ${username}=${'USERNAME'}    ${password}=${'PASSWORD'}\n"
            keywords += "    Wait Until Element Is Visible    ${'USERNAME_FIELD'}    timeout=30s\n"
            keywords += "    Input Text    ${'USERNAME_FIELD'}    ${username}\n"
            keywords += "    Input Text    ${'PASSWORD_FIELD'}    ${password}\n"
            keywords += "    Click Element    ${'LOGIN_BUTTON'}\n"
            
            # Add a wait for success indicator if available
            if "success_indicator" in self.config["login"]:
                success_selector = self.config["login"]["success_indicator"]
                keywords += f"    Wait Until Element Is Visible    {success_selector}    timeout=10s\n"
            
            keywords += "\n"
        
        # Add to cart keyword if product page config exists
        if "product_page" in self.config:
            keywords += "Add Product To Cart\n"
            keywords += "    [Arguments]    ${index}=1\n"
            keywords += "    Wait Until Element Is Visible    ${'PRODUCTS_CONTAINER'}    timeout=10s\n"
            keywords += "    ${product_elements}=    Get WebElements    ${'PRODUCT_ITEM'}\n"
            keywords += "    ${product}=    Get From List    ${product_elements}    ${index}\n"
            keywords += "    ${product_name}=    Get Text    ${product}${'PRODUCT_NAME'}\n"
            keywords += "    Click Element    ${product}${'ADD_TO_CART_BUTTON'}\n"
            keywords += "    [Return]    ${product_name}\n\n"
            
            keywords += "Go To Cart\n"
            keywords += "    Click Element    ${'CART_BUTTON'}\n\n"
        
        # Checkout keywords if checkout config exists
        if "checkout" in self.config:
            keywords += "Complete Checkout\n"
            keywords += "    [Arguments]    ${first_name}=John    ${last_name}=Doe    ${postal_code}=12345\n"
            keywords += "    Wait Until Element Is Visible    ${'CHECKOUT_BUTTON'}    timeout=10s\n"
            keywords += "    Click Element    ${'CHECKOUT_BUTTON'}\n"
            keywords += "    Wait Until Element Is Visible    ${'FIRST_NAME_FIELD'}    timeout=10s\n"
            keywords += "    Input Text    ${'FIRST_NAME_FIELD'}    ${first_name}\n"
            keywords += "    Input Text    ${'LAST_NAME_FIELD'}    ${last_name}\n"
            keywords += "    Input Text    ${'POSTAL_CODE_FIELD'}    ${postal_code}\n"
            keywords += "    Click Element    ${'CONTINUE_BUTTON'}\n"
            keywords += "    Wait Until Element Is Visible    ${'FINISH_BUTTON'}    timeout=10s\n"
            keywords += "    Click Element    ${'FINISH_BUTTON'}\n"
            
            # Add a wait for success message if available
            keywords += f"    Wait Until Element Is Visible    $SUCCESS_MESSAGE    timeout=10s\n\n"
        
        return keywords
    
    def _generate_test_cases(self) -> str:
        """Generate test cases for the mobile app."""
        test_cases = "*** Test Cases ***\n"
        
        # Login test
        if "login" in self.config:
            test_cases += "Verify Login\n"
            test_cases += "    Login\n"
            
            # Add success verification if available
            if "success_indicator" in self.config["login"]:
                success_selector = self.config["login"]["success_indicator"]
                test_cases += f"    Element Should Be Visible    {success_selector}\n\n"
            else:
                test_cases += "    # Verify login success based on page content\n\n"
        
        # Product browsing and cart test
        if "product_page" in self.config:
            test_cases += "Add Product To Cart\n"
            test_cases += "    Login\n"
            test_cases += "    ${product_name}=    Add Product To Cart\n"
            test_cases += "    Go To Cart\n"
            test_cases += "    Page Should Contain Text    ${product_name}\n\n"
        
        # Complete checkout test
        if "checkout" in self.config:
            test_cases += "Complete Checkout Process\n"
            test_cases += "    Login\n"
            test_cases += "    Add Product To Cart\n"
            test_cases += "    Go To Cart\n"
            test_cases += "    Complete Checkout\n"
            test_cases += f"    Element Should Be Visible    $SUCCESS_MESSAGE\n\n"
        
        # Generic test for any app
        test_cases += "Take Screenshot\n"
        test_cases += "    Capture Page Screenshot\n\n"
        
        test_cases += "Verify App Elements\n"
        test_cases += "    Page Should Contain Element    ${'USERNAME_FIELD'}\n"
        test_cases += "    Page Should Contain Element    ${'PASSWORD_FIELD'}\n"
        test_cases += "    Page Should Contain Element    ${'LOGIN_BUTTON'}\n"
        
        return test_cases


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate Robot Framework mobile tests")
    parser.add_argument("--app", type=str, help="Path to the mobile app APK to test", 
                        default="../app_tests/sauce_labs_demo/sauce_labs_demo.apk")
    parser.add_argument("--output", type=str, help="Path to save the generated Robot Framework tests")
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    
    app_path = args.app
    
    # Ensure the APK file exists
    if not os.path.exists(app_path):
        logger.error(f"APK file not found: {app_path}")
        return 1
    
    # Determine output file path
    if args.output:
        output_file = args.output
    else:
        # Extract app name for the filename
        app_name = os.path.splitext(os.path.basename(app_path))[0]
        output_file = os.path.join(ROBOT_DIR, f"{app_name}_mobile_tests.robot")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Create generator and generate tests
    generator = RobotMobileGenerator(app_path)
    success = generator.generate_robot_suite(output_file)
    
    if success:
        logger.info(f"Successfully generated Robot Framework mobile tests: {output_file}")
    else:
        logger.error("Failed to generate Robot Framework mobile tests")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())