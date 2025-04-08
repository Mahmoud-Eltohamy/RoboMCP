"""
API Test Runner Module
====================

This module provides functionality for running Robot Framework tests
generated from OpenAPI specifications.
"""

import os
import logging
import tempfile
import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .openapi_parser import OpenAPIParser
from .robot_generator import RobotGenerator

try:
    import robot
    from robot.api import TestSuite
    HAS_ROBOT = True
except ImportError:
    HAS_ROBOT = False

logger = logging.getLogger(__name__)


class APITestRunner:
    """
    Runner for API tests generated from OpenAPI specifications.
    
    This class is responsible for:
    1. Running Robot Framework tests
    2. Processing test results
    3. Generating test reports
    """
    
    def __init__(self, parser: Optional[OpenAPIParser] = None):
        """
        Initialize the API test runner.
        
        Args:
            parser: An OpenAPIParser instance (optional)
        """
        self.parser = parser
        self.results_dir = os.path.join(tempfile.gettempdir(), "mcp-api-tests")
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
    
    def set_parser(self, parser: OpenAPIParser) -> None:
        """
        Set the OpenAPI parser.
        
        Args:
            parser: An OpenAPIParser instance
        """
        self.parser = parser
    
    def set_results_directory(self, results_dir: str) -> None:
        """
        Set the directory for test results.
        
        Args:
            results_dir: Path to the results directory
        """
        self.results_dir = results_dir
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run_single_test(self, path: str, method: str) -> Dict[str, Any]:
        """
        Run a single test for a specific endpoint.
        
        Args:
            path: The endpoint path
            method: The HTTP method
            
        Returns:
            Dict: Test results
        """
        if not self.parser:
            return {"error": "No OpenAPI parser set"}
        
        if not HAS_ROBOT:
            return {"error": "Robot Framework not installed"}
        
        # Find the endpoint in the API specification
        endpoints = self.parser.get_endpoints()
        
        if path not in endpoints:
            return {"error": f"Endpoint not found: {path}"}
        
        method = method.lower()
        if method not in endpoints[path]:
            return {"error": f"Method not found: {method.upper()} {path}"}
        
        # Get operation details
        operation = endpoints[path][method]
        operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
        
        # Generate a temporary test suite for this endpoint
        test_file = os.path.join(self.results_dir, f"test_{operation_id}.robot")
        
        # Create a Robot Generator to generate the test
        generator = RobotGenerator(self.parser)
        if not generator.generate_robot_suite(test_file):
            return {"error": f"Failed to generate test suite for {method.upper()} {path}"}
        
        # Run the test and get results
        return self._run_robot_test(test_file, operation_id)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run tests for all endpoints.
        
        Returns:
            Dict: Test results
        """
        if not self.parser:
            return {"error": "No OpenAPI parser set"}
        
        if not HAS_ROBOT:
            return {"error": "Robot Framework not installed"}
        
        # Generate a test suite for all endpoints
        test_file = os.path.join(self.results_dir, "all_tests.robot")
        
        # Create a Robot Generator to generate the tests
        generator = RobotGenerator(self.parser)
        if not generator.generate_robot_suite(test_file):
            return {"error": "Failed to generate test suite"}
        
        # Run the tests and get results
        return self._run_robot_test(test_file)
    
    def _run_robot_test(self, test_file: str, test_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a Robot Framework test.
        
        Args:
            test_file: Path to the test file
            test_name: Name of the test to run (optional, runs all tests if not specified)
            
        Returns:
            Dict: Test results
        """
        if not os.path.exists(test_file):
            return {"error": f"Test file not found: {test_file}"}
        
        # Prepare output files
        output_dir = os.path.join(self.results_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        output_xml = os.path.join(output_dir, "output.xml")
        log_html = os.path.join(output_dir, "log.html")
        report_html = os.path.join(output_dir, "report.html")
        
        try:
            # If we have the Python Robot module, use it directly
            if HAS_ROBOT:
                # Build command-line arguments
                robot_args = [
                    test_file,
                    "--outputdir", output_dir
                ]
                
                # Add test name if specified
                if test_name:
                    robot_args.extend(["--name", test_name])
                
                # Run Robot Framework programmatically
                robot.run_cli(robot_args)
                
                # Parse test results
                return self._parse_robot_results(output_xml)
                
            else:
                # Otherwise, use subprocess to call robot command
                cmd = ["robot", "--outputdir", output_dir]
                
                # Add test name if specified
                if test_name:
                    cmd.extend(["--name", test_name])
                
                cmd.append(test_file)
                
                # Run Robot Framework as a subprocess
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode != 0:
                    error_message = result.stderr.strip() or "Unknown error running Robot Framework"
                    return {"error": error_message}
                
                # Parse test results
                return self._parse_robot_results(output_xml)
                
        except Exception as e:
            logger.error(f"Error running test: {str(e)}")
            return {"error": str(e)}
    
    def _parse_robot_results(self, output_xml: str) -> Dict[str, Any]:
        """
        Parse Robot Framework results from XML.
        
        Args:
            output_xml: Path to the output XML file
            
        Returns:
            Dict: Test results
        """
        if not os.path.exists(output_xml):
            return {"error": f"Output file not found: {output_xml}"}
        
        try:
            # If we have the Robot module, use its result parser
            if HAS_ROBOT:
                result = robot.api.ExecutionResult(output_xml)
                stats = result.statistics
                
                # Get test counts
                total = stats.total.critical.total
                passed = stats.total.critical.passed
                failed = total - passed
                
                # Get test details
                tests = []
                for suite in result.suite.suites:
                    for test in suite.tests:
                        test_info = {
                            "name": test.name,
                            "status": test.status,
                            "message": test.message,
                            "tags": list(test.tags)
                        }
                        tests.append(test_info)
                
                return {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "tests": tests
                }
            
            else:
                # Otherwise, parse the XML manually
                tree = ET.parse(output_xml)
                root = tree.getroot()
                
                # Get statistics
                statistics = root.find("statistics")
                if statistics is None:
                    return {"error": "No statistics found in output XML"}
                
                total_elem = statistics.find(".//stat[@name='Critical Tests']")
                if total_elem is None:
                    total_elem = statistics.find(".//stat[@name='All Tests']")
                    
                total = int(total_elem.get("total", "0")) if total_elem is not None else 0
                passed = int(total_elem.get("pass", "0")) if total_elem is not None else 0
                failed = int(total_elem.get("fail", "0")) if total_elem is not None else 0
                
                # Get test details
                tests = []
                for test_elem in root.findall(".//test"):
                    status_elem = test_elem.find("status")
                    status = status_elem.get("status") if status_elem is not None else "UNKNOWN"
                    message = status_elem.text if status_elem is not None else ""
                    
                    tags = []
                    tags_elem = test_elem.find("tags")
                    if tags_elem is not None:
                        for tag_elem in tags_elem.findall("tag"):
                            tags.append(tag_elem.text)
                    
                    test_info = {
                        "name": test_elem.get("name", "Unknown"),
                        "status": status,
                        "message": message,
                        "tags": tags
                    }
                    tests.append(test_info)
                
                return {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "tests": tests
                }
                
        except Exception as e:
            logger.error(f"Error parsing results: {str(e)}")
            return {"error": f"Failed to parse results: {str(e)}"}
    
    def generate_html_report(self, results: Dict[str, Any], output_file: str) -> bool:
        """
        Generate an HTML report from test results.
        
        Args:
            results: Test results
            output_file: Path to save the HTML report
            
        Returns:
            bool: True if generation was successful, False otherwise
        """
        try:
            # Create a simple HTML report
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>API Test Results</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    .summary { margin: 20px 0; padding: 10px; background-color: #f5f5f5; }
                    .test { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
                    .PASS { color: green; }
                    .FAIL { color: red; }
                </style>
            </head>
            <body>
                <h1>API Test Results</h1>
                <div class="summary">
                    <p>Total tests: {total}</p>
                    <p>Passed: {passed}</p>
                    <p>Failed: {failed}</p>
                </div>
                <h2>Test Details</h2>
                {test_details}
            </body>
            </html>
            """
            
            # Fill in test details
            test_details = ""
            for test in results.get("tests", []):
                test_details += f"""
                <div class="test">
                    <h3>{test.get('name', 'Unknown')}</h3>
                    <p class="{test.get('status', 'UNKNOWN')}">Status: {test.get('status', 'UNKNOWN')}</p>
                    <p>Message: {test.get('message', '')}</p>
                    <p>Tags: {', '.join(test.get('tags', []))}</p>
                </div>
                """
            
            # Fill in the template
            html = html.format(
                total=results.get("total", 0),
                passed=results.get("passed", 0),
                failed=results.get("failed", 0),
                test_details=test_details
            )
            
            # Write to file
            with open(output_file, 'w') as f:
                f.write(html)
            
            logger.info(f"Generated HTML report: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return False