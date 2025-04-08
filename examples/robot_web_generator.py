"""
Robot Framework Web Test Generator
=================================

This script generates Robot Framework test scripts using Browser Library
for any given website. It provides a generic framework to:

1. Generate a base test suite with setup/teardown
2. Create test cases for common web interactions 
3. Allow customization for specific websites

Example usage:
    python robot_web_generator.py --url https://www.saucedemo.com/ --output ../data/generated_tests/saucedemo_tests.robot
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to allow importing mcp_appium
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("robot_web_generator")

# Path to store generated tests
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ROBOT_DIR = os.path.join(DATA_DIR, "generated_tests")

# Create directories if they don't exist
os.makedirs(ROBOT_DIR, exist_ok=True)

# Default test data for common websites
WEBSITE_CONFIGS = {
    "saucedemo.com": {
        "login": {
            "username_selector": "input[data-test='username']",
            "password_selector": "input[data-test='password']",
            "login_button_selector": "input[data-test='login-button']",
            "credentials": [
                {"username": "standard_user", "password": "secret_sauce"}
            ],
            "success_indicator": ".inventory_container"
        },
        "product_page": {
            "product_item_selector": ".inventory_item",
            "add_to_cart_selector": "button[data-test^='add-to-cart']",
            "product_name_selector": ".inventory_item_name",
            "product_price_selector": ".inventory_item_price",
            "cart_button": ".shopping_cart_link"
        },
        "checkout": {
            "checkout_button_selector": "button[data-test='checkout']",
            "first_name_selector": "input[data-test='firstName']",
            "last_name_selector": "input[data-test='lastName']",
            "postal_code_selector": "input[data-test='postalCode']",
            "continue_button_selector": "input[data-test='continue']",
            "finish_button_selector": "button[data-test='finish']",
            "success_message_selector": ".complete-header"
        }
    }
}


class RobotWebGenerator:
    """Generator for Robot Framework web test scripts using Browser Library."""
    
    def __init__(self, url: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Robot Framework web test generator.
        
        Args:
            url: URL of the website to test
            config: Optional configuration for the specific website
        """
        self.url = url
        self.domain = self._extract_domain(url)
        self.config = self._get_config(config)
    
    def _extract_domain(self, url: str) -> str:
        """Extract the domain from a URL."""
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        return parsed_url.netloc
    
    def _get_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get configuration for the website.
        
        Args:
            config: Custom configuration (optional)
            
        Returns:
            Dict: Configuration for the website
        """
        if config:
            return config
        
        # Try to find a matching configuration
        for domain, domain_config in WEBSITE_CONFIGS.items():
            if domain in self.domain:
                logger.info(f"Using predefined configuration for {domain}")
                return domain_config
        
        # Return a generic configuration
        logger.info("Using generic configuration")
        return {
            "login": {
                "username_selector": "input[type='text']",
                "password_selector": "input[type='password']",
                "login_button_selector": "button[type='submit']"
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
            
            logger.info(f"Generated Robot Framework web test suite: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating Robot Framework web test suite: {str(e)}")
            return False
    
    def _generate_suite_header(self) -> str:
        """Generate the suite header with documentation."""
        header = f"# Robot Framework Web Tests for {self.url}\n"
        header += f"# Generated by MCP Appium Robot Web Generator"
        return header
    
    def _generate_settings_section(self) -> str:
        """Generate the settings section."""
        settings = "*** Settings ***\n"
        settings += "Documentation     Automated web tests for " + self.url + "\n"
        settings += "Library           Browser\n"
        settings += "Suite Setup       Setup Browser\n"
        settings += "Suite Teardown    Close Browser    ALL\n"
        return settings
    
    def _generate_variables_section(self) -> str:
        """Generate the variables section."""
        variables = "*** Variables ***\n"
        variables += f"${'URL'}    {self.url}\n"
        
        # Add website-specific variables based on config
        if "login" in self.config:
            login_config = self.config["login"]
            username_selector = login_config.get('username_selector', "input[type='text']")
            password_selector = login_config.get('password_selector', "input[type='password']")
            login_button_selector = login_config.get('login_button_selector', "button[type='submit']")
            variables += f"${{'USERNAME_SELECTOR'}}    {username_selector}\n"
            variables += f"${{'PASSWORD_SELECTOR'}}    {password_selector}\n"
            variables += f"${{'LOGIN_BUTTON_SELECTOR'}}    {login_button_selector}\n"
            
            # Add credentials if available
            if "credentials" in login_config and login_config["credentials"]:
                cred = login_config["credentials"][0]
                username = cred.get('username', 'username')
                password = cred.get('password', 'password')
            else:
                username = "username"
                password = "password"
                
            variables += f"${{'USERNAME'}}    {username}\n"
            variables += f"${{'PASSWORD'}}    {password}\n"
        
        # Add product page selectors if available
        if "product_page" in self.config:
            product_config = self.config["product_page"]
            variables += f"\n# Product page selectors\n"
            product_item = product_config.get('product_item_selector', '.product')
            add_to_cart = product_config.get('add_to_cart_selector', 'button.add-to-cart')
            product_name = product_config.get('product_name_selector', '.product-name')
            cart_button = product_config.get('cart_button', 'a.cart')
            
            variables += f"${{'PRODUCT_ITEM_SELECTOR'}}    {product_item}\n"
            variables += f"${{'ADD_TO_CART_SELECTOR'}}    {add_to_cart}\n"
            variables += f"${{'PRODUCT_NAME_SELECTOR'}}    {product_name}\n"
            variables += f"${{'CART_BUTTON'}}    {cart_button}\n"
        
        # Add checkout selectors if available
        if "checkout" in self.config:
            checkout_config = self.config["checkout"]
            variables += f"\n# Checkout selectors\n"
            checkout_button = checkout_config.get('checkout_button_selector', 'button.checkout')
            first_name_selector = checkout_config.get('first_name_selector', "input[name='firstName']")
            last_name_selector = checkout_config.get('last_name_selector', "input[name='lastName']")
            postal_code_selector = checkout_config.get('postal_code_selector', "input[name='postalCode']")
            continue_button = checkout_config.get('continue_button_selector', 'button.continue')
            finish_button = checkout_config.get('finish_button_selector', 'button.finish')
            success_message = checkout_config.get('success_message_selector', '.success-message')
            
            variables += f"${{'CHECKOUT_BUTTON_SELECTOR'}}    {checkout_button}\n"
            variables += f"${{'FIRST_NAME_SELECTOR'}}    {first_name_selector}\n"
            variables += f"${{'LAST_NAME_SELECTOR'}}    {last_name_selector}\n"
            variables += f"${{'POSTAL_CODE_SELECTOR'}}    {postal_code_selector}\n"
            variables += f"${{'CONTINUE_BUTTON_SELECTOR'}}    {continue_button}\n"
            variables += f"${{'FINISH_BUTTON_SELECTOR'}}    {finish_button}\n"
            variables += f"${{'SUCCESS_MESSAGE_SELECTOR'}}    {success_message}\n"
        
        return variables
    
    def _generate_keywords_section(self) -> str:
        """Generate the keywords section with reusable keywords."""
        keywords = "*** Keywords ***\n"
        
        # Setup keyword
        keywords += "Setup Browser\n"
        keywords += "    New Browser    chromium    headless=False\n"
        keywords += "    New Context    viewport={'width': 1280, 'height': 720}\n"
        keywords += f"    New Page    {self.url}\n\n"
        
        # Login keyword
        if "login" in self.config:
            keywords += "Login\n"
            keywords += "    [Arguments]    ${username}=${USERNAME}    ${password}=${PASSWORD}\n"
            keywords += "    Fill Text    ${USERNAME_SELECTOR}    ${username}\n"
            keywords += "    Fill Text    ${PASSWORD_SELECTOR}    ${password}\n"
            keywords += "    Click    ${LOGIN_BUTTON_SELECTOR}\n"
            
            # Add a wait for success indicator if available
            if "success_indicator" in self.config["login"]:
                success_selector = self.config["login"]["success_indicator"]
                keywords += f"    Wait For Elements State    {success_selector}    visible    timeout=10s\n"
            
            keywords += "\n"
        
        # Add to cart keyword if product page config exists
        if "product_page" in self.config:
            keywords += "Add Product To Cart\n"
            keywords += "    [Arguments]    ${index}=0\n"
            keywords += "    ${products}=    Get Elements    ${PRODUCT_ITEM_SELECTOR}\n"
            keywords += "    ${product}=    Get From List    ${products}    ${index}\n"
            keywords += "    ${product_name}=    Get Text    ${product} >> ${PRODUCT_NAME_SELECTOR}\n"
            keywords += "    Click    ${product} >> ${ADD_TO_CART_SELECTOR}\n"
            keywords += "    [Return]    ${product_name}\n\n"
            
            keywords += "Go To Cart\n"
            keywords += "    Click    ${CART_BUTTON}\n\n"
        
        # Checkout keywords if checkout config exists
        if "checkout" in self.config:
            keywords += "Complete Checkout\n"
            keywords += "    [Arguments]    ${first_name}=John    ${last_name}=Doe    ${postal_code}=12345\n"
            keywords += "    Click    ${CHECKOUT_BUTTON_SELECTOR}\n"
            keywords += "    Fill Text    ${FIRST_NAME_SELECTOR}    ${first_name}\n"
            keywords += "    Fill Text    ${LAST_NAME_SELECTOR}    ${last_name}\n"
            keywords += "    Fill Text    ${POSTAL_CODE_SELECTOR}    ${postal_code}\n"
            keywords += "    Click    ${CONTINUE_BUTTON_SELECTOR}\n"
            keywords += "    Click    ${FINISH_BUTTON_SELECTOR}\n"
            
            # Add a wait for success message if available
            keywords += f"    Wait For Elements State    ${{SUCCESS_MESSAGE_SELECTOR}}    visible    timeout=10s\n\n"
        
        return keywords
    
    def _generate_test_cases(self) -> str:
        """Generate test cases for the website."""
        test_cases = "*** Test Cases ***\n"
        
        # Login test
        if "login" in self.config:
            test_cases += "Verify Login\n"
            test_cases += "    Login\n"
            
            # Add success verification if available
            if "success_indicator" in self.config["login"]:
                success_selector = self.config["login"]["success_indicator"]
                test_cases += f"    Get Element    {success_selector}\n\n"
            else:
                test_cases += "    # Verify login success based on page content\n\n"
        
        # Product browsing and cart test
        if "product_page" in self.config:
            test_cases += "Add Product To Cart\n"
            test_cases += "    Login\n"
            test_cases += "    ${product_name}=    Add Product To Cart\n"
            test_cases += "    Go To Cart\n"
            test_cases += "    Get Text    ${PRODUCT_NAME_SELECTOR}    ==    ${product_name}\n\n"
        
        # Complete checkout test
        if "checkout" in self.config:
            test_cases += "Complete Checkout Process\n"
            test_cases += "    Login\n"
            test_cases += "    Add Product To Cart\n"
            test_cases += "    Go To Cart\n"
            test_cases += "    Complete Checkout\n"
            test_cases += f"    Get Text    ${{SUCCESS_MESSAGE_SELECTOR}}\n\n"
        
        # Generic test for any website
        test_cases += "Verify Page Title\n"
        test_cases += "    ${title}=    Get Title\n"
        test_cases += "    Log    Page title: ${title}\n\n"
        
        test_cases += "Take Screenshot of Homepage\n"
        test_cases += "    Take Screenshot\n"
        
        return test_cases


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate Robot Framework web tests")
    parser.add_argument("--url", type=str, help="URL of the website to test", default="https://www.saucedemo.com/")
    parser.add_argument("--output", type=str, help="Path to save the generated Robot Framework tests")
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    
    url = args.url
    
    # Determine output file path
    if args.output:
        output_file = args.output
    else:
        # Extract domain for the filename
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace(".", "_")
        output_file = os.path.join(ROBOT_DIR, f"{domain}_web_tests.robot")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Create generator and generate tests
    generator = RobotWebGenerator(url)
    success = generator.generate_robot_suite(output_file)
    
    if success:
        logger.info(f"Successfully generated Robot Framework web tests: {output_file}")
    else:
        logger.error("Failed to generate Robot Framework web tests")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())