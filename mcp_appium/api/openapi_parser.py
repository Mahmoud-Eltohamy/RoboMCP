"""
OpenAPI Parser Module
===================

This module provides functionality for parsing and processing OpenAPI/Swagger
specifications.
"""

import os
import json
import re
import logging
import urllib.parse
from typing import Dict, List, Any, Optional, Tuple, Union

import requests
import jsonschema

logger = logging.getLogger(__name__)


class OpenAPIParser:
    """
    Parser for OpenAPI/Swagger specifications.
    
    This class is responsible for:
    1. Loading and parsing OpenAPI/Swagger specifications
    2. Extracting API endpoints, parameters, and schemas
    3. Validating requests and responses against the specification
    4. Providing information about API operations
    """
    
    def __init__(self):
        """Initialize the OpenAPI parser."""
        self.spec_data: Dict[str, Any] = {}
        self.paths: Dict[str, Any] = {}
        self.components: Dict[str, Any] = {}
        self.info: Dict[str, Any] = {}
        self.servers: List[Dict[str, Any]] = []
    
    def load_spec(self, spec_path: str) -> bool:
        """
        Load an OpenAPI specification.
        
        Args:
            spec_path: Path to the OpenAPI specification file or URL
            
        Returns:
            bool: True if the specification was loaded successfully, False otherwise
        """
        try:
            # Check if spec_path is a URL
            parsed_url = urllib.parse.urlparse(spec_path)
            is_url = bool(parsed_url.scheme and parsed_url.netloc)
            
            if is_url:
                # Load from URL
                response = requests.get(spec_path)
                response.raise_for_status()
                
                if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                    try:
                        import yaml
                        self.spec_data = yaml.safe_load(response.text)
                    except ImportError:
                        logger.error("YAML support requires PyYAML. Please install it with 'pip install pyyaml'.")
                        return False
                else:
                    self.spec_data = response.json()
            else:
                # Load from file
                if not os.path.exists(spec_path):
                    logger.error(f"Specification file not found: {spec_path}")
                    return False
                
                if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                    try:
                        import yaml
                        with open(spec_path, 'r') as file:
                            self.spec_data = yaml.safe_load(file)
                    except ImportError:
                        logger.error("YAML support requires PyYAML. Please install it with 'pip install pyyaml'.")
                        return False
                else:
                    with open(spec_path, 'r') as file:
                        self.spec_data = json.load(file)
            
            # Extract key components
            self.paths = self.spec_data.get('paths', {})
            self.components = self.spec_data.get('components', {})
            self.info = self.spec_data.get('info', {})
            self.servers = self.spec_data.get('servers', [])
            
            logger.info(f"Loaded OpenAPI specification: {self.info.get('title', 'Unknown API')}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading specification: {str(e)}")
            return False
    
    def get_base_url(self) -> str:
        """
        Get the base URL from the servers list.
        
        Returns:
            str: The base URL, or an empty string if not found
        """
        if self.servers:
            # Return the first server URL
            return self.servers[0].get('url', "")
        
        # Handle Swagger Petstore API specially (it often doesn't have servers defined)
        if self.info and self.info.get('title') == 'Swagger Petstore':
            # Check for Swagger 2.0 format (host and schemes)
            if 'host' in self.spec_data:
                host = self.spec_data.get('host', '')
                schemes = self.spec_data.get('schemes', ['https'])
                basePath = self.spec_data.get('basePath', '')
                if host:
                    return f"{schemes[0]}://{host}{basePath}"
            
            # Default for Swagger Petstore
            return "https://petstore.swagger.io/v2"
            
        # Try to use host and basePath for Swagger 2.0
        if 'host' in self.spec_data:
            host = self.spec_data.get('host', '')
            schemes = self.spec_data.get('schemes', ['https'])
            basePath = self.spec_data.get('basePath', '')
            if host:
                return f"{schemes[0]}://{host}{basePath}"
                
        # No server or host found
        return ""
    
    def get_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all API endpoints.
        
        Returns:
            Dict: A dictionary of paths and their operations
        """
        return self.paths
    
    def get_operation_parameters(self, path: str, method: str) -> List[Dict[str, Any]]:
        """
        Get parameters for an API operation.
        
        Args:
            path: The endpoint path
            method: The HTTP method
            
        Returns:
            List: A list of parameter objects
        """
        method = method.lower()
        
        # Check if path exists
        if path not in self.paths:
            return []
        
        # Check if method exists
        if method not in self.paths[path]:
            return []
        
        # Get operation parameters
        operation = self.paths[path][method]
        parameters = operation.get('parameters', [])
        
        # Resolve references
        resolved_parameters = []
        for param in parameters:
            if '$ref' in param:
                resolved_param = self._resolve_reference(param['$ref'])
                if resolved_param:
                    resolved_parameters.append(resolved_param)
            else:
                resolved_parameters.append(param)
        
        return resolved_parameters
    
    def get_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """
        Get parameters for a path.
        
        Args:
            path: The endpoint path
            
        Returns:
            List: A list of parameter objects
        """
        # Check if path exists
        if path not in self.paths:
            return []
        
        # Get path parameters
        parameters = self.paths[path].get('parameters', [])
        
        # Resolve references
        resolved_parameters = []
        for param in parameters:
            if '$ref' in param:
                resolved_param = self._resolve_reference(param['$ref'])
                if resolved_param:
                    resolved_parameters.append(resolved_param)
            else:
                resolved_parameters.append(param)
        
        return resolved_parameters
    
    def extract_path_parameters(self, path: str) -> List[str]:
        """
        Extract path parameter names from a path.
        
        Args:
            path: The endpoint path
            
        Returns:
            List: A list of parameter names
        """
        # Extract {param} patterns from the path
        return re.findall(r'{([^}]+)}', path)
    
    def extract_example_request(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """
        Extract an example request body for an operation.
        
        Args:
            path: The endpoint path
            method: The HTTP method
            
        Returns:
            Dict: An example request body, or None if not found
        """
        method = method.lower()
        
        # Check if path exists
        if path not in self.paths:
            return None
        
        # Check if method exists
        if method not in self.paths[path]:
            return None
        
        # Get operation requestBody
        operation = self.paths[path][method]
        request_body = operation.get('requestBody', {})
        
        # Resolve reference if needed
        if '$ref' in request_body:
            request_body = self._resolve_reference(request_body['$ref'])
        
        # Get content
        content = request_body.get('content', {})
        
        # Try to find a JSON example
        for content_type, media_type in content.items():
            if 'application/json' in content_type:
                # Check for example
                if 'example' in media_type:
                    return media_type['example']
                
                # Check for examples
                examples = media_type.get('examples', {})
                if examples:
                    # Return the first example
                    for example_name, example in examples.items():
                        if 'value' in example:
                            return example['value']
                        if '$ref' in example:
                            example_ref = self._resolve_reference(example['$ref'])
                            if example_ref and 'value' in example_ref:
                                return example_ref['value']
                
                # Try to generate an example from schema
                schema = media_type.get('schema', {})
                if schema:
                    return self._generate_example_from_schema(schema)
        
        return None
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an example from a schema.
        
        Args:
            schema: The schema
            
        Returns:
            Dict: An example object
        """
        # Resolve reference if needed
        if '$ref' in schema:
            schema = self._resolve_reference(schema['$ref'])
        
        example = {}
        
        # Handle different schema types
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            
            for prop_name, prop_schema in properties.items():
                # Use example if available
                if 'example' in prop_schema:
                    example[prop_name] = prop_schema['example']
                    continue
                
                # Generate based on type
                prop_type = prop_schema.get('type', 'string')
                
                if prop_type == 'string':
                    example[prop_name] = f"example_{prop_name}"
                elif prop_type == 'integer' or prop_type == 'number':
                    example[prop_name] = 0
                elif prop_type == 'boolean':
                    example[prop_name] = False
                elif prop_type == 'array':
                    # Get items schema
                    items_schema = prop_schema.get('items', {})
                    item_example = self._generate_example_from_schema(items_schema)
                    example[prop_name] = [item_example]
                elif prop_type == 'object':
                    example[prop_name] = self._generate_example_from_schema(prop_schema)
        
        return example
    
    def _resolve_reference(self, ref: str) -> Optional[Dict[str, Any]]:
        """
        Resolve a reference.
        
        Args:
            ref: The reference string
            
        Returns:
            Dict: The resolved object, or None if not found
        """
        # Check if ref is a valid reference
        if not ref.startswith('#/'):
            return None
        
        # Split the reference path
        parts = ref[2:].split('/')
        
        # Traverse the specification
        current = self.spec_data
        for part in parts:
            if part not in current:
                return None
            current = current[part]
        
        return current
    
    def get_response_schema(self, path: str, method: str, status_code: str) -> Optional[Dict[str, Any]]:
        """
        Get the response schema for a status code.
        
        Args:
            path: The endpoint path
            method: The HTTP method
            status_code: The response status code
            
        Returns:
            Dict: The response schema, or None if not found
        """
        method = method.lower()
        
        # Check if path exists
        if path not in self.paths:
            return None
        
        # Check if method exists
        if method not in self.paths[path]:
            return None
        
        # Get operation responses
        operation = self.paths[path][method]
        responses = operation.get('responses', {})
        
        # Check if status code exists
        if status_code not in responses:
            # Try default response
            if 'default' in responses:
                response = responses['default']
            else:
                return None
        else:
            response = responses[status_code]
        
        # Resolve reference if needed
        if '$ref' in response:
            response = self._resolve_reference(response['$ref'])
        
        # Get content
        content = response.get('content', {})
        
        # Try to find a JSON schema
        for content_type, media_type in content.items():
            if 'application/json' in content_type:
                # Return schema
                return media_type.get('schema', None)
        
        return None
    
    def get_api_summary(self) -> List[Dict[str, str]]:
        """
        Get a summary of the API endpoints.
        
        Returns:
            List: A list of endpoint summaries
        """
        summary = []
        
        for path, methods in self.paths.items():
            for method, operation in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'operationId': operation.get('operationId', '')
                    }
                    summary.append(endpoint)
        
        return summary
    
    def validate_response(self, path: str, method: str, status_code: int, response_data: Dict[str, Any]) -> bool:
        """
        Validate a response against the schema.
        
        Args:
            path: The endpoint path
            method: The HTTP method
            status_code: The response status code
            response_data: The response data
            
        Returns:
            bool: True if the response is valid, False otherwise
        """
        # Convert status code to string
        status_code_str = str(status_code)
        
        # Get response schema
        schema = self.get_response_schema(path, method, status_code_str)
        
        if not schema:
            logger.warning(f"No schema found for {method.upper()} {path} with status code {status_code}")
            return True
        
        try:
            # Resolve schema references
            resolved_schema = self._resolve_schema_references(schema)
            
            # Validate response against schema
            jsonschema.validate(response_data, resolved_schema)
            return True
            
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Response validation failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error validating response: {str(e)}")
            return False
    
    def _resolve_schema_references(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively resolve references in a schema.
        
        Args:
            schema: The schema
            
        Returns:
            Dict: The resolved schema
        """
        if not schema:
            return {}
        
        # Make a copy of the schema
        resolved = schema.copy()
        
        # Check for reference
        if '$ref' in resolved:
            ref_schema = self._resolve_reference(resolved['$ref'])
            if ref_schema:
                # Merge with original schema (excluding $ref)
                ref_schema = ref_schema.copy()
                resolved.pop('$ref')
                resolved.update(ref_schema)
        
        # Recursively resolve nested properties
        if 'properties' in resolved:
            properties = resolved['properties']
            for prop_name, prop_schema in properties.items():
                properties[prop_name] = self._resolve_schema_references(prop_schema)
        
        # Recursively resolve array items
        if 'items' in resolved:
            resolved['items'] = self._resolve_schema_references(resolved['items'])
        
        # Recursively resolve allOf, anyOf, oneOf
        for key in ['allOf', 'anyOf', 'oneOf']:
            if key in resolved:
                resolved[key] = [self._resolve_schema_references(s) for s in resolved[key]]
        
        return resolved