#!/bin/bash

# This script runs the Sauce Labs Demo App example
echo "Running Sauce Labs Demo App example..."

# Set environment variables for the example
export APPIUM_URL="http://localhost:4723"
export ANDROID_APP_PATH="$(pwd)/app_tests/sauce_labs_demo/sauce_labs_demo.apk"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set."
    echo "Please set your OpenAI API key before running this example."
    exit 1
fi

# Run the example
python examples/sauce_labs_demo_example.py --url "$APPIUM_URL" --app "$ANDROID_APP_PATH" --provider openai