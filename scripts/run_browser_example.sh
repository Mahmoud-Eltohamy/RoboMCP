#!/bin/bash

# Run the web browser automation example
echo "Running web browser automation example..."
python examples/web_browser_example.py

# Check if the command succeeded
if [ $? -eq 0 ]; then
    echo "Web browser example completed successfully."
else
    echo "Web browser example failed."
    exit 1
fi
