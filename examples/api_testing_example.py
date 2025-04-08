"""
API Testing Example
==================

This example demonstrates how to use the MCP Appium API testing capabilities:
1. Loading an OpenAPI specification (JSON or YAML)
2. Extracting API information
3. Making API requests
4. Validating responses
5. Generating Robot Framework tests
"""

import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add the parent directory to the path to allow importing mcp_appium
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_appium.api import APIClient, OpenAPIParser, RobotGenerator, APITestRunner

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api_testing_example")

# Path to store downloaded specs and generated tests
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SPEC_DIR = os.path.join(DATA_DIR, "api_specs")
ROBOT_DIR = os.path.join(DATA_DIR, "generated_tests")

# Create directories if they don't exist
os.makedirs(SPEC_DIR, exist_ok=True)
os.makedirs(ROBOT_DIR, exist_ok=True)

# Default API spec (PetStore as an example)
PETSTORE_SPEC_URL = "https://petstore.swagger.io/v2/swagger.json"
LOCAL_SPEC_PATH = os.path.join(SPEC_DIR, "petstore_spec.json")


def get_spec_path(input_path=None):
    """
    Get the path to the API specification file.
    If input_path is provided, use it. Otherwise, download the PetStore spec.
    
    Args:
        input_path: Optional path to a local specification file (JSON or YAML)
        
    Returns:
        str: Path to the API specification file
    """
    if input_path:
        # Use the provided local file
        if os.path.exists(input_path):
            logger.info(f"Using provided spec from {input_path}")
            return input_path
        else:
            logger.error(f"Provided spec file not found: {input_path}")
            return None
    
    # No input path provided, use the default PetStore spec
    return download_spec()


def download_spec():
    """Download the PetStore API spec and cache it locally."""
    import requests

    try:
        # Check if the spec already exists locally
        if os.path.exists(LOCAL_SPEC_PATH):
            logger.info(f"Using cached spec from {LOCAL_SPEC_PATH}")
            return LOCAL_SPEC_PATH

        # Download the spec
        logger.info(f"Downloading spec from {PETSTORE_SPEC_URL}")
        response = requests.get(PETSTORE_SPEC_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the spec locally
        with open(LOCAL_SPEC_PATH, 'w') as f:
            f.write(response.text)

        logger.info(f"Saved spec to {LOCAL_SPEC_PATH}")
        return LOCAL_SPEC_PATH

    except Exception as e:
        logger.error(f"Error downloading spec: {e}")
        # If downloading fails but a local copy exists, use that
        if os.path.exists(LOCAL_SPEC_PATH):
            logger.info(f"Using cached spec from {LOCAL_SPEC_PATH}")
            return LOCAL_SPEC_PATH
        return None


def explore_api_spec(spec_path):
    """Explore the API specification."""
    # Create an OpenAPI parser
    parser = OpenAPIParser()
    
    # Load the spec
    if not parser.load_spec(spec_path):
        logger.error("Failed to load API specification")
        return
    
    # Get API info
    info = parser.info
    logger.info(f"API Info: {info.get('title', 'Unknown')} - {info.get('version', 'Unknown')}")
    logger.info(f"Description: {info.get('description', 'No description')}")
    
    # Get available endpoints
    endpoints = parser.get_endpoints()
    logger.info(f"Available endpoints: {len(endpoints)}")
    
    # Print the first 5 endpoints
    for i, (path, methods) in enumerate(endpoints.items()):
        if i >= 5:
            break
        logger.info(f"Endpoint: {path}")
        for method, operation in methods.items():
            logger.info(f"  Method: {method.upper()}")
            logger.info(f"  Operation ID: {operation.get('operationId', 'Unknown')}")
            logger.info(f"  Summary: {operation.get('summary', 'No summary')}")
    
    # Get available servers
    servers = parser.servers
    if servers:
        logger.info(f"Servers: {len(servers)}")
        for server in servers:
            logger.info(f"  URL: {server.get('url', 'Unknown')}")
    else:
        logger.info("No servers defined in the specification")


def make_api_requests(spec_path):
    """Make API requests to the PetStore API."""
    # Create an API client
    client = APIClient()
    
    # Load the spec
    if not client.load_specification(spec_path):
        logger.error("Failed to load API specification")
        return
    
    # Create a session
    session = client.create_session("example-session")
    
    # Make GET request to /pet/findByStatus?status=available
    logger.info("Making GET request to /v2/pet/findByStatus?status=available")
    status_code, response_data, response_headers = client.execute_request(
        "/v2/pet/findByStatus",
        "GET",
        params={"status": "available"},
        session_id="example-session"
    )
    
    # Log response details
    logger.info(f"Status Code: {status_code}")
    logger.info(f"Response Headers: {json.dumps(dict(response_headers), indent=2)}")
    
    # Check for successful response
    if status_code >= 200 and status_code < 300:
        # Get the number of available pets
        available_pets = response_data
        pet_count = len(available_pets)
        logger.info(f"Available Pets: {pet_count}")
        
        # Print details of the first pet if available
        if pet_count > 0:
            pet = available_pets[0]
            logger.info(f"First Pet: ID = {pet.get('id')}, Name = {pet.get('name')}, Status = {pet.get('status')}")
    else:
        logger.error(f"Error response: {response_data.get('error', 'Unknown error')}")
    
    # Create a new pet
    logger.info("\nCreating a new pet")
    pet_data = {
        "id": 12345,
        "name": "MCP Test Pet",
        "category": {
            "id": 1,
            "name": "Dogs"
        },
        "photoUrls": [
            "http://example.com/dog.jpg"
        ],
        "tags": [
            {
                "id": 1,
                "name": "friendly"
            }
        ],
        "status": "available"
    }
    
    create_status_code, create_response_data, create_response_headers = client.execute_request(
        "/v2/pet",
        "POST",
        data=pet_data,
        session_id="example-session"
    )
    
    # Log response details
    logger.info(f"Create Pet Status Code: {create_status_code}")
    
    # Check for successful response
    if create_status_code >= 200 and create_status_code < 300:
        logger.info(f"Created Pet: ID = {create_response_data.get('id')}, Name = {create_response_data.get('name')}")
        
        # Now try to retrieve the pet we just created
        pet_id = create_response_data.get('id')
        logger.info(f"\nRetrieving pet with ID: {pet_id}")
        
        get_status_code, get_response_data, get_response_headers = client.execute_request(
            f"/v2/pet/{pet_id}",
            "GET",
            session_id="example-session"
        )
        
        if get_status_code >= 200 and get_status_code < 300:
            logger.info(f"Retrieved Pet: ID = {get_response_data.get('id')}, Name = {get_response_data.get('name')}")
        else:
            logger.error(f"Error retrieving pet: {get_response_data.get('error', 'Unknown error')}")
    else:
        logger.error(f"Error creating pet: {create_response_data.get('error', 'Unknown error')}")
    
    # Close the session
    client.close_session("example-session")


def generate_robot_tests(spec_path, output_path=None):
    """
    Generate Robot Framework tests from an API specification.
    
    Args:
        spec_path: Path to the API specification file (JSON or YAML)
        output_path: Optional path to save the generated Robot Framework tests
        
    Returns:
        str: Path to the generated Robot Framework tests, or None if generation failed
    """
    # Create an API client
    client = APIClient()
    
    # Load the spec
    if not client.load_specification(spec_path):
        logger.error("Failed to load API specification")
        return False
    
    # Determine output file path
    if not output_path:
        # Default output path based on spec file name
        spec_filename = os.path.basename(spec_path)
        base_name = os.path.splitext(spec_filename)[0]
        output_file = os.path.join(ROBOT_DIR, f"{base_name}_api_tests.robot")
    else:
        output_file = output_path
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Generate Robot Framework tests
    success = client.generate_robot_tests(output_file)
    
    if success:
        logger.info(f"Generated Robot Framework tests: {output_file}")
        return output_file
    else:
        logger.error("Failed to generate Robot Framework tests")
        return None


def run_robot_tests(robot_file):
    """Run Robot Framework tests for the PetStore API."""
    if not robot_file or not os.path.exists(robot_file):
        logger.error(f"Robot file not found: {robot_file}")
        return
    
    # Create a test runner
    runner = APITestRunner()
    
    # Create a results directory
    results_dir = os.path.join(DATA_DIR, "robot_results")
    os.makedirs(results_dir, exist_ok=True)
    runner.set_results_directory(results_dir)
    
    # Note: In a real environment, you would run the tests here
    # Since Robot Framework requires additional dependencies, we'll
    # just show the command that would be used
    
    robot_command = f"robot --outputdir {results_dir} {robot_file}"
    logger.info(f"Robot test command: {robot_command}")
    logger.info("Note: To run the tests, you need to install Robot Framework and robotframework-requests")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="API Testing Example")
    parser.add_argument("--spec-file", type=str, help="Path to a local API specification file (JSON or YAML)")
    parser.add_argument("--download-only", action="store_true", help="Only download the API spec")
    parser.add_argument("--explore-only", action="store_true", help="Only explore the API spec")
    parser.add_argument("--make-requests-only", action="store_true", help="Only make API requests")
    parser.add_argument("--generate-only", action="store_true", help="Only generate Robot Framework tests")
    parser.add_argument("--run-only", action="store_true", help="Only run Robot Framework tests")
    parser.add_argument("--output", type=str, help="Path to save the generated Robot Framework tests (default: data/generated_tests/api_tests.robot)")
    
    args = parser.parse_args()
    
    # Get the API spec path
    spec_path = get_spec_path(args.spec_file)
    if not spec_path:
        logger.error("Failed to find or download API specification")
        return 1
    
    if args.download_only:
        return 0
    
    # Explore the API spec
    if args.explore_only:
        explore_api_spec(spec_path)
        return 0
    
    # Make API requests
    if args.make_requests_only:
        make_api_requests(spec_path)
        return 0
    
    # Generate Robot Framework tests
    if args.generate_only:
        generate_robot_tests(spec_path, args.output)
        return 0
    
    # Run Robot Framework tests
    if args.run_only:
        # If a specific output file was provided, use it; otherwise use the default
        if args.output and os.path.exists(args.output):
            robot_file = args.output
        else:
            # Try to find a robot file based on the spec name
            spec_filename = os.path.basename(spec_path)
            base_name = os.path.splitext(spec_filename)[0]
            robot_file = os.path.join(ROBOT_DIR, f"{base_name}_api_tests.robot")
            
            # If it doesn't exist, fall back to the old name
            if not os.path.exists(robot_file):
                robot_file = os.path.join(ROBOT_DIR, "petstore_api_tests.robot")
        
        if os.path.exists(robot_file):
            run_robot_tests(robot_file)
        else:
            robot_file = generate_robot_tests(spec_path, args.output)
            if robot_file:
                run_robot_tests(robot_file)
        return 0
    
    # If no specific action is specified, run the full example
    logger.info("Running full API testing example")
    
    # Step 1: Explore the API spec
    logger.info("\n=== Step 1: Explore the API Specification ===")
    explore_api_spec(spec_path)
    
    # Step 2: Make API requests
    logger.info("\n=== Step 2: Make API Requests ===")
    make_api_requests(spec_path)
    
    # Step 3: Generate Robot Framework tests
    logger.info("\n=== Step 3: Generate Robot Framework Tests ===")
    robot_file = generate_robot_tests(spec_path, args.output)
    
    # Step 4: Run Robot Framework tests
    logger.info("\n=== Step 4: Run Robot Framework Tests ===")
    if robot_file:
        run_robot_tests(robot_file)
    
    logger.info("API testing example completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())