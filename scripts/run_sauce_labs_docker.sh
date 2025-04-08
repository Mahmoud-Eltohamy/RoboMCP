#!/bin/bash

# This script runs the Sauce Labs Demo App example in Docker environment
echo "Running Sauce Labs Demo App example in Docker..."

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set."
    echo "Please set your OpenAI API key before running this example."
    exit 1
fi

# Check if Docker containers are running
if ! docker ps | grep -q mcp-appium; then
    echo "Docker containers are not running. Starting them now..."
    ./docker-run.sh --up --detached
    
    # Give some time for containers to start up
    echo "Waiting for containers to start..."
    sleep 15
fi

# Copy the Sauce Labs Demo APK to the docker container if it's not already there
echo "Ensuring Sauce Labs Demo App APK is available in the container..."
docker exec -it mcp-appium mkdir -p /app/app_tests/sauce_labs_demo
docker cp app_tests/sauce_labs_demo/sauce_labs_demo.apk mcp-appium:/app/app_tests/sauce_labs_demo/

# Run the example
echo "Starting Sauce Labs Demo App Test..."
docker exec -it mcp-appium python examples/docker_sauce_labs_example.py --provider openai

# Show where to find the logs
echo "Testing complete. You can view Docker logs with:"
echo "docker logs mcp-appium"