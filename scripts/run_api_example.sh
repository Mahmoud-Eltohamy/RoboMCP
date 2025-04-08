#!/bin/bash

# Script to run the API Testing Example

# Set the current directory to the script's directory
cd "$(dirname "$0")"
# Move up to the project root
cd ..

# Run the example
python examples/api_testing_example.py

# Exit with the same status as the example
exit $?
