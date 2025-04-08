"""
Robot Framework Test Generator
=============================

This script provides a unified interface to generate Robot Framework test scripts
for both web applications and mobile apps. It supports:

1. Generating tests for websites using Browser Library
2. Generating tests for mobile apps using AppiumLibrary

Example usage:
    # Generate web tests
    python generate_robot_tests.py --type web --url https://www.saucedemo.com/ --output ../data/generated_tests/saucedemo_tests.robot
    
    # Generate mobile tests
    python generate_robot_tests.py --type mobile --app ../app_tests/sauce_labs_demo/sauce_labs_demo.apk --output ../data/generated_tests/swaglabs_tests.robot
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Import the web and mobile generators
from robot_web_generator import RobotWebGenerator
from robot_mobile_generator import RobotMobileGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("generate_robot_tests")

# Path to store generated tests
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ROBOT_DIR = os.path.join(DATA_DIR, "generated_tests")

# Create directories if they don't exist
os.makedirs(ROBOT_DIR, exist_ok=True)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Robot Framework test scripts for web and mobile applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate web tests for Sauce Demo website
  python generate_robot_tests.py --type web --url https://www.saucedemo.com/
  
  # Generate mobile tests for SwagLabs app
  python generate_robot_tests.py --type mobile --app ../app_tests/sauce_labs_demo/sauce_labs_demo.apk
"""
    )
    
    parser.add_argument("--type", type=str, choices=["web", "mobile"], required=True,
                      help="Type of tests to generate: 'web' or 'mobile'")
    
    # Web-specific arguments
    parser.add_argument("--url", type=str, 
                      help="URL of the website to test (required for type='web')")
    
    # Mobile-specific arguments
    parser.add_argument("--app", type=str, 
                      help="Path to the mobile app APK to test (required for type='mobile')")
    
    # Common arguments
    parser.add_argument("--output", type=str,
                      help="Path to save the generated Robot Framework tests")
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    
    # Validate arguments based on the selected type
    if args.type == "web" and not args.url:
        logger.error("The --url argument is required for web tests")
        return 1
    
    if args.type == "mobile" and not args.app:
        logger.error("The --app argument is required for mobile tests")
        return 1
    
    # Generate tests based on the selected type
    if args.type == "web":
        # Determine output file path for web tests
        if args.output:
            output_file = args.output
        else:
            from urllib.parse import urlparse
            domain = urlparse(args.url).netloc.replace(".", "_")
            output_file = os.path.join(ROBOT_DIR, f"{domain}_web_tests.robot")
        
        # Generate web tests
        generator = RobotWebGenerator(args.url)
        success = generator.generate_robot_suite(output_file)
        
        if success:
            logger.info(f"Successfully generated Robot Framework web tests: {output_file}")
        else:
            logger.error("Failed to generate Robot Framework web tests")
            return 1
    
    elif args.type == "mobile":
        # Ensure the APK file exists
        if not os.path.exists(args.app):
            logger.error(f"APK file not found: {args.app}")
            return 1
        
        # Determine output file path for mobile tests
        if args.output:
            output_file = args.output
        else:
            app_name = os.path.splitext(os.path.basename(args.app))[0]
            output_file = os.path.join(ROBOT_DIR, f"{app_name}_mobile_tests.robot")
        
        # Generate mobile tests
        generator = RobotMobileGenerator(args.app)
        success = generator.generate_robot_suite(output_file)
        
        if success:
            logger.info(f"Successfully generated Robot Framework mobile tests: {output_file}")
        else:
            logger.error("Failed to generate Robot Framework mobile tests")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())