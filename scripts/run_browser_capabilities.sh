#!/bin/bash

# Run the browser capabilities example
echo "Running browser capabilities example..."
python examples/browser_capabilities_example.py

# Check if the command succeeded
if [ $? -eq 0 ]; then
    echo "Browser capabilities example completed successfully."
else
    echo "Browser capabilities example failed."
    exit 1
fi
